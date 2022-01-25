# Django Service Bootstrap

This repo is used as a template to build a new Django-based, Kubernetes-deployed service that can be quickly ready for production. It contains boilerplate code under `service` with most common features and known best practices for BH services.

It makes use of BH's [new-service-recipes](https://github.com/blinkhealth/new-service-recipes) to add and apply the required Terragrunt/Terraform configuration that provisions all accompanying infrastructure.


## Architecture and design

***TODO***


## Test locally

### Build image
```
docker build --build-arg ARTIFACTORY_USER=user.name@blinkhealth.com \
   	  --build-arg ARTIFACTORY_PASS=my_password \
	    -t {project-name}:dev .
```
### Run service container
```
docker run -it -p 8000:8000 {project-name}:dev
```

### Run with Postgres and Redis
```
docker-compose up
```


## Provision a new Project

1) Create a repo based off this template for your service, and an S3 bucket for its infra, through [bedrock-opus](https://github.com/blinkhealth/bedrock-opus)
    * Module: `git::git@github.com:blinkhealth/terraform-project`
    * Relevant inputs:
        * `name`             : Name of the repo (will match service)
        * `description`      : Description that will go into the repo
        * `team`             : Name of the team within BH Engineering that owns the service
        * `github_team_slug` : Name of the GitHub team that owns the repo
        * `include_rds`      : add as = "no" only if a DB is NOT needed
        * `include_redis`    : add as = "no" only if a Redis cluster is NOT needed
        * `include_sqs`      : add as = "no" only if an SQS queue is NOT needed
        * `include_s3`       : add as = "yes" only if an extra S3 bucket IS needed
        * `iam_users`        : comma-separated list of IAM users (Entry account) that will need access to the Kubernetes namespace
    * Example PR: https://github.com/blinkhealth/bedrock-opus/pull/759

2) Go to the **Infra Bootstrap** workflow in Actions: https://github.com/blinkhealth/${repo-name}/actions/workflows/bootstrap-infra.yml and trigger it (`Run workflow`) for the desired target environment
    * This workflow
        * checks out `new-service-recipes`
        * for each of the listed infra components, it uses Terraform to:
            * copies the corresponding Terragrunt files into the corresponding location under `provisioning/live`, replacing any variables to match the target environment
            * commit to a new branch and open a PR with the changes
            * automatically run the Atlantis flow for the PR (`atlantis plan`, approval, `atlantis apply`)
            * merge the PR
    * At the end of execution, all infra components for the target environment should have been created and all the TG code should be in `main`
    * The process stops if any issues are found during execution, in this case both the GH output and the last opened PR can be reviewed to determine if any manual intervention is required

3) Go to the **Bootstrap base service code** workflow in Actions: https://github.com/blinkhealth/${repo-name}/actions/workflows/bootstrap-code.yml and trigger it (`Run workflow`)
    * This workflow:
        * replaces all occurrences of django-service-bootstrap with the name of your service in within the `service` folder, and places them on the root of the repo
        * removes unused files
        * commits all the changes to the `init` branch and creates a new PR on the repo

4) Validate the Kubernetes configuration and make any changes necessary to the previous PR
    * Confirm individual user listed under `iam_users` can authenticate to the target cluster and access the namespace
    * Review the Helm configuration under `k8s/config/` to ensure it matches the service name, namespace and serviceaccount name
    * Review the deployment params under `.github/workflows/` to ensure it matches the namespace and serviceaccount metadata
    * If any of the above components such as Redis is not needed, remove the corresponding entries from Vault annotations, eg
```
    vault.hashicorp.com/agent-inject-secret-redis: 'django-service-bootstrap-dev/secret/django-service-bootstrap/redis'
    vault.hashicorp.com/agent-inject-template-redis: |
    {{- with secret "django-service-bootstrap-dev/secret/django-service-bootstrap/redis" -}}
        {{ .Data.data | toJSON }}
    {{- end }}
```
    * Also make sure the corresponding code that interacts with this value is removed from the service codebase

5) Deploy the initial version of the code
    * If target environment is Dev, add the `deploy-to-dev` label to the PR created by 3)
        * This will trigger the `deploy-to-dev.yml` workflow
    * If target environment is Staging, just merge the PR
        * This will trigger the `deploy-to-staging.yml` workflow
    * Deployment workflow will:
        * Build the image from Dockerfile
        * Log into and push to the ECR repo created during provisioning
        * Log into the target Kubernetes cluster
        * Add the Helm repo from jFrog
        * Deploy the `python-public-alb` Helm chart with the corresponding image tag and the values defined per `k8s/config/${environment}`

6) Access Service
    * The deployment for each cluster should be reachable at https://{project-name}.{env-name}.blink.codes/

    * To check deployment status
    ```
    helm list
    # or
    kubectl get deployment -n $EKS_NAMESPACE

    kubectl get pods -n $EKS_NAMESPACE
    kubectl logs -n $EKS_NAMESPACE <pod_name_from_previous_command> -c vault-agent-init
    kubectl logs -n $EKS_NAMESPACE <pod_name_from_previous_command> -c python-public-alb
    ```

## Production Deployment

1) Provision Production Environment
    * You can use the bootstrap workflow (`bootstrap-infra.yml`) with `prod` as input env name

2) Create a new Release from `main` to trigger `deploy-to-prod.yml` workflow
