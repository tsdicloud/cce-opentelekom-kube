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
module: otc_queue
short_description: Creates/removes a queue from Open Telekom Cloud DMS
extends_documentation_fragment: opentelekom-ansible
version_added: "1.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add or remove a queue in Distributed Messaging Service of an OpenTelekomCloud project.
options:
   name:
     description:
        - Name to be assigned to the queue.
     required: true
   queue_mode:
     description:
        - the kind of queue: NORMAL, FIFO, KAFKA_HA, KAFKA_HT
   description:
     description:
        - free-text detail description of the queue
   redrive_policy:
     description:
        - enable or disable deadletter queues (only for NORMAL or FIFO mode)
   max_consume_count:
     description:
        - maximum number of messages failed to consume (1-100)
   retention_hours:
     description:
        - time in hours to keep messages (1-72), only for mode KAFKA
         
   state:
     description:
        - Indicate desired state of the resource.
     choices: ['present', 'absent']
     default: present
     version_added: "2.7"
requirements:
     - "openstacksdk"
     - "python-opentelekom-sdk"
'''

EXAMPLES = '''
'''

RETURN = '''
queue:
    description: Dictionary describing the queue.
    returned: On success when I(state) is 'present'.
    type: complex
    contains:
        id:
            description: queue id.
            type: str
            sample: "4bb4f9a5-3bd2-4562-bf6a-d17a6341bb56"
        name:
            description: queue name.
            type: str
            sample: "own-name-vpc"
        status:
            description: queue status.
            type: str
            sample: "OK"
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module

from opentelekom.connection import connect_from_ansible 
from opentelekom.dms import dms_service
from openstack import exceptions 

def main():
    argument_spec = openstack_full_argument_spec(
        name=dict(type='str', required=True),
        queue_mode=dict(type='str', choices=["NORMAL", "FIFO", "KAFKA_HA", "KAFKA_HT"]),
        description=dict(type='str'),
        redrive_policy=dict(default='enable', choices=['enable', 'disable']),
        max_consume_count=dict(type='int'),
        retention_hours=dict(type='int'),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    state = module.params['state']
    name = module.params['name']
    mode = module.params['queue_mode']

    cloud = connect_from_ansible(module)
    try:
        cloud.add_service( dms_service.DmsService("dmsv1", aliases=['dms'] ))

        q = cloud.dms.find_queue(name)

        if state == 'present':
            if not q:
                if mode == "NORMAL" or mode == "FIFO":        
                    params = {
                        "name": name,
                        "description": module.params['description'],
                        "queue_mode": mode,
                        "redrive_policy": module.params['redrive_policy'],
                    }
                    if module.params['redrive_policy'] == 'enabled' and module.params['max_consume_count']:
                        params['max_consume_count'] = module.params['max_consume_count']
                else:
                    params = {
                        "name": name,
                        "description": module.params['description'],
                        "queue_mode": mode,
                        "retention_hours": module.params['retention_hours'],
                    }
                q = cloud.dms.create_queue(**params)
                changed = True
            else:
                changed = False
            module.exit_json(changed=changed, queue=q.copy(), id=q.id )

        elif state == 'absent':
            if not q:
                module.exit_json(changed=False)
            else:
                cloud.dms.delete_queue(q)
                module.exit_json(changed=True)

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
