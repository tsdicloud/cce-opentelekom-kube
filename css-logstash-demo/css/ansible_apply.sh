#!/bin/sh

ansible-playbook -v -i inventories/css-logstash-demo/hosts --vault-password-file ~/.ssh/.ansible_vault_pwd --skip-tags "destroy"\
  --tags "css" \
  -e "{ 'net_admin_debug': False, 'state': 'present' }" site.yml 
