
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError
import logging

from cloud_providers.aws import aws_cost
from cloud_providers.azure import azure_cost
from cloud_providers.gcp import gcp_cost
from cloud_providers.kubernetes import k8s_cost
from utils.onprem_tco import calculate_onprem_tco
from utils.price_sync_scheduler import start_scheduler, stop_scheduler
from schemas import CalcPayload

app = Flask(__name__)
# For development it's convenient to allow all origins; lock this down for production
CORS(app)

logger = logging.getLogger(__name__)

# Start the periodic price sync scheduler on app startup
try:
    start_scheduler(cron_hour=2, cron_minute=0)  # Daily at 2 AM UTC
except Exception as e:
    logger.warning(f"Could not start price sync scheduler: {e}")


@app.route("/", methods=["GET"])
def health():
    return {"status": "Backend is running"}, 200


@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        payload = CalcPayload(**request.json or {})
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
            "onprem": calculate_onprem_tco(**d)
        })
    except Exception as e:
        logger.exception("Unexpected error in /calculate")
        return jsonify({"error": "internal server error"}), 500


@app.teardown_appcontext
def shutdown(exception=None):
    """Gracefully shut down the scheduler on app termination."""
    stop_scheduler()


if __name__ == "__main__":
    app.run(port=5000, debug=True)

