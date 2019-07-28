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
        name=dict(type='str', required=True)
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=False,
                           **module_kwargs)

    clustername_id = module.params['name']

    cloud = connect_from_ansible(module)
    try:
        # temporary fix for the fact that the new RDS service is not yet in catalog
        cloud.add_service( cce_service.CceService("ccev2.0", aliases=["cce2"]) )

        cluster = cloud.cce2.find_cluster(clustername_id)
        
        if cluster:
            cert_info = cloud.cce2.get_cluster_certs(cluster)
            if cert_info:
                module.exit_json(changed=False, ansible_facts=dict(cluster_certs=cert_info))
        
        module.exit_json(changed=False, ansible_facts={})
    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
