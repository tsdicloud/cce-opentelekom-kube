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
module: otc_cce_node
short_description: Manage Cloud Container nodes on Open Telekom Cloud
extends_documentation_fragment: python-opentelekom
version_added: "2.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add/remove/update node of a cce on Open Telekom Cloud
options:
   state:
     description:
        - Indicate desired state of the engine
     choices: ['present', 'absent']
     default: present
   name:
     description:
        - Name of the nodes
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


def _can_update(module, cloud, res):
    # TODO: support resizing and renaming of nodes
    pass


def _needs_update(module, cloud, res):
    # TODO: support resizing and renaming of nodes
    return False


def _match_spec(res, **params):
    '''Find/compare nodes given a specification of the node.
       login and count are ignored beacause we want to has a
       match on technical resource tape and size'''
    
    if ( not res.metadata.name.startswith( params['name']) ):
        return False

    # check basic compute spec
    if ( res.spec.flavor != params['flavor'] or 
            res.spec.availability_zone != params['availability_zone'] ):
        return False

    # check root volume spec
    if (res.spec.root_volume.size != int(params['root_volume']['size']) or
            res.spec.root_volume.type != params['root_volume']['type']):
        return False

    # TODO public_ip is not considered yet
    #if (( hasattr(res.spec.public_ip, 'ids') and res.spec.public_ip.ids != module.params['public_ip']['ids'] ) or
    #        ( hasattr(res.spec.public_ip, 'floating_ip') and
    #            res.public_ip.spec.floating_ip.type != module.params['public_ip']['type'] or
    #            res.public_ip.spec.floating_ip.bandwidth.size != module.params['public_ip']['bandwidth'] or
    #            res.public_ip.spec.floating_ip.bandwidth.sharetype  != module.params['public_ip']['sharetype']  or
    #            res.public_ip.spec.count != module.params['public_ip']['count'] )):
    #    return False
    
    # list of data volumes must have the same size
    if len(res.spec.data_volumes) != len(params['data_volumes']):
        return False

    # if they have the same size, element in the list must have a
    # corresponding on in the other (both ways!)
    volumes = res.spec.data_volumes.copy()
    for volspec in params['data_volumes']:
        found = False
        for volpos, volres in enumerate(volumes):
            if (volres.type == volspec['type'] and 
                    volres.size == int(volspec['size']) ):
                # consume matching entry (to handle dupicates properly)
                volumes.pop(volpos)
                found = True
                break
        # a spec is not contained
        if not found:
            return False

    # at the end, all data_volumes from node must be consumed
    if volumes:
        # node has more volumes than spec
        return False

    return True

def _filter_for_delete(cloud, cluster_id, **params):
    nodes = list(cloud.cce2.cluster_nodes(cluster_id))
    if 'name' in params and params['name'] is not None:
        nodes = filter( lambda res: res.name.startswith(params['name']), nodes )
    if 'flavor' in params and params['flavor'] is not None:
        nodes = filter( lambda res: res.spec.flavor == params['flavor'], nodes )
    if 'availability_zone' in params and params['availability_zone'] is not None:
        nodes = filter( lambda res: res.spec.availability_zone == params['availability_zone'], 
            nodes )
    return list(nodes)


def _add_nodes(cloud, cluster_id, new_count, **params):
    # required mandatories for create
    nodespec = {
        'flavor': params['flavor'],
        'az': params['availability_zone'],
        'count': new_count,
        'login': { 'sshKey': params['key_name'], },
        'rootVolume': {
            'volumeType': params['root_volume']['type'],
            'size': int(params['root_volume']['size']),
        },
    }

    # need at least one data volume
    nodespec['dataVolumes'] = []
    for vol in params['data_volumes']:
        nodespec['dataVolumes'].append({
            'volumeType': vol['type'],
            'size': int(vol['size']),
        })
    # add public ip varant structure
    if 'public_ip' in params and params['public_ip'] is not None:
        if 'ids' in params['public_ip']:
            nodespec['publicIP'] = {
               'ids': params['public_ip']['ids'],
               }
        else:
            nodespec['publicIP'] = {
                'count': params['public_ip']['count'],
                'floating_ip': {
                    'type': params['public_ip']['type'],
                    'bandwidth': {
                        'size': int(params['public_ip']['bandwidth']),
                        'sharetype': params['public_ip']['sharetype'],
                    }
                }
            }
    
    nodespec_response = cloud.cce2.create_cluster_node(
        cluster=cluster_id,
        metadata={ 'name': params['name'] },
        spec=nodespec )
    return nodespec_response


def _current_spec_nodes(cloud, cluster_id, **params):
    nodes = list( filter(lambda res: _match_spec(res, **params), 
        cloud.cce2.cluster_nodes(cluster_id) ))
    ids   = list( map(lambda res: res.id, nodes) )
    return nodes, ids


def _new_nodes(cloud, cluster_id, existing_ids, **params):    
    nodes = list( filter(lambda res: _match_spec(res, **params) and 
        res.id not in existing_ids, 
        cloud.cce2.cluster_nodes(cluster_id) ))
    return nodes


def main():
    argument_spec = openstack_full_argument_spec(
        state=dict(type='str', default='present',
                   choices=['absent', 'present']),
        cluster=dict(type='str', alias='cluster_id', required=True),
        name=dict(type='str'),
        flavor=dict(type='str'),
        availability_zone=dict(type='str', default="eu-de-01"),
        key_name=dict(type='str'),
        count=dict(type='int'),
        root_volume=dict(type='dict'),
        data_volumes=dict(type='list'),
        public_ip=dict(type='dict'),
    )

    # FIXME: define some more constraints like mutual exclusives
    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=False,
                           **module_kwargs)

    state = module.params['state']
    clustername_id = module.params['cluster']

    cloud = connect_from_ansible(module)
    try:
        # temporary fix for the fact that the new RDS service is not yet in catalog
        cloud.add_service( cce_service.CceService("ccev2.0", aliases=["cce2"]) )

        # search for cluster by name or id
        cluster = cloud.cce2.find_cluster(clustername_id)
        if cluster:
            if state == 'present':
                # filter existing nodes with given spec
                existing_nodes, existing_ids = _current_spec_nodes(
                    cloud, cluster.id, **module.params)
                new_count = int(module.params['count']) - len(existing_nodes)
                
                if new_count > 0:
                    _add_nodes(cloud, cluster.id, new_count, **module.params)                        
                    changed = True
                    if module.params['wait']:
                        new_nodes = _new_nodes(cloud, cluster.id, existing_ids, **module.params)
                        cloud.cce2.wait_for_status_nodes(cluster.id, new_nodes)
                    existing_nodes, existing_ids = _current_spec_nodes(
                        cloud, cluster.id, **module.params)

                elif new_count < 0:
                    nodes_to_delete = existing_nodes[new_count:]
                    if nodes_to_delete:
                        for node in nodes_to_delete:
                            cloud.cce2.delete_cluster_node(cluster.id, node)
                        changed = True
                        if module.params['wait']:
                            cloud.cce2.wait_for_delete_nodes(cluster.id, nodes_to_delete)
                        existing_nodes, existing_ids = _current_spec_nodes(
                            cloud, cluster.id, **module.params)
                else:
                    changed = False
                module.exit_json(changed=changed, ids=existing_ids, nodes=existing_nodes)
                         
            elif state == 'absent':
                nodes_to_delete = _filter_for_delete(cloud, cluster.id, **module.params)
                if nodes_to_delete:
                    for node in nodes_to_delete:
                        cloud.cce2.delete_cluster_node(cluster.id, node)
                    changed = True
                    if module.params['wait']:
                        cloud.cce2.wait_for_delete_nodes(cluster.id, nodes_to_delete)
                else:
                    changed = False
                module.exit_json(changed=changed)

        else:
            module.fail_json(msg=str("Cluster " + clustername_id + " not found"))

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
