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
module: otc_key
short_description: Creates/manages customer mater keys from Open Telekom Cloud kms service
extends_documentation_fragment: opentelekom-ansible
version_added: "1.0"
author: "B. Rederlechner (@brederle)"
description:
   - Manage KMS customer master key.
options:
   state:
     description:
        - Indicate desired state of the resource.
          present: creates a key or returns an enabled one with the name
          enable: enables a disabled one (and cancels a deletion)
          disable: disables key (and cancels a deletion)
          absent: schedules a deletion 
     choices: ['present', 'enable', 'disable', 'absent']
     default: present
   name, key_alias:
     description:
        - Name to be assigned to the CustomerMasterKey.
     required: true
   description, key_description:
     description:
        - Name to be assigned to the VPC.
   origin:
     description:
        - where the key comes from.
     choices: ['kms', 'external']
     default: kms
   pending_days:
     description:
        - Days to schedule the deletion for 7-1096 days
requirements:
     - "openstacksdk"
     - "python-opentelekom-sdk"
'''

EXAMPLES = '''
'''

RETURN = '''
key:
    description: Dictionary describing the CusomerMasterKey.
    returned: On success when I(state) is 'present', 'enable' or 'disable'.
    type: complex
    contains:
        key_id:
            description: key id.
            type: str
            sample: "4bb4f9a5-3bd2-4562-bf6a-d17a6341bb56"
        name:
            description: the key alias name.
            type: str
            sample: "test/my-first-key-000001"
        key_state:
            description: the key status: "2"=enabled, "3"=disabled, "4"=scheduled for deletion
            type: str
            sample: "2"
        key_type:
            description: type identifier for the key
            type: int
        creation_date:
            description: creation datetime
            type: str
        scheduled_deletion_date:
            description: scheduled deletion datetime
            type: str
        default_key_flag:
            description: "1" marks a default key
            type: str
        expiration_time:
            description: key expiration timestamp
            type: str
        origin:
            description: where the key comes from: kms or external
            type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module

from opentelekom.connection import connect_from_ansible 
from opentelekom.kms import kms_service
from openstack import exceptions 

def main():
    argument_spec = openstack_full_argument_spec(
        name=dict(type='str', required=True, aliases=['key_alias']),
        state=dict(default='present', choices=['absent', 'present', 'enabled', 'disabled']),
        origin=dict(default='kms', choices=['kms', 'external']),
        description=dict(type='str', aliases=['key_description']),
        pending_days=dict(default=7, type='int')
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    state = module.params['state']
    name = module.params['name']

    cloud = connect_from_ansible(module)
    try:
        cloud.add_service( kms_service.KmsService("kmsv1", aliases=['kms'] ))

        key = cloud.kms.find_key(name)
        if state == 'present':
            if not key:
                key = cloud.kms.create_key(name=name,
                    origin=module.params['origin'],
                    key_description=module.params['description'])
                changed = True
            elif key.key_state == 2:
                changed = False
            elif key.key_state == 3: 
                msg_disabled = "Key %s is disabled." % key.name
                module.fail_json(msg=msg_disabled)
            elif key.key_state == 4: 
                msg_deleted = "Key %s is scheduled for deletion." % key.name
                module.fail_json(msg=msg_deleted)
            module.exit_json(changed=changed, key=dict(key), id=key.id)
        elif state == 'enabled':
            if not key:
                msg_nokey = "No key %s found for be enabled." % key.name
                module.fail_json(msg=msg_nokey)
            elif key.key_state == 2:
                changed = False
            elif key.key_state == 3:
                cloud.kms.enable_key(key=key)
                changed = True
            elif key.key_state == 4:
                cloud.kms.cancel_delete_key(key=key)
                changed = True
                cloud.kms.enable_key(key=key)
            module.exit_json(changed=changed, key=dict(key), id=key.id)
        elif state == 'disabled':
            if not key:
                msg_nokey = "No key %s found for be disable." % key.name
                module.fail_json(msg=msg_nokey)
            elif key.key_state == 2:
                cloud.kms.disable_key(key=key)
                changed = True
            elif key.key_state == 3:
                changed = False
            elif key.key_state == 4:
                cloud.kms.cancel_delete_key(key=key)
                changed = True
            module.exit_json(changed=changed, key=dict(key), id=key.id)
        elif state == 'absent':
            if not key or key.key_state==4:
                module.exit_json(changed=False)
            else:
                cloud.kms.schedule_delete_key(key=key, pending_days=module.params['pending_days'])
                module.exit_json(changed=True)

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
