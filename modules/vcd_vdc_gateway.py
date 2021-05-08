# Copyright © 2018 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause OR GPL-3.0-only

# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
module: vcd_vdc_gateway
short_description: Manage edge gateway's states/operations in vCloud Director
version_added: "2.7"
description:
    - Manage edge gateway's states/operations in vCloud Director
author:
    - Michal Taratuta <michalta@softcat.com>
    - Mukul Taneja  <mtaneja@vmware.com>
options:
    user:
        description:
            - vCloud Director user name
        type: str
        required: false
    password:
        description:
            - vCloud Director user password
        type: str
        required: false
    host:
        description:
            - vCloud Director host address
        type: str
        required: false
    org:
        description:
            - Organization name on vCloud Director to access i.e. System.
        type: str
        required: false
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
            - The name of the vdc where Gateway is going to be created.
        required: false
        type: str
    org_name:
        description:
            - target org name for gateway
        type: str
        required: false
    description:
        description:
            - The description of the edge gateway
        type: str
        required: false
    gateway_name:
        description:
            - The name of the new gateway.
        type: str
        required: true
    new_gateway_name:
        description:
            - The updated name of the existing gateway.
        type: str
        required: false
    external_networks:
        description:
            - list of external network's name to which gateway can connect.
        type: list
        required: false
    gateway_backing_config:
        description:
            - The size of the NSX Edge instance based on your performance
                requirements.
        type: str
        required: false
        choices: ['compact', 'full', 'full4', 'x-large']
    edge_gateway_type:
        description:
            - edge gateway type
        type: str
        required: false
        choices: ['NSXV_BACKED', 'NSXT_BACKED', 'NSXT_IMPORTED']
    default_gateway:
        description:
            - should the new gateway be configured as the default gateway.
        type: bool
        default: false
        required: false
    extnw_for_default_gw:
        description:
            - external network for default gateway.
        type: str
        required: false
    default_gateway_ip:
        description:
            - dafault gateway IP
        type: str
        required: false
    default_gw_for_dns_relay:
        description:
            - should this default gateway use for dns relay.
        type: bool
        default: false
        required: false
    ha_enabled:
        description:
            - Is HA enabled
        type: bool
        default: false
        required: false
    create_as_advanced_gw:
        description:
            - create as advanced gateway
        type: bool
        default: false
        required: false
    dr_enabled:
        description:
            - Is distributed routing enabled
        type: bool
        default: false
        required: false
    configure_ip_settings:
        description:
            - Is ip settings configured
        type: bool
        default: false
        required: false
    ext_net_to_participated_subnet_with_ip_settings:
        description:
            - External network to subnet ip with ip assigned in case of manual
                 else Auto.
        type: dict
        required: false
    sub_allocate_ip_pools:
        description:
            - Is sub allocate ip pools enabled.
        type: bool
        default: false
        required: false
    ext_net_subnet_allocated_ip_pool:
        description:
            - External network to sub allocated ip with ip ranges.
        type: dict
        required: false
    ext_net_to_rate_limit:
        description:
            - External network to rate limit.
        required: false
    flips_mode:
        description:
            - Is flip mode enabled.
        type: bool
        default: false
    state:
        description:
            - State of the Gateway.
        type: string
        required: false
        choices: ['present','absent', 'update']
    operation:
        description:
            - Operation performed on the Gateway.
        type: string
        required: false
        choices: ['update_ip_pool', 'add_network', 'remove_network']
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
    ext_net_subnet_allocated_ip_pool: {
        "network_name": "10.221.10.170-10.221.10.171"
    }
    ext_net_to_participated_subnet_with_ip_settings: {
        "CLOUDLAB EXTERNAL NETWORK": {
            "10.221.10.161/27": "10.221.10.170"
        }
    }
    ext_net_to_rate_limit: {
        "CLOUDLAB EXTERNAL NETWORK": {
            "100": "100"
        }
    }
    state: present
'''


RETURN = '''
msg: success/failure message corresponding to edge gateway state
changed: true if resource has been changed else false
'''


from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.gateway import Gateway
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import BadRequestException, EntityNotFoundException


EDGE_GATEWAY_STATES = ['present', 'update', 'absent']
EDGE_GATEWAY_OPERATIONS = ['update_ip_pool', 'add_network', 'remove_network']
EDGE_GW_TYPE = ['NSXV_BACKED', 'NSXT_BACKED', 'NSXT_IMPORTED']
EDGE_GW_BACKING_CONF = ['compact', 'full', 'full4', 'x-large']


def vdc_gw_argument_spec():
    return dict(
        org_name=dict(type='str', required=True),
        vdc_name=dict(type='str', required=True),
        gateway_name=dict(type='str', required=True),
        new_gateway_name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        external_networks=dict(type='list', required=False),
        default_gateway=dict(type='bool', required=False, default=False),
        extnw_for_default_gw=dict(type='str', required=False),
        default_gateway_ip=dict(type='str', required=False),
        ha_enabled=dict(type='bool', required=False, default=False),
        create_as_advanced_gw=dict(type='bool', required=False, default=False),
        dr_enabled=dict(type='bool', required=False, default=False),
        configure_ip_settings=dict(type='bool', required=False, default=False),
        ext_net_subnet_allocated_ip_pool=dict(type='dict', required=False),
        sub_allocate_ip_pools=dict(type='bool', required=False, default=False),
        ext_net_to_subnet_with_ip_range=dict(type='dict', required=False),
        ext_net_to_rate_limit=dict(type='dict', required=False),
        flips_mode=dict(type='bool', required=False, default=False),
        default_gw_for_dns_relay=dict(
            type='bool', required=False, default=False),
        ext_net_to_participated_subnet_with_ip_settings=dict(
            type='dict', required=False),
        edge_gateway_type=dict(
            type='str', required=False, choices=EDGE_GW_TYPE),
        gateway_backing_config=dict(
            type='str', required=False, choices=EDGE_GW_BACKING_CONF),
        state=dict(choices=EDGE_GATEWAY_STATES, required=False),
        operation=dict(choices=EDGE_GATEWAY_OPERATIONS, required=False)
    )


class VdcGW(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VdcGW, self).__init__(**kwargs)
        self.vdc_name = self.params.get('vdc_name')
        self.org = self.get_org()
        vdc_resource = self.org.get_vdc(self.vdc_name)
        self.vdc = VDC(self.client, name=self.vdc_name, resource=vdc_resource)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.create_gw()

        if state == "update":
            return self.update_gw()

        if state == "absent":
            return self.delete_gw()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "update_ip_pool":
            return self.update_sub_allocated_ip_pools()

        if operation == "add_network":
            return self.add_network()

        if operation == "remove_network":
            return self.remove_network()

    def get_org(self):
        org_name = self.params.get('org_name')
        org_resource = self.client.get_org()
        if org_name:
            org_resource = self.client.get_org_by_name(org_name)

        return Org(self.client, resource=org_resource)

    def get_gateway(self, gateway_name):
        gateway = self.vdc.get_gateway(gateway_name)
        if gateway is not None:
            for key, value in gateway.items():
                if key == "href":
                    return Gateway(self.client, name=gateway_name, href=value)

        msg = "Edge gateway {0} is not present"
        raise EntityNotFoundException(msg.format(gateway_name))

    def create_gw(self):
        api_version = self.client.get_api_version()
        if api_version == "30.0":
            return self.create_gateway_api_version_30()

        if api_version == "31.0":
            return self.create_gateway_api_version_31()

        if api_version == "32.0":
            return self.create_gateway_api_version_32()

    def create_gateway_api_version_30(self):
        response = dict()
        response['changed'] = False
        gateway_name = self.params.get('gateway_name')
        description = self.params.get('description')
        external_networks = self.params.get('external_networks')
        gateway_backing_config = self.params.get('gateway_backing_config')
        default_gateway = self.params.get('default_gateway')
        extnw_for_default_gw = self.params.get('extnw_for_default_gw')
        default_gateway_ip = self.params.get('default_gateway_ip')
        default_gw_for_dns_relay = self.params.get('default_gw_for_dns_relay')
        ha_enabled = self.params.get('ha_enabled')
        create_as_advanced_gw = self.params.get('create_as_advanced_gw')
        dr_enabled = self.params.get('dr_enabled')
        configure_ip_settings = self.params.get('configure_ip_settings')
        sub_allocate_ip_pools = self.params.get('sub_allocate_ip_pools')
        ext_net_to_rate_limit = self.params.get('ext_net_to_rate_limit')
        ext_net_to_subnet_with_ip_range = self.params.get(
            'ext_net_to_subnet_with_ip_range')
        ext_net_to_participated_subnet_with_ip_settings = self.params.get(
            'ext_net_to_participated_subnet_with_ip_settings')

        try:
            self.get_gateway(gateway_name)
        except EntityNotFoundException:
            create_task = self.vdc.create_gateway_api_version_30(
                name=gateway_name,
                external_networks=external_networks,
                gateway_backing_config=gateway_backing_config,
                desc=description,
                is_default_gateway=default_gateway,
                selected_extnw_for_default_gw=extnw_for_default_gw,
                default_gateway_ip=default_gateway_ip,
                is_default_gw_for_dns_relay_selected=default_gw_for_dns_relay,
                is_ha_enabled=ha_enabled,
                should_create_as_advanced=create_as_advanced_gw,
                is_dr_enabled=dr_enabled,
                is_ip_settings_configured=configure_ip_settings,
                ext_net_to_participated_subnet_with_ip_settings=ext_net_to_participated_subnet_with_ip_settings,
                is_sub_allocate_ip_pools_enabled=sub_allocate_ip_pools,
                ext_net_to_subnet_with_ip_range=ext_net_to_subnet_with_ip_range,
                ext_net_to_rate_limit=ext_net_to_rate_limit)

            self.execute_task(create_task.Tasks.Task[0])
            msg = "Edge Gateway {0} has been created"
            response['msg'] = msg.format(gateway_name)
            response['changed'] = True
        else:
            msg = "Edge Gateway {0} is already present"
            response['warnings'] = msg.format(gateway_name)

        return response

    def create_gateway_api_version_31(self):
        response = dict()
        response['changed'] = False
        gateway_name = self.params.get('gateway_name')
        description = self.params.get('description')
        external_networks = self.params.get('external_networks')
        gateway_backing_config = self.params.get('gateway_backing_config')
        default_gateway = self.params.get('default_gateway')
        extnw_for_default_gw = self.params.get('extnw_for_default_gw')
        default_gateway_ip = self.params.get('default_gateway_ip')
        default_gw_for_dns_relay = self.params.get('default_gw_for_dns_relay')
        ha_enabled = self.params.get('ha_enabled')
        create_as_advanced_gw = self.params.get('create_as_advanced_gw')
        dr_enabled = self.params.get('dr_enabled')
        configure_ip_settings = self.params.get('configure_ip_settings')
        sub_allocate_ip_pools = self.params.get('sub_allocate_ip_pools')
        ext_net_to_rate_limit = self.params.get('ext_net_to_rate_limit')
        flips_mode = self.params.get('flips_mode')
        ext_net_to_subnet_with_ip_range = self.params.get(
            'ext_net_to_subnet_with_ip_range')
        ext_net_to_participated_subnet_with_ip_settings = self.params.get(
            'ext_net_to_participated_subnet_with_ip_settings')

        try:
            self.get_gateway(gateway_name)
        except EntityNotFoundException:
            create_task = self.vdc.create_gateway_api_version_31(
                name=gateway_name,
                external_networks=external_networks,
                gateway_backing_config=gateway_backing_config,
                desc=description,
                is_default_gateway=default_gateway,
                selected_extnw_for_default_gw=extnw_for_default_gw,
                default_gateway_ip=default_gateway_ip,
                is_default_gw_for_dns_relay_selected=default_gw_for_dns_relay,
                is_ha_enabled=ha_enabled,
                should_create_as_advanced=create_as_advanced_gw,
                is_dr_enabled=dr_enabled,
                is_ip_settings_configured=configure_ip_settings,
                ext_net_to_participated_subnet_with_ip_settings=ext_net_to_participated_subnet_with_ip_settings,
                is_sub_allocate_ip_pools_enabled=sub_allocate_ip_pools,
                ext_net_to_subnet_with_ip_range=ext_net_to_subnet_with_ip_range,
                ext_net_to_rate_limit=ext_net_to_rate_limit,
                is_flips_mode_enabled=flips_mode)

            self.execute_task(create_task.Tasks.Task[0])
            msg = "Edge Gateway {0} has been created"
            response['msg'] = msg.format(gateway_name)
            response['changed'] = True
        else:
            msg = "Edge Gateway {0} is already present"
            response['warnings'] = msg.format(gateway_name)

        return response

    def create_gateway_api_version_32(self):
        response = dict()
        response['changed'] = False
        gateway_name = self.params.get('gateway_name')
        description = self.params.get('description')
        external_networks = self.params.get('external_networks')
        gateway_backing_config = self.params.get('gateway_backing_config')
        default_gateway = self.params.get('default_gateway')
        extnw_for_default_gw = self.params.get('extnw_for_default_gw')
        default_gateway_ip = self.params.get('default_gateway_ip')
        default_gw_for_dns_relay = self.params.get('default_gw_for_dns_relay')
        ha_enabled = self.params.get('ha_enabled')
        create_as_advanced_gw = self.params.get('create_as_advanced_gw')
        dr_enabled = self.params.get('dr_enabled')
        configure_ip_settings = self.params.get('configure_ip_settings')
        sub_allocate_ip_pools = self.params.get('sub_allocate_ip_pools')
        ext_net_to_rate_limit = self.params.get('ext_net_to_rate_limit')
        edge_gateway_type = self.params.get('edge_gateway_type')
        flips_mode = self.params.get('flips_mode')
        ext_net_to_subnet_with_ip_range = self.params.get(
            'ext_net_to_subnet_with_ip_range')
        ext_net_to_participated_subnet_with_ip_settings = self.params.get(
            'ext_net_to_participated_subnet_with_ip_settings')

        try:
            self.get_gateway(gateway_name)
        except EntityNotFoundException:
            create_task = self.vdc.create_gateway_api_version_32(
                name=gateway_name,
                external_networks=external_networks,
                gateway_backing_config=gateway_backing_config,
                desc=description,
                is_default_gateway=default_gateway,
                selected_extnw_for_default_gw=extnw_for_default_gw,
                default_gateway_ip=default_gateway_ip,
                is_default_gw_for_dns_relay_selected=default_gw_for_dns_relay,
                is_ha_enabled=ha_enabled,
                should_create_as_advanced=create_as_advanced_gw,
                is_dr_enabled=dr_enabled,
                is_ip_settings_configured=configure_ip_settings,
                ext_net_to_participated_subnet_with_ip_settings=ext_net_to_participated_subnet_with_ip_settings,
                is_sub_allocate_ip_pools_enabled=sub_allocate_ip_pools,
                ext_net_to_subnet_with_ip_range=ext_net_to_subnet_with_ip_range,
                ext_net_to_rate_limit=ext_net_to_rate_limit,
                is_flips_mode_enabled=flips_mode,
                edgeGatewayType=edge_gateway_type)

            self.execute_task(create_task.Tasks.Task[0])
            msg = "Edge Gateway {0} has been created"
            response['msg'] = msg.format(gateway_name)
            response['changed'] = True
        else:
            msg = "Edge Gateway {0} is already present"
            response['warnings'] = msg.format(gateway_name)

        return response

    def update_gw(self):
        response = dict()
        response['changed'] = False
        gateway_name = self.params.get('gateway_name')
        new_gateway_name = self.params.get('new_gateway_name')
        description = self.params.get('description')
        ha_enabled = self.params.get('ha_enabled')

        try:
            gateway = self.get_gateway(gateway_name)
        except EntityNotFoundException as ex:
            response['warnings'] = ex
        else:
            update_task = gateway.edit_gateway(
                newname=new_gateway_name, desc=description, ha=ha_enabled)
            self.execute_task(update_task)
            msg = "Edge Gateway {0} has been updated with {1}"
            response['msg'] = msg.format(gateway_name, new_gateway_name)
            response['changed'] = True

        return response

    def delete_gw(self):
        response = dict()
        response['changed'] = False
        gateway_name = self.params.get('gateway_name')

        try:
            self.get_gateway(gateway_name)
        except EntityNotFoundException as ex:
            response['warnings'] = ex
        else:
            delete_task = self.vdc.delete_gateway(gateway_name)
            self.execute_task(delete_task)
            msg = "Edge Gateway {0} has been deleted"
            response['msg'] = msg.format(gateway_name)
            response['changed'] = True

        return response

    def _get_subnet_participation(self, gw_resource, network):
        for gateway_inf in \
                gw_resource.Configuration.GatewayInterfaces.GatewayInterface:
            if gateway_inf.Name == network:
                return gateway_inf.SubnetParticipation

        return None

    def update_sub_allocated_ip_pools(self):
        response = dict()
        response['changed'] = False
        gateway_name = self.params.get('gateway_name')

        try:
            gateway = self.get_gateway(gateway_name)
        except EntityNotFoundException as ex:
            response['warnings'] = ex
        else:
            ip_pool = self.params.get('ext_net_subnet_allocated_ip_pool')
            for network, new_ip_range in ip_pool.items():
                subnet_participation = self._get_subnet_participation(gateway.get_resource(), network)
                if subnet_participation is None:
                    msg = "No subnet ip pools are attached with network {0}"
                    raise Exception(msg.format(network))

                ip_ranges = gateway.get_sub_allocate_ip_ranges_element(subnet_participation)
                old_ip_range = "{0}-{1}".format(ip_ranges.IpRange.StartAddress, ip_ranges.IpRange.EndAddress)
                update_task = gateway.edit_sub_allocated_ip_pools(network, old_ip_range, new_ip_range)
                self.execute_task(update_task)
            msg = "Ip Pools have been updated on edge gatway {0}"
            response['msg'] = msg.format(gateway_name)
            response['changed'] = True

        return response

    def add_network(self):
        response = dict()
        response['changed'] = False
        gateway_name = self.params.get('gateway_name')

        try:
            gateway = self.get_gateway(gateway_name)
        except EntityNotFoundException as ex:
            response['warnings'] = ex
        else:
            network_settings = self.params.get('ext_net_to_participated_subnet_with_ip_settings')
            networks_to_attach = network_settings.keys()
            attached_networks = gateway.list_external_network_ip_allocations().keys()
            networks = list()
            for network in networks_to_attach:
                if network not in attached_networks:
                    networks.append(network)
                    for ip_settings in network_settings.values():
                        for subnet, ip in ip_settings.items():
                            add_network_task = gateway.add_external_network(network, [(subnet, ip)])
                            self.execute_task(add_network_task)
            if len(networks) == 0:
                networks = list(networks_to_attach)
                msg = "Networks {0} are already attached to edge gatway {1}"
            else:
                msg = "Networks {0} are added to edge gatway {1}"
            response['msg'] = msg.format(networks, gateway_name)
            response['changed'] = True

        return response

    def remove_network(self):
        response = dict()
        response['changed'] = False
        gateway_name = self.params.get('gateway_name')

        try:
            gateway = self.get_gateway(gateway_name)
        except EntityNotFoundException as ex:
            response['warnings'] = ex
        else:
            external_networks = self.params.get('external_networks')
            for network in external_networks:
                remove_network_task = gateway.remove_external_network(network)
                self.execute_task(remove_network_task)
            msg = "Networks {0} have been removed from edge gatway {1}"
            response['msg'] = msg.format(external_networks, gateway_name)
            response['changed'] = True

        return response


def main():
    argument_spec = vdc_gw_argument_spec()
    response = dict(msg=dict(type='str'))
    module = VdcGW(argument_spec=argument_spec, supports_check_mode=True)
    try:
        if module.check_mode:
            response = dict()
            response['changed'] = False
            response['msg'] = "skipped, running in check mode"
            response['skipped'] = True
        elif module.params.get('state'):
            response = module.manage_states()
        elif module.params.get('operation'):
            response = module.manage_operations()
        else:
            raise Exception('Please provide state/operation for resource')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
