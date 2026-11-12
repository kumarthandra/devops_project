# Use Case 19 — Define SLOs, Error Budget, and Alert Rules

## 1. Objective

Deploy a Python Flask application to Kubernetes, collect its metrics using Prometheus, define a 99% availability SLO, calculate the error budget, and trigger alerts when the error rate exceeds 1%.

## 2. Architecture

Client Requests
    |
    v
Flask Application (Port 5000)
    |
    v
Prometheus Metrics (/metrics)
    |
    v
Prometheus Server (Port 9090)
    |
    v
SLO Alert Rule (Error Rate > 1%)
    |
    v
Alertmanager (Port 9093)

## 3. Tools Used

- Python and Flask — application
- prometheus-client — application metrics
- Docker — container image
- Kubernetes — application deployment
- Helm — Prometheus installation
- Prometheus — metrics and alert evaluation
- Alertmanager — alert reception and routing

## 4. Application Files

- app.py — Flask application with /health, /fail, and /metrics endpoints
- requirements.txt — Python dependencies
- Dockerfile — container image definition
- deployment.yaml — Kubernetes Deployment
- service.yaml — Kubernetes Service
- prometheus-values.yaml — Helm configuration and alert rule
- slo-alert-rules.yaml — standalone reference alert rule

## 5. Build the Docker Image

From this project directory:

docker build -t uc19-slo-app:local .

Why: Packages the Flask application and its dependencies into a Docker image.

## 6. Create the Kubernetes Namespace

kubectl create namespace usecase19

Why: Isolates this use case from other Kubernetes workloads.

If the namespace already exists, reuse it.

## 7. Deploy the Application

kubectl apply -n usecase19 -f deployment.yaml
kubectl apply -n usecase19 -f service.yaml

Verify:

kubectl get pods -n usecase19
kubectl get svc -n usecase19

Expected: Application pod Running and service created.

## 8. Access the Application

Run in a separate terminal:

kubectl port-forward -n usecase19 svc/uc19-slo-service 5000:5000

Test in another terminal:

curl http://localhost:5000/health
curl -i http://localhost:5000/fail
curl http://localhost:5000/metrics

Expected:
- /health returns HTTP 200
- /fail returns HTTP 500
- /metrics exposes uc19_http_requests_total

The /fail endpoint intentionally generates failures for testing.

## 9. Install Prometheus and Alertmanager

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

Install:

helm install uc19-prometheus prometheus-community/prometheus \
  --namespace usecase19 \
  -f prometheus-values.yaml

For an existing installation, use helm upgrade instead of helm install.

Verify:

kubectl get pods -n usecase19

## 10. Docker Desktop Troubleshooting

Problem:
Prometheus node-exporter may enter CrashLoopBackOff because of a host filesystem mount restriction.

Resolution:
Disable node-exporter in prometheus-values.yaml:

prometheus-node-exporter:
  enabled: false

Apply the updated values using helm upgrade.

This setting is included in the supplied configuration.

## 11. Access Prometheus

Run in a separate terminal:

kubectl port-forward -n usecase19 svc/uc19-prometheus-server 9090:80

Open:

http://localhost:9090

Query:

uc19_http_requests_total

Why: Verifies that Prometheus collects application request metrics.

## 12. Define the SLI

SLI means Service Level Indicator.

For this demonstration, the SLI measures the percentage of successful requests among the application's instrumented /health and /fail requests.

PromQL:

100 * sum(uc19_http_requests_total{status="success"}) / sum(uc19_http_requests_total)

This is a cumulative demonstration query, not a rolling production SLI.

## 13. Define the SLO

SLO means Service Level Objective.

Target: 99% successful requests.

The application meets the target when its measured success rate is at least 99%.

## 14. Calculate the Error Budget

Error budget = 100% - SLO target

100% - 99% = 1%

Example:
For 10,000 measured requests, a 1% request-based error budget allows 100 failed requests during the defined SLO measurement period.

The SLO measurement period must be agreed upon in a production system.

## 15. Configure the Alert Rule

Alert name:

UC19HighErrorRate

The Prometheus alert expression checks:

- Failed requests over the last 5 minutes
- Total requests over the last 5 minutes
- Error rate greater than 1%
- At least some request traffic

The threshold must remain violated for 1 minute before the alert enters FIRING.

The rule is included in prometheus-values.yaml under serverFiles.alerting_rules.yml.

The standalone slo-alert-rules.yaml is provided as a reference.

## 16. Test the Alert

Generate 20 failed requests:

for i in {1..20}; do curl -s -o /dev/null http://localhost:5000/fail; done; echo "20 failed requests generated"

Open:

http://localhost:9090/alerts

Expected alert progression:

INACTIVE -> PENDING -> FIRING

The alert can later return to INACTIVE when the rolling five-minute error-rate condition is no longer violated.

## 17. Access Alertmanager

Run in a separate terminal:

kubectl port-forward -n usecase19 svc/uc19-prometheus-alertmanager 9093:9093

Open:

http://localhost:9093

Check Alertmanager health:

curl -s http://localhost:9093/-/healthy

Expected:

OK

## 18. Verify Alert Delivery

Check Prometheus alerts:

curl -s http://localhost:9090/api/v1/alerts | python3 -m json.tool

Check Alertmanager:

curl -s 'http://localhost:9093/api/v2/alerts?active=true&silenced=true&inhibited=true&unprocessed=true' | python3 -m json.tool

Run the Alertmanager check while the Prometheus alert is FIRING.

Expected:
Alertmanager receives UC19HighErrorRate with severity warning and service uc19-slo-app.

Receiver:
default-receiver

This confirms reception and routing within Alertmanager, not delivery to external email or Slack.

## 19. Troubleshooting Performed

Issue 1: Prometheus was not scraping application metrics.
Cause: Extra scrape configuration was initially placed under the wrong Helm values key.
Fix: Use top-level extraScrapeConfigs in prometheus-values.yaml.

Issue 2: Node-exporter entered CrashLoopBackOff.
Cause: Docker Desktop host filesystem mount limitation.
Fix: Disable prometheus-node-exporter.

Issue 3: Alertmanager API returned [].
Explanation: The alert may have resolved, or Alertmanager may not yet have received it.
Verification: Check Prometheus FIRING state and then query Alertmanager while the alert is active.

Issue 4: zsh parse error.
Cause: Terminal prompt or previous JSON output was pasted as a shell command.
Fix: Copy only the command.

## 20. Final Verified Results

- Flask application deployed successfully
- Kubernetes application pod Running
- Prometheus scraping application metrics
- SLI query tested
- 99% SLO target defined
- 1% error budget calculated
- High-error-rate alert transitioned to PENDING and FIRING
- Alert later returned to INACTIVE
- Alertmanager health check returned OK
- Alertmanager API confirmed receipt of UC19HighErrorRate
- Alert routed to default-receiver

## Important Production Note

This is a simplified training demonstration.

The application only counts requests to the instrumented endpoints. A real production SLI should measure meaningful user-facing requests, exclude appropriate traffic, use a defined measurement period, and typically use recording rules and multi-window error-budget burn-rate alerts.

## Conclusion

Use Case 19 demonstrates how application metrics flow from Flask to Prometheus, how an SLO and error budget are evaluated, and how Prometheus sends a firing alert to Alertmanager.
