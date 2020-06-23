## Install Kubernetes Dashboard
Prerequisites:
set your cluster context first with `kubectl config set-context user_<clustername>`

Use installation script 
```> ./install-dashboard
```
It installs the dashboard in `kube-system` namespace

To start the dashboard:
- Establish an SSH tunnel to your local machine, default port 8001
- start `kubectl proxy &` on your remote ssh machine
- open in your local browser 
```http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/
```


For details and alternate approaches:
. Google documentation: https://github.com/kubernetes/dashboard
. OTC approach with Nodeport access instead of kubectl proxy: https://github.com/OpenTelekomCloud/CCE 