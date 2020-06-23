### Install docker-ce and log in to OpenTelekom image registry

'''
> sudo install-docker-repo <openstack cloud name from cloud.yaml>
'''

It executes the following steps:
1. It installs docker-ce
2. It registers the OTC image registry in docker client (`--insecure` is needed due to lacking domain CN entry in certificate of the registry)
3. t uses your OPenstack credentials from '~/.config/openstack/clouds.yaml' to log docker in to your private image registry using the 'auth_registry' script

As a result, you have aDocker secret for further steps in Kubernetes.