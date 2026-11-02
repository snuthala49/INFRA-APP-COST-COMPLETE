import json
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError
import logging

from cloud_providers.aws import aws_cost
from cloud_providers.azure import azure_cost
from cloud_providers.gcp import gcp_cost
from cloud_providers.kubernetes import k8s_cost
from cloud_providers.catalog_pricing import load_price_provenance
from cloud_providers.databases import calculate_database_quote, get_database_rate_catalog
from utils.onprem_tco import calculate_onprem_tco
from utils.database_price_sync import DATABASE_SERVICES, load_database_price_cache
from schemas import CalcPayload, DatabaseEstimatePayload

app = Flask(__name__)
CORS(app)

logger = logging.getLogger(__name__)


# ✅ Health route (root)
@app.route("/", methods=["GET"])
def health():
    return {"status": "Backend is running"}, 200


# ✅ Production health route
@app.route("/api/health", methods=["GET"])
def api_health():
    return {"service": "InfraCostIQ API", "status": "ok"}, 200


# ✅ Calculate route
@app.route("/api/calculate", methods=["POST"])
def calculate():
    try:
        payload = CalcPayload(**(request.json or {}))
    except ValidationError as e:
        logger.debug("Validation error: %s", e)
        return jsonify({"error": "invalid input", "details": e.errors(include_context=False, include_url=False)}), 400

    d = payload.model_dump()

    try:
        return jsonify({
            "aws": aws_cost(**d),
            "azure": azure_cost(**d),
            "gcp": gcp_cost(**d),
            "kubernetes": k8s_cost(**d),
            "onprem": calculate_onprem_tco(
                cpu=d["cpu"],
                ram=d["ram"],
                storage=d["storage"],
                network_ingress_gb_month=d["network_ingress_gb_month"],
                network_egress_gb_month=d["network_egress_gb_month"],
                network_cross_region_gb_month=d["network_cross_region_gb_month"],
                network_source_region=d["network_source_region"],
                network_destination_region=d["network_destination_region"],
                backup=d["backup"],
                instance_count=d["instance_count"],
            )
        })
    except ValueError as e:
        return jsonify({"error": "invalid workload or instance selection", "details": str(e)}), 422
    except Exception as e:
        logger.exception("Unexpected error in /calculate")
        return jsonify({"error": "internal server error"}), 500


# ✅ Catalog route
@app.route("/api/catalog", methods=["GET"])
def get_catalog():
    data_dir = os.path.join(os.path.dirname(__file__), "data")

    with open(os.path.join(data_dir, "aws_catalog.json"), "r") as f:
        aws = json.load(f)
    with open(os.path.join(data_dir, "azure_catalog.json"), "r") as f:
        azure = json.load(f)
    with open(os.path.join(data_dir, "gcp_catalog.json"), "r") as f:
        gcp = json.load(f)
    with open(os.path.join(data_dir, "storage_rates.json"), "r") as f:
        storage_rates = json.load(f)

    return jsonify({
        "aws": aws,
        "azure": azure,
        "gcp": gcp,
        "storage_rates": storage_rates,
        "price_provenance": load_price_provenance(),
    })


@app.route("/api/database/catalog", methods=["GET"])
def get_database_catalog():
    catalog = load_database_price_cache()
    if not catalog.get("records"):
        return jsonify({
            "error": "Database prices have not been synced",
            "providers": catalog.get("providers", {}),
        }), 503

    provider = request.args.get("provider")
    service = request.args.get("service")
    region = request.args.get("region")
    component = request.args.get("component")
    search = request.args.get("search")
    try:
        limit = int(request.args.get("limit", "250"))
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400
    if not all((provider, service, region)):
        return jsonify({
            "updated_at": catalog.get("updated_at"),
            "providers": catalog.get("providers", {}),
            "services": DATABASE_SERVICES,
        })

    try:
        return jsonify(get_database_rate_catalog(catalog, provider, service, region, component, search, limit))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/database/calculate", methods=["POST"])
def calculate_database():
    try:
        payload = DatabaseEstimatePayload(**(request.get_json(silent=True) or {}))
    except ValidationError as e:
        return jsonify({"error": "invalid input", "details": e.errors(include_context=False, include_url=False)}), 400

    try:
        return jsonify(calculate_database_quote(payload.model_dump(), load_database_price_cache()))
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        return {"error": "Contact service is not configured"}, 503

    try:
        import resend

        resend.api_key = api_key
        # 📩 Mail to YOU
        resend.Emails.send({
            "from": "srinath@infracostiq.com",
            "to": ["srinath@infracostiq.com"],
            "subject": "New Contact - InfraCostIQ",
            "text": f"""
New Contact Form Submission

Name: {name}
Email: {email}

Message:
{message}
"""
        })

        # 📩 Auto reply to USER
        resend.Emails.send({
            "from": "srinath@infracostiq.com",
            "to": [email],
            "subject": "Thanks for contacting InfraCostIQ",
            "text": f"""
Hi {name},

Thanks for reaching out to InfraCostIQ.

We have received your message and will get back to you soon.

Regards,
InfraCostIQ Team
"""
        })

        return {"status": "sent"}, 200

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
