#!/usr/bin/python

# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: os_subnet_facts
short_description: Retrieve facts about one OpenStack subnet.
version_added: "2.0"
author: "Bernd Rederlechner (@brederle)"
description:
    - Retrieve facts about one or more subnets from OpenTelekom with vpc references.
requirements:
    - "python >= 2.7"
    - "openstacksdk"
options:
   name:
     description:
        - Name or ID of the subnet.
        - Alias 'subnet' added in version 2.8.
     required: false
     aliases: ['subnet']
   filters:
     description:
        - A dictionary of meta data to use for further filtering.  Elements of
          this dictionary may be additional dictionaries.
     required: false
   availability_zone:
     description:
       - Ignored. Present for backwards compatibility
     required: false
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
- name: Gather facts about previously created subnets
  os_subnets_facts:
    auth:
      auth_url: https://identity.example.com
      username: user
      password: password
      project_name: someproject

- name: Show openstack subnets
  debug:
    var: openstack_subnets

- name: Gather facts about a previously created subnet by name
  os_subnets_facts:
    auth:
      auth_url: https://identity.example.com
      username: user
      password: password
      project_name: someproject
    name: subnet1

- name: Show openstack subnets
  debug:
    var: openstack_subnets

- name: Gather facts about a previously created subnet with filter
  # Note: name and filters parameters are not mutually exclusive
  os_subnets_facts:
    auth:
      auth_url: https://identity.example.com
      username: user
      password: password
      project_name: someproject
    filters:
      tenant_id: 55e2ce24b2a245b09f181bf025724cbe

- name: Show openstack subnets
  debug:
    var: openstack_subnets
'''

RETURN = '''
subnets:
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_cloud_from_module

from opentelekom.vpc import vpc_service, vpc2_service
from opentelekom.connection import connect_from_ansible

from openstack import exceptions 


def main():

    argument_spec = openstack_full_argument_spec(
        name=dict(required=False, default=None, aliases=['subnet']),
        filters=dict(required=False, type='dict', default={})
    )
    module = AnsibleModule(argument_spec)

    cloud = connect_from_ansible(module)
    try:
        cloud.add_service( vpc_service.VpcService("vpc", aliases=['vpc'] ))
        cloud.add_service( vpc2_service.Vpc2Service("vpc2.0", aliases=['vpc2'] ))

        subnets = cloud.vpc.find_subnet(name_or_id=module.params['name'],
                                       **module.params['filters'])
        if subnets:
            module.exit_json(changed=False, subnet=subnets.copy())
        else:
            module.fail_json(msg="Subnet %s not found" % module.params['name'])

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
