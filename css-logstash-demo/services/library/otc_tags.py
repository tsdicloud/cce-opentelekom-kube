# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from opentelekom.vpc.v1 import subnet, vpc
from opentelekom.kms.v1 import cmk as _key
from opentelekom.nat.v2 import gateway as _gateway
from opentelekom.rds.v3 import instance as _rds_instance
from opentelekom.dms.v1 import queue as _queue
from opentelekom.css.v1 import cluster as _css_cluster

from openstack.block_storage.v3 import volume as _volume


class OtcTags:
    """ A helper class to centrally manage Open Telekom CLoud tasks -
        even for OPenstack resources (which do not have key-value tags) """

    @staticmethod
    def findResource(session, resource_type, name_or_id):
        """ Factory method to find a proper Resource given type and id """ 

class OtcOpenstackTagManager:
    