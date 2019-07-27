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
module: otc_eip
short_description: Handles EIP without binding it to a resource
extends_documentation_fragment: opentelekom-ansible
version_added: "1.0"
author: "B. Rederlechner (@brederle)"
description:
   - Aquires/removes an EIP from a resource.
     Unbind is usually done implicitely on the corresponding resource
options:
   reuse:
     description:
        - If true, the modules tries to reuse an unbound EIP
   eip_id:
     description:
        - For absent or unbind state, find by id
   state:
     description:
        - Indicate desired state of the resource.
     choices: ['present', 'absent', 'unbind']
     default: present
requirements:
     - "openstacksdk"
     - "python-opentelekom-sdk"
'''

EXAMPLES = '''
otc_eip:
  cloud: "mycloud"
  state: "present"
register: my_eip

otc_eip:
  cloud: "mycloud"
  state: "absent"
  eip_id: my_eip.id
'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module

from opentelekom.connection import connect_from_ansible 
from openstack import exceptions 

def main():
    argument_spec = openstack_full_argument_spec(
        reuse=dict(type='bool', default=True),
        state=dict(default='present', choices=['absent', 'present']),
        eip_id=dict(type='str')
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    state = module.params['state']

    cloud = connect_from_ansible(module)
    try:
        if state == 'present':

            # find the external network the EIP belongs to
            external_networks = list(cloud.network.networks(is_router_external=True,
                                                        project_id=cloud.session.get_project_id()))
            if not external_networks:
                module.fail_json(msg="No external network for project.")
            external_network = external_networks[0]

            # try to find a free eip first
            eip = None
            if module.params['reuse']:
                eips = cloud.network.ips(
                    floating_network_id=external_network.id,
                    project_id=cloud.session.get_project_id())
                eips = list(filter(lambda ip: ip.port_id is None, eips))
                if eips:
                    eip = eips[0]
                changed = False
            if not eip:
                # if none found: allocate a new EIP
                eip = cloud.network.create_ip(
                    floating_network_id=external_network.id)
                changed = True
            module.exit_json(changed=changed, eip=eip.copy(), id=eip.id)

        elif state == 'absent':
            eip_id = module.params['eip_id']
            eip = cloud.network.get_ip(eip_id)
            if not eip:
                module.exit_json(changed=False)
            else:
                cloud.network.delete_ip(eip_id)
                module.exit_json(changed=True)

        elif state == 'unbind':
            eip_id = module.params['eip_id']
            eip = cloud.network.get_ip(eip_id)
            if not eip:
                module.exit_json(changed=False)
            else:
                cloud.network.delete_port(eip.port_id)
                module.exit_json(changed=True)


    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
