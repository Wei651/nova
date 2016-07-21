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
#
# version 1.0  7/9/2016  Serena Pan
#   First working version
# version 1.1  7/19/2016  Fei Yeh
#   Authorization Token/Passwords are read in from Neutron and Keystone instead of hard-coded

import time
from oslo_config import cfg
from oslo_log import log as logging
from oslo_serialization import jsonutils

from neutronclient.common import exceptions as neutron_client_exc
from neutronclient.v2_0 import client as clientv20

from ironic.common.i18n import _

neutron_opts = [
    cfg.IntOpt('url_timeout',
               default=30,
               help=_('Timeout value for connecting to neutron in seconds.')),
    cfg.IntOpt('retries',
               default=3,
               help=_('Client retries in the case of a failed request.')),
]

CONF = cfg.CONF
CONF.register_opts(neutron_opts, group='neutron')

LOG = logging.getLogger(__name__)

keystone_opts = [
    cfg.StrOpt('region_name',
               help=_('The region used for getting endpoints of OpenStack'
                      'services.')),
]

CONF.register_opts(keystone_opts, group='keystone')
CONF.import_group('keystone_authtoken', 'keystonemiddleware.auth_token')

def _build_client(token=None):
    """Utility function to create Neutron client."""

    params = {
        'timeout': CONF.neutron.url_timeout,
        'retries': CONF.neutron.retries,
        'insecure': CONF.keystone_authtoken.insecure,
        'ca_cert': CONF.keystone_authtoken.certfile,
    }

    if CONF.neutron.auth_strategy not in ['noauth', 'keystone']:
        raise exception.ConfigInvalid(_('Neutron auth_strategy should be '
                                        'either "noauth" or "keystone".'))

    if CONF.neutron.auth_strategy == 'noauth':
        params['endpoint_url'] = CONF.neutron.url
        params['auth_strategy'] = 'noauth'
    elif (CONF.neutron.auth_strategy == 'keystone' and
          token is None):
        params['endpoint_url'] = (CONF.neutron.url or
                                  keystone.get_service_url('neutron'))
        params['username'] = CONF.keystone_authtoken.admin_user
        params['tenant_name'] = CONF.keystone_authtoken.admin_tenant_name
        params['password'] = CONF.keystone_authtoken.admin_password
        params['auth_url'] = (CONF.keystone_authtoken.auth_uri or '')
        if CONF.keystone.region_name:
            params['region_name'] = CONF.keystone.region_name
    else:
        params['token'] = token
        params['endpoint_url'] = CONF.neutron.url
        params['auth_strategy'] = None

    return clientv20.Client(**params)

class NeutronDHCPApi():
    """API for communicating to neutron 2.x API."""
    #def update_realswport(self, port_id, sw_id, sw_port):
    def update_realswport(self, port_id, sw_id, sw_port):
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

