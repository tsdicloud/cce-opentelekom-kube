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
module: otc_queue_group
short_description: Creates/removes a consumer group from a queue
extends_documentation_fragment: opentelekom-ansible
version_added: "1.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add or remove a consumer_group to/from a queue in Distributed Messaging Service
options:
   name:
     description:
        - Name to be assigned to the queue.
     required: true
   queue_id:
     description:
        - the refernce to the queue the group is acssociated with
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
queue_group:
    description: Dictionary describing the queue group.
    returned: On success when I(state) is 'present'.
    type: complex
    contains:
        id:
            description: queue id.
            type: str
            sample: "4bb4f9a5-3bd2-4562-bf6a-d17a6341bb56"
        name:
            description: queue group name.
            type: str
            sample: "own-name-qg"
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
        queue_id=dict(type='str'),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    state = module.params['state']
    name = module.params['name']
    queue = module.params['queue_id']

    cloud = connect_from_ansible(module)
    try:
        cloud.add_service( dms_service.DmsService("dmsv1", aliases=['dms'] ))

        qgroup = cloud.dms.find_queue_group(queue=queue, name_or_id=name)

        if state == 'present':
            if not qgroup:
                qgroup = cloud.dms.create_queue_group(queue=queue,name=name)
                changed = True
            else:
                changed = False
            module.exit_json(changed=changed, queue_group=qgroup.copy(), id=qgroup.id )

        elif state == 'absent':
            if not qgroup:
                module.exit_json(changed=False)
            else:
                cloud.dms.delete_queue_group(queue=queue,group=qgroup)
                module.exit_json(changed=True)

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
