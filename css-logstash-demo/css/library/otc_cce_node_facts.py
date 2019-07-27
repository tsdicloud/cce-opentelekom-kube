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
module: otc_cce_cert_facts
short_description: Get certs for Cloud Container engine on Open Telekom Cloud
extends_documentation_fragment: python-opentelekom
version_added: "2.0"
author: "B. Rederlechner (@brederle)"
description:
   - Get authentication and server certs for Cloud Container engine on Open Telekom Cloud
options:
   cluster:
     description:
        - Name of the container cluster to get access to
      required: true
   node_ids:
     description:
        - Limit the facts to a list of node ids
   wait:
     description:
        - If true, the method waits with delivering facts until a vertain status is reached.
        This is useful if you want to track a bulk of create/delete node operations in parallel
     default: false
   wait_status:
     description:
        - If wait is True, the field selects whether is is a wait for activation or deletion
    choices: ['active', 'deleted']
   cluster:
     description:
        - Name of the container cluster to get access to
      required: true
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


def main():
    argument_spec = openstack_full_argument_spec(
        cluster=dict(type='str', required=True),
        node_ids=dict(type=list),
        wait_status=dict(type='str', choices=['active', 'deleted'])
    )
    # redefine wait default behavior, wait must be enabled expicitly here
    argument_spec['wait']['default'] = False

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=False,
                           **module_kwargs)

    clustername_id = module.params['cluster']

    cloud = connect_from_ansible(module)
    try:
        # temporary fix for the fact that the new RDS service is not yet in catalog
        cloud.add_service( cce_service.CceService("ccev2.0", aliases=["cce2"]) )

        cluster = cloud.cce2.find_cluster(clustername_id)
        
        if cluster:
            if not module.params['wait']:
                if 'node_ids' in module.params:
                    nodes = filter(lambda res: res.id in module.params['node_ids'], cloud.cce2.cluster_nodes(cluster.id))
                else:
                    nodes = cloud.cce2.cluster_nodes(cluster.id)
                module.exit_json(changed=False, ansible_facts=dict(cluster_nodes=list(nodes)))
            elif module.params['wait_status'] == 'active':
                nodes = cloud.cce2.wait_for_status_nodes(cluster.id, module.params['node_ids'])
                module.exit_json(changed=False, ansible_facts=dict(cluster_nodes=list(nodes)))
            elif module.params['wait_status'] == 'deleted':
                nodes = cloud.cce2.wait_for_delete_nodes(cluster.id, module.params['node_ids'])
                module.exit_json(changed=False, ansible_facts=dict(cluster_nodes=list(nodes)))
        
        module.exit_json(changed=False, ansible_facts={})

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
