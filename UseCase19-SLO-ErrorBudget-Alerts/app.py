from flask import Flask, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUESTS = Counter(
    "uc19_http_requests_total",
    "Total application requests",
    ["endpoint", "status"]
)

@app.route("/health")
def health():
    REQUESTS.labels(endpoint="/health", status="success").inc()
    return {"status": "healthy"}, 200

@app.route("/fail")
def fail():
    REQUESTS.labels(endpoint="/fail", status="failure").inc()
    return {"status": "failed"}, 500

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/")
def home():
    return {"message": "Use Case 19 - SLO Monitoring"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
