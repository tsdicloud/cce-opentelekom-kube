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
module: otc_nat_snatrule
short_description: Add/Remove SNAT RULE of a natting gateway for Open Telekom Cloud
extends_documentation_fragment: openstack
version_added: "2.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add or remove a SNAT rule for natting gateway service
options:
   state:
     description:
        - Indicate desired state of the resource
     choices: ['present', 'absent']
     default: present
   network_name:
     description:
        - Name of the network to which the subnet should be attached
        - Required when I(state) is 'present'
   nat_gateway_id:
     description:
       - The id to identify the natting gateway the rule belongs to
     required: true
   eip_id:
     description:
        - Id of the EIP by which the rule accesses the internet
   subnet_id:
     description:
        - The subnet that access the internet. Mutual exclusive to cidr
   cidr:
     description:
        - a CIDR network range that is allowed to access the internet.
          Mutual exclusive to subnet_id

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

def _find_snatrule(module, cloud, nat_gateway_id, subnet_id, cidr):
    if subnet_id is not None:
        rules = list(cloud.nat.snat_rules(nat_gateway=nat_gateway_id, subnet_id=subnet_id))
    elif cidr is not None:
        rules = list(cloud.nat.snat_rules(nat_gateway=nat_gateway_id, cidr=cidr))
    else:
        module.fail_json(
            msg='Need at least subnet_id or cidr to identify a SNAT rule')
    if rules:
        return rules[0]
    else:
        return None

def main():
    argument_spec = openstack_full_argument_spec(
        nat_gateway_id=dict(type='str', required=True),
        subnet_id=dict(type='str'),
        cidr=dict(type='str'),
        eip_id=dict(type='str'),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = openstack_module_kwargs(
        mutually_exclusive=[
            ['subnet_id', 'cidr'],
        ]
    )
    module = AnsibleModule(argument_spec,
                           supports_check_mode=False,
                           **module_kwargs)

    state = module.params['state']
    nat_gateway_id = module.params['nat_gateway_id']
    subnet_id = module.params['subnet_id']
    cidr = module.params['cidr']

    cloud = connect_from_ansible(module)
    try:
        cloud.add_service( nat_service.NatService("nat") )
        rule = _find_snatrule(module, cloud, nat_gateway_id, subnet_id, cidr)

        # FIXME
        # if module.check_mode:
        #    module.exit_json(changed=_system_state_change(module, subnet,
        #                                              cloud))

        if state == 'present':
            if not rule:
                if subnet_id is not None:
                    rule = cloud.nat.create_snat_rule(nat_gateway_id=nat_gateway_id,
                                                  eip_id=module.params['eip_id'],
                                                  subnet_id=subnet_id
                                                  )
                else:
                    rule = cloud.nat.create_snat_rule(nat_gateway_id=nat_gateway_id,
                                                  eip_id=module.params['eip_id'],
                                                  cidr=cidr
                                                  )
                changed = True
            else:
                changed = False
            module.exit_json(changed=changed,
                         nat=rule.copy(),
                         id=rule.id)
        elif state == 'absent':
            if not rule:
                changed = False
            else:
                changed = True
                cloud.nat.delete_snat_rule(rule)
            module.exit_json(changed=changed)

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
