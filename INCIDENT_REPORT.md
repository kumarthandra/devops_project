# Use Case 9 — Incident Report

## 1. Incident Summary

**Incident:** Failed Kubernetes deployment caused by an invalid container image

**Date:** 15 October 2026

**Environment:** Local Docker Desktop Kubernetes

**Namespace:** `uc9`

**Deployment:** `claims-backend-uc9`

**Incident status:** Resolved

## 2. Incident Impact

The new application rollout failed because Kubernetes could not pull the specified container image.

The previous healthy pod remained running, and the health API continued responding with HTTP 200.

**Observed user impact:** No API downtime detected during the checks performed.

**Operational impact:** Deployment of the new application version was blocked.

## 3. Incident Timeline

| Time (IST) | Event |
|---|---|
| 17:22:37 | Incident simulation started |
| After 17:22 | Deployment updated to invalid image `claims-backend:uc9-invalid` |
| After update | New pod entered `ImagePullBackOff` |
| During investigation | Rollout timed out; Kubernetes events confirmed image pull failure |
| 17:28:09 | Existing API returned HTTP 200 during incident |
| Before 17:31:48 | Deployment rolled back successfully |
| 17:31:48 | Recovery verified using API and application logs |

*Exact rollback execution time was not separately recorded.*

## 4. Detection and Investigation

Commands used:

```bash
kubectl get pods -n uc9
kubectl rollout status deployment/claims-backend-uc9 -n uc9 --timeout=10s
kubectl describe deployment claims-backend-uc9 -n uc9
kubectl get events -n uc9 --sort-by=.lastTimestamp
kubectl logs deployment/claims-backend-uc9 -n uc9 --all-pods=true --prefix=true
```

**Evidence collected:**

- New pod reported `ImagePullBackOff`.
- Deployment rollout timed out.
- Kubernetes events showed `ErrImagePull` and a failed image pull.
- Existing Flask pod continued running.
- Health endpoint returned HTTP 200 during the incident.

## 5. Root Cause

The Deployment image was intentionally changed from:

`claims-backend:uc9-good`

to:

`claims-backend:uc9-invalid`

The invalid image was unavailable locally and could not be pulled from the container registry.

Kubernetes therefore could not start the replacement container.

**Root cause classification:** Invalid or unavailable container image reference.

## 6. Recovery Action

Rolled back the Kubernetes Deployment:

```bash
kubectl rollout undo deployment/claims-backend-uc9 -n uc9
```

Verified the recovered deployment:

```bash
kubectl rollout status deployment/claims-backend-uc9 -n uc9 --timeout=120s
kubectl get deployments,pods -n uc9
```

The Deployment returned to `1/1` Ready using `claims-backend:uc9-good`.

## 7. Post-Recovery Verification

At **17:31:48 IST**:

- Health API returned `HTTP/1.1 200 OK`.
- Application returned `"status":"healthy"`.
- Application version was `1.0.1`.
- Kubernetes Deployment was healthy.
- Recent Flask logs showed successful health requests.

## 8. Prevention

**Recommended prevention:** Add a pre-deployment image validation check in the CI/CD pipeline.

Before deployment, verify that the required image and tag exist in the container registry. Reject deployment if the image reference cannot be resolved.

This would help catch invalid image references before they reach Kubernetes.

## 9. Lessons Learned

A failed rollout does not always mean the application is unavailable.

Kubernetes rolling updates can preserve existing healthy pods when replacement pods fail.

Incident responders should confirm actual user impact, inspect deployment events, and verify recovery before closing an incident.