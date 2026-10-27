# Use Case 14 — Blue-Green Deployment Using Kubernetes

## Objective

Implement Blue-Green Deployment using Kubernetes Deployments and a Service. Demonstrate traffic switching, health verification, failure simulation, and rollback.

## Environment

- Operating System: macOS
- Container Platform: Docker Desktop
- Orchestration: Kubernetes
- Application: Nginx
- Namespace: `usecase14`
- Git Branch: `feature/usecase14`

## 1. Deploy Blue and Green

Created two Kubernetes Deployments:

- `blue-deployment` — Stable version
- `green-deployment` — New release environment

Both Deployments use `nginx:alpine` and have one replica.

## 2. Configure Kubernetes Service

Created `bluegreen-service` with the initial selector:

```yaml
selector:
  app: bluegreen-demo
  version: blue
```

This routes Service traffic to Blue Pods.

## 3. Verify Blue Traffic

Checked Service routing:

```bash
kubectl describe service bluegreen-service -n usecase14
```

Verified that the Service selected the Blue Pod.

Sent an HTTP request through the Service and received the Nginx welcome page.

## 4. Verify Green Health

Checked Green Pods:

```bash
kubectl get pods -n usecase14 -l version=green -o wide
```

Verified that Green was Running and Ready.

Tested Green directly and received a successful HTTP response.

Checked application logs:

```bash
kubectl logs deployment/green-deployment -n usecase14 --tail=20
```

Observed an HTTP `200` response in the access logs.

## 5. Switch Traffic to Green

Updated the Service selector:

```yaml
selector:
  app: bluegreen-demo
  version: green
```

Applied the change:

```bash
kubectl apply -f usecase14-blue-green/service.yaml
```

Verified that the Service endpoint changed from Blue to Green.

Sent an HTTP request through the Service and received:

```text
HTTP Status: 200
```

## 6. Simulate a Failed Release

Updated Green to an intentionally invalid image:

```bash
kubectl set image deployment/green-deployment nginx=nginx:nonexistent-usecase14 -n usecase14
```

Checked Pod status:

```bash
kubectl get pods -n usecase14 -l version=green
```

Observed:

```text
ImagePullBackOff
```

The new Pod failed to start, while the previous healthy Green Pod remained running.

This demonstrated a failed rollout, not a confirmed application outage.

## 7. Roll Back Traffic to Blue

Changed the Service selector back to:

```yaml
selector:
  app: bluegreen-demo
  version: blue
```

Applied the configuration:

```bash
kubectl apply -f usecase14-blue-green/service.yaml
```

Verified that the Service endpoint returned to Blue.

Tested the Service and received:

```text
HTTP Status: 200
```

## 8. Restore the Green Deployment

Reverted Green's failed Deployment revision:

```bash
kubectl rollout undo deployment/green-deployment -n usecase14
```

Verified the final state:

```bash
kubectl get deployments,pods -n usecase14
```

Both Blue and Green Deployments returned to `1/1` Ready, with their Pods Running and zero restarts.

## 9. Rollout Stop Signals

A release should be stopped or rolled back when:

- New Pods cannot start (`ImagePullBackOff`).
- Pods fail readiness checks.
- HTTP requests return errors.
- Application logs show critical failures.
- Error rates or latency exceed acceptable thresholds.

## 10. Final Result

Successfully demonstrated:

- Blue and Green Deployments running simultaneously.
- Kubernetes Service-based traffic switching.
- HTTP health verification.
- Failed release detection.
- Traffic rollback to Blue.
- Recovery of the Green Deployment.

**Limitation:** Both Deployments used the same Nginx application image. This lab demonstrated traffic routing and rollback mechanics rather than a functional application version upgrade.