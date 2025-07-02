# ArgoCD GitOps Configuration

This directory contains the ArgoCD manifests for deploying and managing the Hotel Inventory and Booking System using GitOps best practices.

## Structure
- `project.yaml`: Defines the ArgoCD AppProject, grouping both services for unified management.
- `app-inventory.yaml`: ArgoCD Application manifest for the Inventory Service.
- `app-booking.yaml`: ArgoCD Application manifest for the Booking Service.

## Usage

1. **AppProject Setup**
   - The `project.yaml` manifest defines a project (`hotel-inventory-booking`) that allows both services to be managed together.
   - Apply it to your ArgoCD instance:
     ```sh
     kubectl apply -f argocd/project.yaml
     ```

2. **Application Manifests**
   - Each service has its own Application manifest. These reference the project and point to the respective deployment manifests or Helm charts.
   - Apply them to ArgoCD:
     ```sh
     kubectl apply -f argocd/app-inventory.yaml
     kubectl apply -f argocd/app-booking.yaml
     ```

3. **Sync and Manage**
   - Use the ArgoCD UI or CLI to sync and monitor both applications. Both services will be launched and managed together under the defined project.

## Notes
- Ensure your Git repository is registered as a source in ArgoCD.
- Update the `repoURL` and `path` fields in the Application manifests to match your repository and deployment structure.
- For more advanced configuration (RBAC, resource restrictions), edit `project.yaml` accordingly.
