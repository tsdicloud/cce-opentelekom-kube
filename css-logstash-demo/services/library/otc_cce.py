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
module: otc_ccc
short_description: Manage Cloud Container engine on Open Telekom Cloud
extends_documentation_fragment: python-opentelekom
version_added: "2.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add/remove/update cloud container engine on Open Telekom Cloud
options:
   state:
     description:
        - Indicate desired state of the engine
     choices: ['present', 'absent']
     default: present
   name:
     description:
        - Name of the container cluster
     required: true
   type:
     description:
        - Type of cluster.
     choices: ['VirtualMachine', 'BareMetal']
   flavor:
     description:
        - The flavor of the CCE cluster
     example: "cce.s2.small"
   version:
     description:
        - optional CCE Kubernetes version. Latest version if not given.
     example: "v.1.11.3-r1"
   description:
     description:
        - some descriptive comment for the cluster
   vpc_id:
      description:
        - the vpc id for the cluster and its nodes
   subnet_id:
      description:
        - the subnet id for the cluster and its nodes
   high_subnet_id:
      description:
        - the "highway" subnet id; esp. required for bare metal clusters
   container_net_mode:
      description:
        - the network mode of the container network
      choices: ['overlay_l2', 'underlay_ipvlan', 'vpc-router']
   container_net_cidr:
     description:
        - the cidr range for the internal container ip addresses
requirements:
    - "python >= 3.6"
    - "openstacksdk"
    - "python-opentelekom-sdk"
'''

EXAMPLES = '''
'''

from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module
from ansible.module_utils.basic import AnsibleModule

from opentelekom.connection import connect_from_ansible 
from opentelekom.cce import cce_service
from openstack import exceptions 

def _can_update(module, cloud, res):
    # TODO: support resizing and renaming of nodes
    pass

def _needs_update(module, cloud, res):
    # TODO: support resizing and renaming of nodes
    return False


def _create_cluster(module, cloud):
    # required mandatories for create
    metadata = { 'name': module.params['name'] }

    ccespec = {
        'type': module.params['type'],
        'flavor': module.params['flavor'],
        'hostNetwork': {
            'vpc': module.params['vpc_id'],
            'subnet': module.params['subnet_id'],
        },
        'containerNetwork': {
            'mode': module.params['container_net_mode'],
            'cidr': module.params['container_net_cidr']
        }
    }

    # add optionals
    # TODO add tags here
    version = module.params['version']
    if version:
        ccespec['version'] = version
    description = module.params['description']
    if description:
        ccespec['description'] = description

    
    return cloud.cce2.create_cluster(
        metadata = metadata,
        spec = ccespec )




def main():
    argument_spec = openstack_full_argument_spec(
        state=dict(type='str', default='present',
                   choices=['absent', 'present']),
        name=dict(type='str', required=True),
        type=dict(type='str', choices=['VirtualMachine', 'BareMetal']),
        flavor=dict(type='str'),
        version=dict(type='str'),
        description=dict(type='str'),
        vpc_id=dict(type='str'),
        subnet_id=dict(type='str'),
        high_subnet_id=dict(type='str'),
        container_net_mode=dict(type='str', choices=['overlay_l2', 'underlay_ipvlan', 'vpc-router']),
        container_net_cidr=dict(type='str', default="172.16.0.0/16"),
    )

    # FIXME: define some more constraints like mutual exclusives
    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=False,
                           **module_kwargs)

    state = module.params['state']
    name = module.params['name']

    cloud = connect_from_ansible(module)
    try:
        # temporary fix for the fact that the new RDS service is not yet in catalog
        cloud.add_service( cce_service.CceService("ccev2.0", aliases=["cce2"]) )

        cluster = cloud.cce2.find_cluster(name)

        # FIXME
        # if module.check_mode:
        #    module.exit_json(changed=_system_state_change(module, subnet,
        #                                              cloud))

        if state == 'present':
            if not cluster:
                cluster = _create_cluster(module, cloud)
                changed = True
            else:
                changed = False
            if changed and module.params['wait']:
                cloud.cce2.wait_for_status(cluster)
            module.exit_json(changed=changed, id=cluster.id, cce=cluster.copy())
                         
        elif state == 'absent':
            if not cluster:
                changed = False
            else:
                changed = True
                cloud.cce2.delete_cluster(cluster)
                if module.params['wait']:
                    cloud.cce2.wait_for_delete(cluster)              
            module.exit_json(changed=changed)

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
