### Login to otc
'''
https://console.otc.t-systems.com
'''
Autotype login

### Walkthrough CCE / CSS
- Show CCE cluster
- Show empty CSS 

### Open ssh shell
- login
'''
ssh otc-paas
'''
- 

### Provision CCE (optional)
'''
cd 
'''


### Show kubectl up and running
'''
kubectl version
kubectl current-context
kubectl cluster-info
'''

### Show dashboard
'''
kubectl proxy
'''
Browser
'''
http://127.0.0.1:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/#!/overview?namespace=default
'''
Bearer-Token eingeben (Passwort-Store)

Walk through dashboard


### Show empty CSS
- Open Kibana from OTC console 
'''
GET /_cat/indices?v
'''
Get IP of one of the nodes

### Adapt, push image
'''
docker build -t logstash:1.5 .
docker tag logstash:1.5 100.125.7.25:20202/bmw1/logstash:1.5
docker push 100.125.7.25:20202/bmw1/logstash:1.5
'''

### Deploy logstash pod in namespace
Precondition (optional):
'''
kubectl create namespace cce-logstash-demo
kubectl config set-context $(kubectl config current-context) --namespace=cce-logstash-demo
'''

Switch current context ti namespace:
'''
'''