# Use Case 12 — Rotate Secrets Without Breaking the Application

## 1. Objective

Learn how to rotate a Kubernetes Secret without permanently disrupting an application.

In this lab, we will:
- Create a Kubernetes Secret
- Connect the Secret to an application
- Rotate the Secret from Version 1 to Version 2
- Restart the application to load the updated Secret
- Verify application health
- Check logs for exposed secrets
- Document the rollback procedure

## 2. Tools Used

| Tool | Purpose |
|---|---|
| Kubernetes | Manage application workloads |
| Docker Desktop | Run and view the local Kubernetes cluster |
| kubectl | Execute Kubernetes commands |
| Kubernetes Secret | Store a lab-only credential |
| BusyBox | Run a lightweight test container |
| Git | Track project changes |
| GitHub | Store the completed lab documentation |

## 3. Architecture

```text
Kubernetes Cluster (Docker Desktop)
          |
          v
Namespace: usecase12
          |
          +---- Secret: app-secret
          |       |
          |       +---- APP_PASSWORD
          |
          +---- Deployment: secret-demo
                      |
                      v
                 BusyBox Pod
                      |
                      v
             Reads APP_PASSWORD
```

The application reads the Secret through an environment variable.

**Important:** This is a demonstration workload, not a database-connected application. It verifies Secret loading and Pod health, but not database connectivity.

## 4. Create a Kubernetes Namespace

**Command:**

```bash
kubectl create namespace usecase12
```

**Why?**

A namespace isolates our training resources from other Kubernetes applications.

**Verification:**

```bash
kubectl get namespaces
```

**Expected result:** `usecase12` appears with status `Active`.

## 5. Create the Initial Secret (V1)

**Command:**

```bash
kubectl create secret generic app-secret \
  --from-literal=APP_PASSWORD='lab-password-v1' \
  -n usecase12
```

**Why?**

The application needs a credential that is managed separately from its container image.

**Verification:**

```bash
kubectl get secret app-secret -n usecase12
```

**Expected result:** The Secret exists with type `Opaque` and one data entry.

**Security note:** These are dummy training passwords. Never store real credentials in Git or paste them into terminal commands.

## 6. Create a Test Deployment

**Command:**

```bash
kubectl create deployment secret-demo \
  --image=busybox:1.36 \
  -n usecase12 \
  -- /bin/sh -c 'while true; do sleep 30; done'
```

**Why?**

BusyBox provides a lightweight container for testing Secret injection.

## 7. Connect the Secret to the Deployment

**Command:**

```bash
kubectl set env deployment/secret-demo \
  --from=secret/app-secret \
  -n usecase12
```

**Why?**

This configures the Deployment to provide `APP_PASSWORD` to its container as an environment variable.

**Verify rollout:**

```bash
kubectl rollout status deployment/secret-demo -n usecase12
```

**Verify the variable exists without printing it:**

```bash
kubectl exec deployment/secret-demo -n usecase12 -- \
  sh -c 'if [ -n "$APP_PASSWORD" ]; then echo "Secret loaded successfully"; else echo "Secret missing"; fi'
```

**Observed result:**

```text
Secret loaded successfully
```

## 8. Rotate the Secret (V1 → V2)

**Command:**

```bash
kubectl create secret generic app-secret \
  --from-literal=APP_PASSWORD='lab-password-v2' \
  -n usecase12 \
  --dry-run=client -o yaml | kubectl apply -f -
```

**Why?**

Secret rotation replaces an old credential with a new credential.

**Observed result:**

```text
secret/app-secret configured
```

The command also displayed a warning about a missing `last-applied-configuration` annotation. Kubernetes patched the annotation automatically.

**Important:** Updating a Kubernetes Secret does not automatically change environment variables in existing Pods.

## 9. Restart the Application

**Command:**

```bash
kubectl rollout restart deployment/secret-demo -n usecase12
```

**Why?**

A new Pod must start to receive the updated Secret as an environment variable.

**Observed result:**

```text
deployment.apps/secret-demo restarted
```

## 10. Verify Application Health

**Commands:**

```bash
kubectl rollout status deployment/secret-demo -n usecase12
kubectl get pods -n usecase12
```

**Observed results:**

```text
deployment "secret-demo" successfully rolled out
```

The new Pod showed:
- READY: `1/1`
- STATUS: `Running`
- RESTARTS: `0`

**Note:** This lab uses one replica, so a restart may briefly interrupt the workload. Production applications should use an appropriate rolling-update strategy and sufficient healthy replicas.

## 11. Verify the Rotated Secret (V2)

**Command:**

```bash
kubectl exec deployment/secret-demo -n usecase12 -- sh -c '
if [ "$APP_PASSWORD" = "lab-password-v2" ]; then
  echo "SUCCESS: Application received rotated secret V2"
else
  echo "FAILED: Application did not receive rotated secret V2"
fi'
```

**Why?**

A successful Pod restart does not prove the new Secret was loaded. This check confirms the application received V2 without printing the credential.

**Observed result:**

```text
SUCCESS: Application received rotated secret V2
```

## 12. Check Application Logs

**Command:**

```bash
kubectl logs deployment/secret-demo -n usecase12
```

**Why?**

Logs should be inspected for application errors and accidental credential exposure.

**Observed result:** No log output.

This is expected because the BusyBox container runs a sleep loop.

No passwords were printed in the inspected container logs. This does not establish that other systems, terminal history, or Kubernetes audit logs are free of credentials.

## 13. Rollback Procedure

**Scenario:** The application fails after rotating to V2.

**Rollback plan:**

1. Restore the previously working Secret value.
2. Restart the Deployment.
3. Wait for the rollout to finish.
4. Verify the Pod is healthy.
5. Confirm the application received the restored Secret.

**Restore V1 (lab only):**

```bash
kubectl create secret generic app-secret \
  --from-literal=APP_PASSWORD='lab-password-v1' \
  -n usecase12 \
  --dry-run=client -o yaml | kubectl apply -f -
```

**Restart the Deployment:**

```bash
kubectl rollout restart deployment/secret-demo -n usecase12
```

**Verify rollout:**

```bash
kubectl rollout status deployment/secret-demo -n usecase12
```

**Verify the restored version:**

```bash
kubectl exec deployment/secret-demo -n usecase12 -- \
  sh -c '[ "$APP_PASSWORD" = "lab-password-v1" ] && echo "Rollback successful" || echo "Rollback verification failed"'
```

**Status:** Rollback is documented but has not been executed.

In a real environment, rollback must also account for whether the external service still accepts the previous credential.

## 14. Security Best Practices

- Never commit real credentials to GitHub.
- Do not print passwords in application logs.
- Avoid passing production secrets directly through shell commands.
- Use approved secret-management systems such as Vault or a cloud secrets manager.
- Restrict access using Kubernetes RBAC.
- Remember that Kubernetes Secrets are not automatically encrypted at rest in every cluster configuration.
- Verify both application health and actual service connectivity after production rotation.

## 15. Final Lab Results

| Verification | Result |
|---|---|
| Namespace created | PASS |
| Initial Secret created | PASS |
| Secret injected into Pod | PASS |
| Secret rotated to V2 | PASS |
| Deployment restarted | PASS |
| Pod healthy after restart | PASS |
| V2 loaded successfully | PASS |
| Container logs inspected | PASS |
| Rollback procedure documented | PASS |
| Rollback executed | NOT TESTED |

## 16. GitHub Submission

**Working branch:** `feature/usecase12`

**Documentation folder:** `usecase12-secret-rotation/`

The completed documentation and reproducible Kubernetes configuration should be committed to the feature branch.

Do not commit `.env`, Terraform state files, or actual credentials.

## 17. Conclusion

We successfully rotated a lab-only Kubernetes Secret from V1 to V2, restarted the Deployment, and confirmed that the new Pod loaded the updated value.

The Pod remained healthy after the rollout, and the inspected container logs contained no output.

The exercise demonstrates Kubernetes Secret rotation through environment variables. It does not validate real database connectivity or guarantee zero-downtime rotation.