# Copyright © 2018 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause

# !/usr/bin/python


# from __future__ import (absolute_import, division, print_function)
# __metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: vcd_vdc_gateway
short_description: Ansible module to create/delete edge gateway in vdc in vCloud Director.
version_added: "2.7"
description:
    - "Ansible module to create/delete edge gateway in vdc in vCloud Director."
author:
    - Michal Taratuta <michalta@softcat.com>
options:
    user:
        description:
            - vCloud Director user name
        type: str
    password:
        description:
            - vCloud Director user password
        type: str
    host:
        description:
            - vCloud Director host address
        type: str
    org_name:
        description:
            - Name of the organization the Gateway belongs to.
        type: str
    org:
        description:
            - Organization name on vCloud Director to access i.e. System.
        type: str
    api_version:
        description:
            - Pyvcloud API version, required as float i.e 31 => 31.0
        type: float
    verify_ssl_certs:
        description:
            - whether to use secure connection to vCloud Director host.
        type: bool
    vdc_name:
        description:
            - The name of the vdc where GW is going to be created.
        required: true
        type: str
    description:
        description:
            - The description of the edge gateway
        type: str
    gateway_name:
        description:
            - The name of the new gateway.
        type: str
        required: true
        choices: ['AllocationVApp', 'AllocationPool', 'ReservationPool']
    external_networks:
        description:
            - list of external network's name to which gateway can connect.
        type: list
        required: true
    gateway_backing_config:
        description:
            - The size of the NSX Edge instance based on your performance
              requirements.
        type: str
        required: true
        choices: ['compact', 'full', 'full4', 'x-large']
    default_gateway:
        description:
            - Is this a default gateway
        type: bool
        default: false
    extnw_for_default_gw:
        description:
            - External network for default gateway.
        type: str
    default_gateway_ip:
        description:
            - Dafault gateway IP
        type: str
    default_gw_for_dns_relay:
        description:
            - Is this a default gateway for dns relay.
        type: bool
        default: false
    ha_enabled:
        description:
            - Is HA enabled
        type: bool
        default: false
    create_as_advanced_gw:
        description:
            - Maximum number of network objects that can be deployed in this
              vDC. Defaults to 0, which means no networks can be deployed
        type: bool
        default: false
    dr_enabled:
        description:
            - Is distributed routing enabled
        type: bool
        default: false
    configure_ip_settings:
        description:
            - Is ip settings configured
        type: bool
        default: false
    ext_net_to_participated_subnet_with_ip_settings:
        description:
            - External network to subnet ip with ip assigned in case of manual
              else Auto. Manual example {"CLOUDLAB EXTERNAL NETWORK": {
                                         "10.221.10.161/27": "10.221.10.170"}}
        type: dict
    sub_allocate_ip_pools:
        description:
            - Is sub allocate ip pools enabled.
        type: bool
        default: false
    ext_net_to_subnet_with_ip_range:
        description:
            - External network to sub allocated ip with ip ranges. Example:
              {"ext_net' : {'10.3.2.1/24' : [10.3.2.2-10.3.2.5,
                                             10.3.2.12-10.3.2.15]}}
        type: dict
    ext_net_to_rate_limit:
        description:
            - External network to rate limit.
              Example: {"CLOUDLAB EXTERNAL NETWORK": {"100": "100"}}
        type: dict
    flips_mode:
        description:
            - Is flip mode enabled.
        type: bool
        default: false
    state:
        description:
            - State of the Gateway.
        type: string
        default: present
        choices: ['present','absent']
'''


EXAMPLES = '''
- name: create GW with STATIC IP Address and Rate Limit
  vcd_vdc_gateway:
    user: "{{vcd_user}}"
    password: "{{vcd_password}}"
    host: "{{host}}"
    org_name: "{{customer_org}}"
    org: "{{org_name}}"
    api_version: "{{api_version}}"
    verify_ssl_certs: False
    vdc_name: "{{vdc_name}}"
    gateway_name: "module_test_3"
    description: "Created by Ansible module"
    external_networks:
      - "CLOUDLAB EXTERNAL NETWORK"
    gateway_backing_config: compact
    default_gateway: True
    extnw_for_default_gw: "CLOUDLAB EXTERNAL NETWORK"
    default_gateway_ip: 10.221.10.161
    default_gw_for_dns_relay: True
    ha_enabled: True
    create_as_advanced_gw: True
    dr_enabled: True
    configure_ip_settings: True
    ext_net_to_participated_subnet_with_ip_settings: {"CLOUDLAB EXTERNAL NETWORK": {"10.221.10.161/27": "10.221.10.170"}}
    ext_net_to_rate_limit: {"CLOUDLAB EXTERNAL NETWORK": {"100": "100"}}
    state: present
'''


RETURN = '''
msg: success/failure message corresponding to vdc state/operation
changed: true if resource has been changed else false
'''


from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.exceptions import EntityNotFoundException


VAPP_GW_BACKING_CONF = ['compact', 'full', 'full4', 'x-large']
VAPP_NETWORK_STATES = ['present', 'absent']


def vdc_gw_argument_spec():
    return dict(org_name=dict(type='str', required=False),
                vdc_name=dict(type='str', required=True),
                gateway_name=dict(type='str', required=True),
                description=dict(type='str', required=False),
                external_networks=dict(type='list', required=True),
                gateway_backing_config=dict(type='str', required=True,
                                            choices=VAPP_GW_BACKING_CONF),
                default_gateway=dict(type='bool', required=False,
                                     default=False),
                extnw_for_default_gw=dict(type='str', required=True),
                default_gateway_ip=dict(type='str', required=False),
                default_gw_for_dns_relay=dict(type='bool', required=False,
                                              default=False),
                ha_enabled=dict(type='bool', required=False, default=False),
                create_as_advanced_gw=dict(type='bool', required=False,
                                           default=False),
                dr_enabled=dict(type='bool', required=False, default=False),
                configure_ip_settings=dict(type='bool', required=False,
                                           default=False),
                ext_net_to_participated_subnet_with_ip_settings=dict(type='dict',
                                                                     required=False),
                sub_allocate_ip_pools=dict(type='bool', required=False,
                                           default=False),
                ext_net_to_subnet_with_ip_range=dict(type='dict',
                                                     required=False),
                ext_net_to_rate_limit=dict(type='dict', required=False),
                flips_mode=dict(type='bool', required=False, default=False),
                state=dict(choices=VAPP_NETWORK_STATES, required=False,
                           default='present'))


class VdcGW(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VdcGW, self).__init__(**kwargs)
        self.vdc_name = self.params.get('vdc_name')
        self.gateway_name = self.params.get('gateway_name')
        self.description = self.params.get('description')
        self.external_networks = self.params.get('external_networks')
        self.gateway_backing_config = self.params.get('gateway_backing_config')
        self.default_gateway = self.params.get('default_gateway')
        self.extnw_for_default_gw = self.params.get('extnw_for_default_gw')
        self.default_gateway_ip = self.params.get('default_gateway_ip')
        self.default_gw_for_dns_relay = self.params.get(
            'default_gw_for_dns_relay')
        self.ha_enabled = self.params.get('ha_enabled')
        self.create_as_advanced_gw = self.params.get('create_as_advanced_gw')
        self.dr_enabled = self.params.get('dr_enabled')
        self.configure_ip_settings = self.params.get('configure_ip_settings')
        self.ext_net_to_participated_subnet_with_ip_settings = self.params.get(
            'ext_net_to_participated_subnet_with_ip_settings')
        self.sub_allocate_ip_pools = self.params.get('sub_allocate_ip_pools')
        self.ext_net_to_subnet_with_ip_range = self.params.get(
            'ext_net_to_subnet_with_ip_range')
        self.ext_net_to_rate_limit = self.params.get('ext_net_to_rate_limit')
        self.flips_mode = self.params.get('flips_mode')
        self.org_name = self.params.get('org_name')

        org_resource = self.client.get_org_by_name(self.org_name)
        self.org = Org(self.client, resource=org_resource)
        vdc_resource = self.org.get_vdc(self.vdc_name)
        self.vdc = VDC(self.client, name=self.vdc_name, resource=vdc_resource)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.create_gw()

        if state == "absent":
            return self.delete_gw()

    def create_gw(self):
        response = dict()

        try:
            self.vdc.get_gateway(self.gateway_name)

        except EntityNotFoundException:
            create = self.vdc.create_gateway(
                name=self.gateway_name,
                external_networks=self.external_networks,
                gateway_backing_config=self.gateway_backing_config,
                desc=self.description,
                is_default_gateway=self.default_gateway,
                selected_extnw_for_default_gw=self.extnw_for_default_gw,
                default_gateway_ip=self.default_gateway_ip,
                is_default_gw_for_dns_relay_selected=self.default_gw_for_dns_relay,
                is_ha_enabled=self.ha_enabled,
                should_create_as_advanced=self.create_as_advanced_gw,
                is_dr_enabled=self.dr_enabled,
                is_ip_settings_configured=self.configure_ip_settings,
                ext_net_to_participated_subnet_with_ip_settings=self.ext_net_to_participated_subnet_with_ip_settings,
                is_sub_allocate_ip_pools_enabled=self.sub_allocate_ip_pools,
                ext_net_to_subnet_with_ip_range=self.ext_net_to_subnet_with_ip_range,
                ext_net_to_rate_limit=self.ext_net_to_rate_limit,
                is_flips_mode_enabled=self.flips_mode)

            self.execute_task(create.Tasks.Task[0])

            response['msg'] = 'Edge Gateway {0} created'.format(
                self.gateway_name)
            response['changed'] = True

        else:
            response['warnings'] = 'Edge Gateway {0} is already present.'.format(
                self.gateway_name)

        return response

    def delete_gw(self):
        response = dict()

        try:
            self.vdc.get_gateway(self.gateway_name)

        except EntityNotFoundException:
            response['warnings'] = 'Edge Gateway {0} is not present.'.format(
                self.gateway_name)

        else:
            delete = self.vdc.delete_gateway(self.gateway_name)
            self.execute_task(delete)
            response['changed'] = True

        return response


def main():
    argument_spec = vdc_gw_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = VdcGW(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if not module.params.get('state'):
            raise Exception('Please provide the state for the resource.')

        response = module.manage_states()
        module.exit_json(**response)

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)


if __name__ == '__main__':
    main()
