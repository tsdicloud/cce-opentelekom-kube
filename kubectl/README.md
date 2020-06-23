### Install kubectl and set up login to OTC CCE clusters
```
> sudo install-kubectl
Usage: install-kubectl [-f] [-c clustername] <cloud alias for clouds.yaml>
                -f: force reload of credentials
                -c: name of a cluster to add/update (all clusters otherwise)
                -u: username for context"
```

It executes the following steps:
1. It installs kubectl
   (please check curl download commands in file if you need a newer version of kubectl)
2. For each specified cluster, it downloads a key + certificate for your Openstack credentials using info taken from '~/.config/openstack/clouds.yaml'.
3. It creates a cluster entry in `~/.kube/config` for each given cluster

You can use the sub-script `cce_auth_cluster_contexts  [-f] [-c clustername] <cloud alias for clouds.yaml>` 