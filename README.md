# cce-opentelekom-kube
Installation scripts and tools to establish a docker/kubectl controller for OpenTelekomClout (OTC) CCE service


### Prerequisites
- enable Shared SNAT on cluster VPC (ot use a natting gateway) to pull public (docker) images
- Run installation of prerequisites
  ```> install-requirements
  ```
  The script installs some useful Openstack tools to make login with the control client easier.

### Step 1: Install docker-ce and log in to OpenTelekom image registry
Go to [Docker](./docker)
to find helper scripts and artefacts

### Step 2: Install Kubernetes commandline client `kubectl` and log in to cluster
Go to [Google Kubectl](./kubectl)
to find helper scripts and artefacts

### Step 3 (optional): Install suitable original Kubernetes dashboard
Go to [original Kubernetes Dashboard](./dashboard)
to find helper scripts and artefacts

### For each new namespace: create a secret for repo access
Go to [Google Kubectl](./kubectl)
and use `cce_kubesecret `
