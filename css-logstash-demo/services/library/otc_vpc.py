#!/usr/bin/python

# Copyright (c) 2019, T-Systems International
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'T-Systems'}

DOCUMENTATION = '''
---
module: otc_vpc
short_description: Creates/removes a VPC from Open Telekom Cloud
extends_documentation_fragment: opentelekom-ansible
version_added: "1.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add or remove VPC from OpenTelekomCloud project.
options:
   name:
     description:
        - Name to be assigned to the VPC.
     required: true
   cidr:
     description:
        - network cidr of the VPC
     required: true
   enable_shared_snat:
     description:
        - enable the shared snat option for the VPC
   state:
     description:
        - Indicate desired state of the resource.
     choices: ['present', 'absent']
     default: present
     version_added: "2.7"
requirements:
     - "openstacksdk"
     - "python-opentelekom-sdk"
'''

EXAMPLES = '''
'''

RETURN = '''
vpc:
    description: Dictionary describing the VPC.
    returned: On success when I(state) is 'present'.
    type: complex
    contains:
        id:
            description: VPC id.
            type: str
            sample: "4bb4f9a5-3bd2-4562-bf6a-d17a6341bb56"
        name:
            description: VPC name.
            type: str
            sample: "own-name-vpc"
        status:
            description: VPC status.
            type: str
            sample: "OK"
        routes:
            description: special routes added to the VPC.
            type: complex
            contains:
                destination:
                    description: the destination netwrok segment as CIDR
                    returned: always
                    type: str
                nexthop:
                    description: the next hop of a route (IP address in a subnet of the VPC).
                    returned: always
                    type: str
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module

from opentelekom.connection import connect_from_ansible 
from opentelekom.vpc import vpc_service
from openstack import exceptions 


def _needs_update(module, cloud, res):
    if res.cidr != module.params['cidr']:
        return True
    
    if not hasattr(res, 'enable_shared_snat') and module.params['enable_shared_snat']:
        return True
    
    if hasattr(res, 'enable_shared_snat') and (res.enable_shared_snat != module.params['enable_shared_snat']):
        return True
    
    return False



def main():
    argument_spec = openstack_full_argument_spec(
        name=dict(type='str', required=True),
        cidr=dict(type='str'),
        enable_shared_snat=dict(default=False, type='bool'),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    state = module.params['state']
    name = module.params['name']

    cloud = connect_from_ansible(module)
    try:
        cloud.add_service( vpc_service.VpcService("vpc", aliases=['vpc1'] ))
        cloud.add_service( vpc_service.VpcService("vpc2.0", aliases=['vpc2'] ))

        v = cloud.vpc.find_vpc(name)

        if state == 'present':
            if not v:
                v = cloud.vpc.create_vpc(name=name,
                    cidr=module.params['cidr'],
                    enable_shared_snat=module.params['enable_shared_snat'])
                changed = True
            elif _needs_update(module, cloud, v):
                v = cloud.vpc.update_vpc(vpc=v,
                    name=name,
                    cidr=module.params['cidr'],
                    enable_shared_snat=module.params['enable_shared_snat'])
                changed = True
            else:
                changed = False
            module.exit_json(changed=changed, vpc=v.copy(), id=v.id )

        elif state == 'absent':
            if not v:
                module.exit_json(changed=False)
            else:
                cloud.vpc.delete_vpc(v)
                module.exit_json(changed=True)

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
