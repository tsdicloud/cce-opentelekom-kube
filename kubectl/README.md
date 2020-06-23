### Install kubectl and set up login to OTC CCE clusters
```
> sudo install-kubectl
Usage: install-kubectl [-f] [-c clustername] <cloud alias for clouds.yaml>
                -f: force reload of credentials
                -c: name of a cluster to add/update (all clusters otherwise)
                -u: username for context
```

It executes the following steps:
1. It installs kubectl
   (please check curl download commands in file if you need a newer version of kubectl)
2. For each specified cluster, it downloads a key + certificate for your Openstack credentials using info taken from '~/.config/openstack/clouds.yaml'.
3. It creates a cluster entry in `~/.kube/config` for each given cluster

NOTES:
- You can use the sub-script `cce_auth_cluster_contexts [-f] [-c clustername] <cloud alias for clouds.yaml>` to update your credentials in the config at any time.
- To start, set your context once with so that you don´t have to enter it any time
```> kubectl config use-context user_<clustername>
```
- You can check `kubectl` with
```> kubectl version
> kubectl get namespace
```

### Foreach namespace: create a repo secret and use it in kube manifest yamls
if you reference a container in your kubernetes yamls, and you use the OTC CCE image repo, you have to
- refer properly to the image
- use a secret to have access to the private image repo.
An example snipppet is:
```
namespace: mynamespace
...
spec:
  spec:
      containers:
      - image: 100.125.7.25:20202/my_organisation/my_image:1.42
      imagePullSecrets:
      - name: reposecret
```

Note: if your image is based upon 'external' images from internet sources, you have to have SNAT configured because Kubernetes takes these directly from their sources.

You can create the secret by using
```> cce_kubesecret mynamespace reposecret
```
The secret is composed from the informations in your `~/.docker/config.json`.
