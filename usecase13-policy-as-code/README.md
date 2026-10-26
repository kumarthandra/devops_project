# Use Case 13 — Policy as Code for Kubernetes Deployments

## 1. Objective

Implement a Policy as Code check that prevents unsafe Kubernetes Deployment configurations from being deployed.

In this lab, we use **Conftest and Open Policy Agent (OPA)** to validate Kubernetes YAML files.

## 2. Tools Used

| Tool | Purpose |
|---|---|
| VS Code | Create and edit configuration files |
| Conftest | Validate Kubernetes YAML against policies |
| OPA/Rego | Define policy rules |
| Kubernetes | Deploy the validated application |
| Docker Desktop | Verify Deployment and Pod status |
| Git | Version-control the project |

## 3. Policy Requirement

Every container in a Kubernetes Deployment must define:

- CPU request
- Memory request

Deployments missing either resource request must fail validation.

**Why?**

Resource requests help Kubernetes schedule Pods based on their resource requirements.

## 4. Project Structure

```text
usecase13-policy-as-code/
├── policy/
│   └── deployment.rego
├── deployment-unsafe.yaml
├── deployment-safe.yaml
└── README.md
```

## 5. Install and Verify Conftest

Install Conftest:

```bash
brew install conftest
```

Verify installation:

```bash
conftest --version
```

Verified versions:

- Conftest: 0.71.1
- OPA: 1.21.1

## 6. Create the Policy

File: `policy/deployment.rego`

```rego
package main

import rego.v1

deny contains msg if {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.resources.requests.cpu
    msg := sprintf("Container %s is missing CPU request", [container.name])
}

deny contains msg if {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.resources.requests.memory
    msg := sprintf("Container %s is missing memory request", [container.name])
}
```

**Explanation:** The policy rejects Kubernetes Deployments when a container does not specify CPU or memory requests.

## 7. Test the Unsafe Deployment

File: `deployment-unsafe.yaml`

The Nginx container intentionally has no CPU or memory requests.

Run from the project root:

```bash
conftest test usecase13-policy-as-code/deployment-unsafe.yaml \
  --policy usecase13-policy-as-code/policy/
```

**Actual result:**

```text
FAIL - Container nginx is missing CPU request
FAIL - Container nginx is missing memory request

2 tests, 0 passed, 0 warnings, 2 failures, 0 exceptions
```

**Result:** Expected failure. The policy successfully detects both violations.

**Screenshot Proof 1:** Capture the terminal showing both policy failures.

## 8. Fix the Deployment

File: `deployment-safe.yaml`

Add the following configuration to the Nginx container:

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

**Explanation:** CPU and memory requests satisfy the policy. Limits also help control resource consumption, although this policy does not require them.

**Screenshot Proof 2:** Capture the corrected YAML in VS Code.

## 9. Test the Safe Deployment

Run:

```bash
conftest test usecase13-policy-as-code/deployment-safe.yaml \
  --policy usecase13-policy-as-code/policy/
```

**Actual result:**

```text
2 tests, 2 passed, 0 warnings, 0 failures, 0 exceptions
```

**Result:** Successful validation.

**Screenshot Proof 3:** Capture the terminal showing the successful policy test.

## 10. Create the Kubernetes Namespace

Run:

```bash
kubectl create namespace usecase13
```

Set the safe Deployment's namespace to:

```yaml
metadata:
  name: policy-demo
  namespace: usecase13
```

**Why?** This isolates the lab from other Kubernetes workloads.

## 11. Deploy the Safe Application

Run:

```bash
kubectl apply -f usecase13-policy-as-code/deployment-safe.yaml
```

**Actual output:**

```text
deployment.apps/policy-demo created
```

Only the safe Deployment was applied.

## 12. Verify the Application

Run:

```bash
kubectl get deployments,pods -n usecase13
```

Alternatively, open:

**Docker Desktop → Kubernetes → Namespace: usecase13**

Verified results:

- Deployment: `policy-demo`
- Deployment status: Available
- Pods: 1/1
- Pod status: Running
- Kubernetes node: Ready

**Screenshot Proof 4:** Capture the running Deployment and Pod in Docker Desktop.

## 13. Guardrail vs. Noise

**Useful guardrail:** Reject Deployments missing CPU or memory requests.

**Why it is useful:** It prevents a common resource-configuration mistake before deployment.

**Potential noise:** A policy that enforces the same resource values for every workload may reject valid applications with different resource requirements.

A good policy should enforce necessary standards without unnecessarily blocking legitimate changes.

## 14. Important Limitation

Conftest performs validation when its command runs.

In this lab, validation was executed manually before deployment.

**A CI/CD pipeline check has not yet been configured.** To block unsafe configurations automatically, Conftest must be added as a required validation step before deployment.

## 15. Final Result

- Unsafe Deployment rejected by Conftest.
- Safe Deployment passed Conftest.
- Corrected application deployed to Kubernetes.
- Deployment and Pod verified as running.

**Use Case 13 local policy validation and deployment demonstration completed successfully.**