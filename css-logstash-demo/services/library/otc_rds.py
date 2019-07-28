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
module: otc_rds
short_description: Add/Remove/update RDS 3.0 on Open Telekom Cloud
extends_documentation_fragment: python-opentelekom
version_added: "2.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add/Remove/update relational database service (RDS)
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
   datastore_version:
     description:
        - Specifies the version of the datastore.
     example: "5.7"
   replication_mode:
     description:
        - high-availability replication mode (if HA is needed).
   replica_of_id:
     description:
        - id of a db instance to create a read replica for.
   parameter_group_id:
     description:
        - reference to own parameter group specification.
   port:
     description:
        - a custom port that deviated from the db standard port
   password:
     description:
        - a db password (required on create)
   backup_start_time:
     description:
        - start time of a backup strategy
   backup_keep_days:
     description:
        - number of days to keep in backup
     type: int
   disk_encryption_id:
      description:
        - reference to a customer master key id (if encryption is needed)
   flavor_ref:
     description:
        - the refernce name for the flavor to use. Must match the datastore spec
   volume_type:
     description:
        - type of the volume; one of COMMON, ULTRAHIGH
   volume_size:
     description:
        - size of the volumes to use
     type: int
   region:
     description:
        - the database reason the DB belongs to (required on create)
   availability_zone:
     description:
        - the availability zone for the primary instance of the db
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
from opentelekom.rds import rds_service
from openstack import exceptions 

def _can_update(module, cloud, res):
    # TODO: support certain spec changes as supported by RDS v1
    pass

def _needs_update(module, cloud, res):
    # TODO: support certain spec changes as supported by RDS v1
    return False

def _create_db(module, cloud):
    # required mandatories for create
    dbparams = {
       'name': module.params['name'],
       'datastore': {
         'type': module.params['datastore_type'],
         'version': module.params['datastore_version']
        },
        'password': module.params['password'],
        'flavor_ref': module.params['flavor_ref'],
        'volume': {
           'type': module.params['volume_type'],
           'size': module.params['volume_size']
        },
        'region': module.params['region'],
        'availability_zone': module.params['availability_zone'],
        'vpc_id': module.params['vpc_id'],
        'subnet_id': module.params['subnet_id'],
        'security_group_id': module.params['security_group_id']
    }
    # add optionals
    replication_mode=module.params['replication_mode']
    if replication_mode is not None:
        dbparams['ha'] = {
          'mode': "Ha",
          'replication_mode': replication_mode 
          }
    parameter_group_id=module.params['parameter_group_id']
    if parameter_group_id is not None:
        dbparams['configuration_id'] = parameter_group_id
    port=module.params['port']
    if port is not None:
        dbparams['port'] = port
    backup_start_time = module.params['backup_start_time']
    if backup_start_time is not None:
        backup_keep_days = module.params['backup_keep_days']
        if backup_keep_days:
            dbparams['backup_strategy'] = {
                'start_time': backup_start_time,
                'keep_days': backup_keep_days
            }
        else:
            dbparams['backup_strategy'] = {
                'start_time': backup_start_time,
            }
    disk_encryption_id = module.params['disk_encryption_id']
    if disk_encryption_id is not None:
        dbparams['disk_encryption_id'] = disk_encryption_id
    # for read replicas
    replica_of_id=module.params['replica_of_id']
    if replica_of_id is not None:
        dbparams['replica_of_id']= replica_of_id
    return cloud.rdsv3.create_db(**dbparams)




def main():
    argument_spec = openstack_full_argument_spec(
        state=dict(type='str', default='present',
                   choices=['absent', 'present']),
        name=dict(type='str', required=True),
        datastore_type=dict(type='str'),
        datastore_version=dict(type='str'),
        replication_mode=dict(type='str', default=None),
        replica_of_id=dict(type='str', default=None),
        parameter_group_id=dict(type='str', default=None),
        port=dict(type='str', default=None),
        password=dict(type='str', no_log=True),
        backup_start_time=dict(type='str', default=None),
        backup_keep_days=dict(type='int', default=None),
        disk_encryption_id=dict(type='str', default=None),
        flavor_ref=dict(type='str'),
        volume_type=dict(type='str'),
        volume_size=dict(type='int'),
        region=dict(type='str'),
        availability_zone=dict(type='str'),
        vpc_id=dict(type='str'),
        subnet_id=dict(type='str'),
        security_group_id=dict(type='str')
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
        cloud.add_service( rds_service.Rds3Service("rdsv3") )

        db = cloud.rdsv3.find_db(name)

        # FIXME
        # if module.check_mode:
        #    module.exit_json(changed=_system_state_change(module, subnet,
        #                                              cloud))

        if state == 'present':
            if not db:
                db = _create_db(module, cloud)
                changed = True
            else:
                changed = False
            if changed and module.params['wait']:
                cloud.rdsv3.wait_for_status(db)
            module.exit_json(changed=changed, id=db.id, rds=db.copy())
                         
        elif state == 'absent':
            if not db:
                changed = False
            else:
                changed = True
                cloud.rdsv3.delete_db(db)
                if module.params['wait']:
                    cloud.rdsv3.wait_for_delete(db)              
            module.exit_json(changed=changed)

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
