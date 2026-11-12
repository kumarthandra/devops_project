# Use Case 18 — Kubernetes Logging Pipeline Troubleshooting

## 1. Objective

Build a centralized logging pipeline using Kubernetes, Grafana Alloy, Loki, and Grafana.

Simulate a logging pipeline failure, identify why application logs stop appearing, restore the collector, and verify recovery.

**Scenario:** An application continues running and generating logs, but the monitoring team cannot see recent logs in Grafana because the log collector has stopped.

## 2. Architecture

```text
Kubernetes Application
        |
        | JSON logs (stdout)
        v
    Grafana Alloy
        |
        | Collects and forwards logs
        v
      Grafana Loki
        |
        | Stores and queries logs
        v
    Grafana Explore
```

**Component responsibilities:**

- **Application:** Generates structured JSON logs.
- **Grafana Alloy:** Discovers the application pod and forwards its logs.
- **Loki:** Receives, stores, and searches logs.
- **Grafana:** Provides a web interface to investigate logs.

This is a logging pipeline, not a GitLab CI/CD pipeline.

## 3. Prerequisites

Install and configure:

- Docker Desktop with Kubernetes enabled
- `kubectl`
- Helm
- Visual Studio Code
- A web browser

Verify the tools:

```bash
kubectl get nodes
helm version --short
kubectl get storageclass
```

The Kubernetes node should show `Ready`.

## 4. Create the Kubernetes Namespace

```bash
kubectl create namespace usecase18
kubectl get namespaces
```

**Purpose:** Keep all Use Case 18 resources isolated from other Kubernetes projects.

## 5. Deploy the Log-Generating Application

```bash
kubectl create deployment uc18-log-app \
  --image=busybox:1.36 \
  --namespace=usecase18 \
  -- /bin/sh -c 'while true; do echo "{\"service\":\"uc18-demo\",\"environment\":\"lab\",\"version\":\"v1\",\"request_id\":\"UC18-TEST-001\",\"message\":\"Logging pipeline test\"}"; sleep 5; done'
```

Wait for the deployment:

```bash
kubectl rollout status deployment/uc18-log-app -n usecase18 --timeout=180s
```

Verify application logs:

```bash
kubectl logs deployment/uc18-log-app -n usecase18 --tail=5
```

**Expected log:**

```json
{"service":"uc18-demo","environment":"lab","version":"v1","request_id":"UC18-TEST-001","message":"Logging pipeline test"}
```

**Result:** The application generates one structured JSON log approximately every five seconds.

## 6. Add the Grafana Helm Repository

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

Verify available charts:

```bash
helm search repo grafana/loki
helm search repo grafana/alloy
helm search repo grafana/grafana
```

## 7. Install Loki

Download the Helm chart:

```bash
helm pull grafana/loki --version 7.5.0 --untar
```

The supplied `loki-values.yaml` configures Loki for this local Kubernetes lab.

Validate the chart:

```bash
helm lint ./loki -f loki-values.yaml
```

Preview the installation:

```bash
helm install uc18-loki ./loki \
  -n usecase18 \
  -f loki-values.yaml \
  --dry-run=client --hide-secret
```

Install Loki:

```bash
helm install uc18-loki ./loki \
  -n usecase18 \
  -f loki-values.yaml \
  --timeout 10m
```

Verify:

```bash
kubectl get pods -n usecase18
kubectl get svc -n usecase18
```

**Expected:** The Loki pod `uc18-loki-0` eventually reaches `2/2 Running`.

Loki's internal Kubernetes URL is:

```text
http://uc18-loki.usecase18.svc.cluster.local:3100
```

## 8. Install Grafana Alloy

Download the chart:

```bash
helm pull grafana/alloy --version 1.15.0 --untar
```

The supplied `alloy-values.yaml` configures Alloy to discover the `uc18-log-app` pod and forward its logs to Loki.

Validate:

```bash
helm lint ./alloy -f alloy-values.yaml
```

Preview:

```bash
helm install uc18-alloy ./alloy \
  -n usecase18 \
  -f alloy-values.yaml \
  --dry-run=client --hide-secret
```

Install:

```bash
helm install uc18-alloy ./alloy \
  -n usecase18 \
  -f alloy-values.yaml \
  --timeout 10m
```

Verify:

```bash
kubectl rollout status deployment/uc18-alloy -n usecase18 --timeout=180s
kubectl logs deployment/uc18-alloy -n usecase18 -c alloy --tail=30
```

**Expected:** Alloy becomes ready and reports that it has opened the application's log stream.

## 9. Verify Logs in Loki

Open a terminal and run:

```bash
kubectl port-forward -n usecase18 svc/uc18-loki 3100:3100
```

Keep that terminal open.

In another terminal, run:

```bash
curl -G -s http://localhost:3100/loki/api/v1/query_range \
  --data-urlencode 'query={service="uc18-demo"}' \
  --data-urlencode 'limit=5' \
  | python3 -m json.tool
```

**Expected:** A successful response containing log entries with `UC18-TEST-001`.

This confirms that Alloy has forwarded application logs into Loki.

## 10. Install Grafana

Download the chart:

```bash
helm pull grafana/grafana --version 10.5.15 --untar
```

The supplied `grafana-values.yaml` automatically provisions Loki as the default Grafana data source.

Validate:

```bash
helm lint ./grafana -f grafana-values.yaml
```

Preview:

```bash
helm install uc18-grafana ./grafana \
  -n usecase18 \
  -f grafana-values.yaml \
  --dry-run=client --hide-secret
```

Install:

```bash
helm install uc18-grafana ./grafana \
  -n usecase18 \
  -f grafana-values.yaml \
  --timeout 10m
```

Verify readiness:

```bash
kubectl rollout status deployment/uc18-grafana -n usecase18 --timeout=180s
```

**Note:** Helm may display a chart deprecation warning. This lab uses the chart version tested during the original exercise.

## 11. Open Grafana

In a terminal, run:

```bash
kubectl port-forward -n usecase18 svc/uc18-grafana 3000:80
```

Keep the terminal running.

Open:

```text
http://localhost:3000
```

Username:

```text
admin
```

Retrieve the generated administrator password in another terminal:

```bash
kubectl get secret uc18-grafana \
  -n usecase18 \
  -o jsonpath="{.data.admin-password}" \
  | base64 --decode; echo
```

Do not commit or share the password.

After login, navigate to **Connections → Data sources** and confirm that Loki is available.

## 12. Search Application Logs in Grafana

Open **Grafana → Explore**.

Select the Loki data source and enter:

```logql
{service="uc18-demo"}
```

Set the time range to **Last 15 minutes** and click **Run query**.

**Expected:** JSON log entries containing `UC18-TEST-001`.

This proves the complete logging pipeline works.

## 13. Simulate a Logging Pipeline Failure

Stop the Alloy collector:

```bash
kubectl scale deployment uc18-alloy -n usecase18 --replicas=0
```

Verify:

```bash
kubectl get deployments -n usecase18
```

**Expected:** `uc18-alloy` shows `0/0`, while the application and Grafana remain ready.

Confirm that the application still generates logs:

```bash
kubectl logs deployment/uc18-log-app \
  -n usecase18 \
  --tail=5 \
  --timestamps=true
```

**Observation:** Application logs continue even though Alloy is unavailable.

## 14. Identify the Failure in Grafana

Open Grafana Explore.

Run:

```logql
{service="uc18-demo"}
```

Set the time range to **Last 5 minutes**.

Wait approximately one minute after stopping Alloy, then run the query again.

**Expected:** New log entries stop arriving in Loki. Previously collected logs remain searchable.

**Root cause:** Alloy has zero running replicas, so it cannot collect and forward new application logs.

## 15. Restore the Logging Pipeline

Restart Alloy:

```bash
kubectl scale deployment uc18-alloy -n usecase18 --replicas=1
```

Wait for recovery:

```bash
kubectl rollout status deployment/uc18-alloy \
  -n usecase18 \
  --timeout=180s
```

Open Grafana Explore and run:

```logql
{service="uc18-demo"}
```

**Expected:** Fresh application logs appear again.

Note that some logs generated during the outage may be collected after restart. Verify resumed ingestion rather than assuming every missed log was recovered.

## 16. Final Verification

```bash
kubectl get pods -n usecase18
```

Expected components:

```text
uc18-alloy      2/2   Running
uc18-grafana    1/1   Running
uc18-log-app    1/1   Running
uc18-loki-0     2/2   Running
```

Pod names and ages will differ.

## 17. Common Troubleshooting

**Kubernetes connection refused**

Start Docker Desktop, enable Kubernetes, and verify:

```bash
kubectl get nodes
```

**Pod remains Pending**

Check storage and scheduling:

```bash
kubectl describe pod uc18-loki-0 -n usecase18
kubectl get pvc -n usecase18
```

**Alloy is not ready**

Inspect the deployment and logs:

```bash
kubectl describe deployment uc18-alloy -n usecase18
kubectl logs deployment/uc18-alloy -n usecase18 -c alloy --tail=50
```

**No logs in Grafana**

Check that the application and Alloy are running, confirm the Loki data source URL, and expand the Grafana time range.

**Grafana password incorrect**

Retrieve the generated password from the Kubernetes Secret using the command in Section 11.

**Port already in use**

Stop the existing port-forward process or choose another local port.

## 18. Incident Explanation

**Issue:** Application logs stopped appearing in Grafana.

**Impact:** Engineers lost visibility into recent application activity, making incident investigation more difficult.

**Investigation:** We verified that the application continued producing logs, checked Kubernetes deployments, and identified that Alloy had zero running replicas.

**Root cause:** The Alloy collector was intentionally scaled down.

**Resolution:** We restored Alloy to one replica and verified that new logs were searchable in Grafana.

**Result:** The logging pipeline recovered successfully.

## 19. Completion Checklist

- [ ] Kubernetes is running.
- [ ] Application generates structured JSON logs.
- [ ] Loki is running.
- [ ] Alloy is collecting and forwarding logs.
- [ ] Loki API returns application logs.
- [ ] Grafana is accessible in a browser.
- [ ] Grafana Explore displays application logs.
- [ ] Collector failure is simulated.
- [ ] Missing recent logs are identified.
- [ ] Alloy is restored.
- [ ] Fresh logs are searchable again.
- [ ] All four Kubernetes components are healthy.

**Use Case 18 — Completed Successfully.**
