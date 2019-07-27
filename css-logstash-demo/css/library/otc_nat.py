#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2019, T-Systems International
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: otc_nat
short_description: Add/Remove/update natting gateway service for Open Telekom Cloud
extends_documentation_fragment: openstack
version_added: "2.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add, remove or update an natting gateway service
options:
   state:
     description:
        - Indicate desired state of the resource
     choices: ['present', 'absent']
     default: present
   name:
     description:
       - The name to identify the natting gateway
     required: true
   description:
     description:
        - A description note on the natting gateway
   spec:
     description:
        - The size of the gateway 1=small, ..., 4=xtra large
   vpc_id:
     description:
        - Id of the VPC to add the gateway to
   subnet_id:
     description:
        - The id of the subnet the gateway is located in
requirements:
    - "python >= 2.7"
    - "openstacksdk"
    - "python-opentelekom-sdk"
'''

EXAMPLES = '''
'''

RETURN = '''
nat:
    description: Dictionary describing the NAT gateway.
    returned: On success when I(state) is 'present'.
    type: complex
    contains:
        id:
            description: nat gateway id.
            type: str
            sample: "4bb4f9a5-3bd2-4562-bf6a-d17a6341bb56"
        name:
            description: NAT gateway name.
            type: str
            sample: "own-name-nat-gw"
        description:
            description: NAT gateway description.
            type: str
            sample: "Some NAT comment"
        status:
            description: gateway status.
            type: str
            sample: "OK"
        admin_state_up:
            description: Additional administrational state of the gateway.
            type: str
'''


from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module
from ansible.module_utils.basic import AnsibleModule

from opentelekom.connection import connect_from_ansible 
from opentelekom.nat import nat_service
from openstack import exceptions 

def _can_update(module, cloud, res):
    if res.vpc_id != module.params['vpc_id']:
        module.fail_json(
            msg='Cannot re-assign bnat gateway to another vpc %s' % res.vpc_id)
    if res.subnet_id != module.params['subnet_id']:
        module.fail_json(
            msg='Cannot re-assign bnat gateway to another subnet %s' % res.subnet_id)

def _needs_update(module, cloud, res):
    if (res.name != module.params['name'] or
        res.description != module.params['description'] or
        res.spec != module.params['spec']):
        return True
    else:
        return False


def main():
    argument_spec = openstack_full_argument_spec(
        state=dict(type='str', default='present',
                   choices=['absent', 'present']),
        name=dict(type='str', required=True),
        description=dict(type='str'),
        spec=dict(type='str', default="1"),
        vpc_id=dict(type='str'),
        subnet_id=dict(type='str')
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=False,
                           **module_kwargs)

    state = module.params['state']
    name = module.params['name']

    cloud = connect_from_ansible(module)
    try:
        cloud.add_service( nat_service.NatService("nat") )
        natgw = cloud.nat.find_nat(name)

        # FIXME
        # if module.check_mode:
        #    module.exit_json(changed=_system_state_change(module, subnet,
        #                                              cloud))

        if state == 'present':
            if not natgw:
                natgw = cloud.nat.create_nat(name=name,
                                             description=module.params['description'],
                                             spec=module.params['spec'],
                                             vpc_id=module.params['vpc_id'],
                                             subnet_id=module.params['subnet_id'],
                                             )
                changed = True
            elif ( _can_update(module, cloud, natgw) and
                   _needs_update(module, cloud, natgw) ):
                cloud.nat.update_nat(name=name,
                    description=module.params['description'],
                    spec=module.params['spec'])
                changed = True
            else:
                changed = False
            
            if changed and module.params['wait']:
                cloud.nat.wait_for_status(natgw)
            module.exit_json(changed=changed,
                         nat=natgw.copy(),
                         id=natgw.id)

        elif state == 'absent':
            if not natgw:
                changed = False
            else:
                changed = True
                cloud.nat.delete_nat(natgw)
                if module.params['wait']:
                    cloud.nat.wait_for_delete(natgw)              
            module.exit_json(changed=changed)

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
