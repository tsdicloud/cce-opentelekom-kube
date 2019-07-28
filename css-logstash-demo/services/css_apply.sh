#!/bin/sh

ansible-playbook -v -i inventories/css-logstash-demo/hosts --vault-password-file ~/.ssh/ansible_vault_pwd --skip-tags "destroy"\
  --tags "vpc, css" \
  -e "{ 'net_admin_debug': False, 'state': 'present', prefix: 'css-stash-demo' }" site.yml 
