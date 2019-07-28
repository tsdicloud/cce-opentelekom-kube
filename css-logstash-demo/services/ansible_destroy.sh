#!/bin/sh

ansible-playbook -v -i inventories/css-logstash-demo/hosts  --vault-password-file ~/.ssh/ansible_vault_pwd --skip-tags "apply"\
  --tags "vpc, cce, css" \
  -e "{ 'net_admin_debug': False, 'state': 'absent', prefix: 'css-stash-demo' }" site.yml 
