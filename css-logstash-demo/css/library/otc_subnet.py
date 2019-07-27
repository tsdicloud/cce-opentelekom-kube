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
module: otc_subnet
short_description: Add/Remove subnet to an Open Telekom VPC
extends_documentation_fragment: openstack
version_added: "2.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add or Remove a subnet to a VPC network
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
   name:
     description:
       - The name of the subnet that should be created. Although Neutron
         allows for non-unique subnet names, this module enforces subnet
         name uniqueness.
     required: true
   cidr:
     description:
        - The CIDR representation of the subnet that should be assigned to
          the subnet. Required when I(state) is 'present' and a subnetpool
          is not specified.
     required: false
   gateway_ip:
     description:
        - The IP of the gateway to the subnet. Usually the CIDR with .1 at the end
     required: true
   dhcp_enable:
     description:
        - Whether DHCP should be enabled for this subnet.
     type: bool
     default: 'yes'
   dns_nameservers:
     description:
        - List of DNS nameservers for this subnet (superseeding primary and secondary).
     required: false
   availability_zone:
     description:
        - the availability zone of the subnet (backward compatibility only).
     required: false
   vpc_id:
     description:
        - the id of the VPC to assign the subnet to
     required: true
   extra_dhcp_opts:
     description:
        - Dictionary with extra opt_name/opt_value pairs passed to the API for DHCP configuration
     required: false
     default: {}
     version_added: "2.7"
requirements:
    - "python >= 2.7"
    - "openstacksdk"
    - "python-opentelekom-sdk"
'''

EXAMPLES = '''
'''

import json

from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module
from ansible.module_utils.basic import AnsibleModule

from opentelekom.connection import connect_from_ansible 
from opentelekom.vpc import vpc_service, vpc2_service
from openstack import exceptions 

def _can_update(module, cloud, res):
    if res.vpc_id != module.params['vpc_id']:
        module.fail_json(
            msg='Cannot re-assign subnet to another vpc %s' % res.vpc_id)
    if res.gateway_ip != module.params['gateway_ip']:
        module.fail_json(msg='Cannot change gateway IP %s to  %s' % (res.gateway_ip, module.params['gateway_ip']) )


def _opts_to_dict(extra_dhcp_opts):
    dhcp_opt_map = {}
    for opt in extra_dhcp_opts:
        dhcp_opt_map[opt['opt_key']] = opt['opt_value']
    return dhcp_opt_map


def _dict_to_opts(extra_dhcp_map):
    extra_opt_list = []
    for key, value in extra_dhcp_map:
        extra_opt_list.append({'opt_name': key, 'opt_value': value})
    return extra_opt_list


def _needs_update(module, cloud, res):
    if (res.name != module.params['name'] or
        res.cidr != module.params['cidr'] or
            res.dhcp_enable != module.params['dhcp_enable']):
        return True

    # compare dns Nameserver lists
    # FIXME: should be complement, not intersection!
    if set(res.dnsList).intersect(module.params['dns_nameservers']):
        return True

    # compare dicts
    # FIXME: should be complement, not intersection!
    res_opts = _opts_to_dict(res.dhcp_extra_opts)
    if set(res_opts.items()).intersect(module.params['extra_dhcp_opts'].items()):
        return True
    return False


def main():
    argument_spec = openstack_full_argument_spec(
        state=dict(type='str', default='present',
                   choices=['absent', 'present']),
        name=dict(type='str', required=True),
        cidr=dict(type='str'),
        gateway_ip=dict(type='str'),
        vpc_id=dict(type='str'),
        dhcp_enable=dict(type='bool', default=True),
        dns_nameservers=dict(type='list', default=None),
        availability_zone=dict(type='str'),
        extra_dhcp_opts=dict(type='dict', default=dict()),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=False,
                           **module_kwargs)

    state = module.params['state']
    name = module.params['name']
    gateway_ip = module.params['gateway_ip']

    cloud = connect_from_ansible(module)
    try:
        cloud.add_service( vpc_service.VpcService("vpc", aliases=['vpc'] ))
        cloud.add_service( vpc2_service.Vpc2Service("vpc2.0", aliases=['vpc2'] ))

        subnet = cloud.vpc.find_subnet(name)

        # FIXME
        # if module.check_mode:
        #    module.exit_json(changed=_system_state_change(module, subnet,
        #                                              cloud))

        if state == 'present':
            if not subnet:
                dhcp_extras = _dict_to_opts(module.params['extra_dhcp_opts'])
                if dhcp_extras:
                    subnet = cloud.vpc.create_subnet(name=name,
                                             cidr=module.params['cidr'],
                                             dhcp_enable=module.params['dhcp_enable'],
                                             gateway_ip=gateway_ip,
                                             vpc=module.params['vpc_id'],
                                             dnsList=module.params['dns_nameservers'],
                                             extra_dhcp_opts=dhcp_extras
                                             )
                    subnet.extra_dhcp_opts = module.params['extra_dhcp_opts']
                else:
                    subnet = cloud.vpc.create_subnet(name=name,
                                             cidr=module.params['cidr'],
                                             dhcp_enable=module.params['dhcp_enable'],
                                             gateway_ip=gateway_ip,
                                             vpc=module.params['vpc_id'],
                                             dnsList=module.params['dns_nameservers']
                                             )
                changed = True
            elif ( _can_update(module, cloud, subnet) and
                   _needs_update(module, cloud, subnet) ):
                cloud.vpc.update_subnet(subnet['id'],
                    name=name,
                    cidr=module.params['cidr'],
                    dhcp_enable=module.params['dhcp_enable'],
                    dnsList=module.params['dns_nameservers'],
                    extra_dhcp_opts=_dict_to_opts(
                        module.params['extra_dhcp_opts']) )
                changed = True
            else:
                changed = False
            if changed and module.params['wait']:
                cloud.vpc.wait_for_status(subnet)
            module.exit_json(changed=changed, id=subnet.id, subnet=subnet.copy())
                         
        elif state == 'absent':
            if not subnet:
                changed = False
            else:
                changed = True
                cloud.vpc.delete_subnet(subnet)
                if module.params['wait']:
                    cloud.vpc.wait_for_delete(subnet)              
            module.exit_json(changed=changed)

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
