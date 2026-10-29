# Use Case 15 — Multi-Environment Promotion

## Objective
Deploy the same backend application across Dev, QA, Stage, and Production using Helm.

## Environment Configuration

| Environment | Namespace | Replicas | Database Secret |
|---|---|---|---|
| Dev | uc15-dev | 1 | claims-db-dev |
| QA | uc15-qa | 1 | claims-db-qa |
| Stage | uc15-stage | 2 | claims-db-stage |
| Production | uc15-prod | 2 | claims-db-prod |

## Docker Image
claims-backend:uc15-v1

The same image tag was used across all four environments.

## Promotion Flow
Dev → QA → Stage → Production

- Dev and QA were deployed using Helm.
- Stage deployment was manually approved.
- Production deployment was manually approved.
- All four environments were verified running.

## Rollback Demonstration
1. Production revision 1: 2 replicas.
2. Production revision 2: Scaled to 3 replicas.
3. Rolled back to revision 1.
4. Helm created revision 3.
5. Verified Production returned to 2 replicas.

## Results
- Dev: 1/1 available
- QA: 1/1 available
- Stage: 2/2 available
- Production: 2/2 available
- Helm rollback: Successful

## Lab Limitations
- Deployments and approvals were performed manually.
- CI/CD approval gates are not yet implemented.
- Environments share one PostgreSQL database in this local lab.
- Image tags were verified, but image digest identity was not verified.