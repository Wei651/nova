#
# Copyright 2014 OpenStack Foundation
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import time
from oslo_serialization import jsonutils

from neutronclient.common import exceptions as neutron_client_exc
from neutronclient.v2_0 import client as clientv20

def get_sw_port (uuid ):
   #uuid="xxxxxxxx-xxxxxxxxxxxxxxx-xxxxxxxxx" is the device vif uuid of neutron
   sw_port=""
   f = open("/etc/nova/port_list","r")
   lines = f.readlines()
   f.close()
   for i in lines:
      if i.rstrip('\r\n').split(',')[1] == uuid:
         return i.rstrip('\r\n').split(',')[0]

   fw = open('/etc/nova/port_list', 'w')
   for i in lines:
      ne_portuuid = i.rstrip('\r\n').split(',')[1]
      if ne_portuuid == '' and sw_port == "":
         #print i.rstrip('\r\n').split(',')[0]
         sw_port=i.rstrip('\r\n').split(',')[0]
         fw.write(i.rstrip('\r\n').split(',')[0]+","+uuid+"\n")
      else:
         fw.write(i)
   fw.close()
   return sw_port

def _build_client():
    params = {
        'timeout': 200,
        'retries': 10,
    }

    params['username'] = 'nova'
    params['tenant_name'] = "services"
    params['password'] = "cham2icair"
    params['auth_url'] = 'http://chic1:5000/v2.0'
    params['token'] = 'cham2icair'
    params['endpoint_url'] = 'http://chic1:9696'
    params['auth_strategy'] = 'keystone'

    return clientv20.Client(**params)

# This part need to be modified.

class NeutronDHCPApi():
    """API for communicating to neutron 2.x API."""
    #def update_realswport(self, port_id, sw_id, sw_port):
    def update_realswport(self, port_id, sw_id, sw_port):
        #
        #sw_port=get_sw_port(instance)
        #
        body = {'port': {}}
        body['port'].update({'binding:profile':jsonutils.loads('{"local_link_information": [{"port_id": "'+ sw_port +'", "switch_id": "'+sw_id+'"}]}')})
        #port_req_body = {'port': {"binding:profile":{"local_link_information":[{"switch_id":sw_id,"port_id":sw_port}]}}}
        #port_path="/ports/%s" % port_id
        try:
            #_build_client().update_port(port_id, port_req_body)
            if not sw_port == "":
               _build_client().update_port(port_id, body)
            #_build_client().update_port(port_path, body)
        except neutron_client_exc.NeutronClientException:
            print port_id
            #LOG.exception(_LE("Failed to update Neutron port %s."), port_id)
            #raise exception.FailedToUpdateDHCPOptOnPort(port_id=port_id)

