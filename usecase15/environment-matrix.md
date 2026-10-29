# Use Case 15 - Multi-Environment Promotion

| Setting | Dev | QA | Stage | Prod |
|---|---|---|---|---|
| Namespace | uc15-dev | uc15-qa | uc15-stage | uc15-prod |
| Replicas | 1 | 1 | 2 | 2 |
| CPU Request | 100m | 100m | 200m | 200m |
| Memory Request | 128Mi | 128Mi | 256Mi | 256Mi |
| DB Secret | claims-db-dev | claims-db-qa | claims-db-stage | claims-db-prod |
| Approval | Automatic | Automatic | Manual | Manual |
| Rollback | Helm | Helm | Helm | Helm |

## Image Promotion
Dev -> QA -> Stage -> Prod

Use the same Docker image digest across all environments.

## Secrets
Use separate namespaces and database Secrets.
Never store passwords in Git.

## Approvals
Stage and Prod require manual approval in the CI/CD pipeline.

## Rollback
Use Helm to roll back each environment independently.
