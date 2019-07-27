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
module: otc_css
short_description: Add/Remove/update CSS on Open Telekom Cloud
extends_documentation_fragment: python-opentelekom
version_added: "2.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add/Remove Cloud Search Service/Elasticsearch service on Open Telekom Cloud
options:
   state:
     description:
        - Indicate desired state of the DB
     choices: ['present', 'absent']
     default: present
   name:
     description:
        - Name of the database instance
     required: true
   datastore_type:
     description:
        - Specifies the database type, e.g. mysql, sqlserver, postgresql.
     default: "elasticsearch"
   datastore_version:
     description:
        - Specifies the version of the datastore.
     example: "6.2.3"
   instanceNum:
     description:
        - number of cluster nodes (1-32).
     type: int
   flavorRef:
     description:
        - the refernce name for the flavor to use. Must match the datastore spec
   disk_encryption_id:
      description:
        - reference to a customer master key id (if encryption is needed)
   volume_type:
     description:
        - type of the volume; one of COMMON, HIGH, ULTRAHIGH
   volume_size:
     description:
        - size of the volumes to use
     type: int
   httpsEnable:
     description:
        - the string "true" if https is used, string "false" for http (FIXME)
   vpc_id:
     description:
        - the VPC the db belongs to
   subnet_id:
     description:
        - the subnet the db is completely located in
   security_group_id:
     description:
        - the security group to secure access to DB
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
from opentelekom.css import css_service
from openstack import exceptions 

def _can_update(module, cloud, res):
    # TODO: support certain spec changes as supported by RDS v1
    pass

def _needs_update(module, cloud, res):
    # TODO: support certain spec changes as supported by RDS v1
    return False

def _create_cluster(module, cloud):
    # required mandatories for create
    cssparams = {
       'name': module.params['name'],
       'datastore': {
         'type': module.params['datastore_type'],
         'version': module.params['datastore_version']
        },
        'instanceNum': module.params['instances'],
        'instance': { 
            'flavorRef': module.params['flavor_ref'],
            'volume': {
                'volume_type': module.params['volume_type'],
                'size': module.params['volume_size']
            },
            'nics': {
                'vpcId': module.params['vpc_id'],
                'netId': module.params['subnet_id'],
                'securityGroupId': module.params['security_group_id']
            }
        }
    }
    # add optionals
    disk_encryption_id = module.params['disk_encryption_id']
    if disk_encryption_id:
        cssparams['diskEncryption'] = {
          'systemEncrypted': "1",
          'systemCmkid': module.params['disk_encryption_id'] 
          }
    httpsEnable = module.params['httpsEnable']
    if httpsEnable:
        cssparams['httpsEnable'] = httpsEnable

    return cloud.css.create_cluster(**cssparams)




def main():
    argument_spec = openstack_full_argument_spec(
        state=dict(type='str', default='present',
                   choices=['absent', 'present']),
        name=dict(type='str', required=True),
        datastore_type=dict(type='str', default="elasticsearch"),
        datastore_version=dict(type='str', default="6.2.3"),
        instances=dict(type='int', alias="instanceNum"),
        flavor_ref=dict(type='str', alias="flavorRef"),
        volume_type=dict(type='str'),
        volume_size=dict(type='int'),
        vpc_id=dict(type='str'),
        subnet_id=dict(type='str'),
        security_group_id=dict(type='str', alias="securityGroupId"),
        httpsEnable=dict(type='str'),
        disk_encryption_id=dict(type='str', default=None)
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
        cloud.add_service( css_service.CssService("css") )

        cluster = cloud.css.find_cluster(name)

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
                cloud.css.wait_for_status(cluster)
            module.exit_json(changed=changed, id=cluster.id, css=cluster.copy())
                         
        elif state == 'absent':
            if not cluster:
                changed = False
            else:
                changed = True
                cloud.css.delete_cluster(cluster)
                if module.params['wait']:
                    cloud.css.wait_for_delete(cluster)              
            module.exit_json(changed=changed)

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
