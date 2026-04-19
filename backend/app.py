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
from utils.onprem_tco import calculate_onprem_tco
from schemas import CalcPayload

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
        return jsonify({"error": "invalid input", "details": e.errors()}), 400

    d = payload.dict()

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
                network=d["network"],
                backup=d["backup"],
                instance_count=d["instance_count"],
            )
        })
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
    })


if __name__ == "__main__":
    app.run(port=5000, debug=True)
import resend

resend.api_key = "re_HVBdgGCL_EM9kwMKXchmpKbMeupPD9rSg"

@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    try:
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
