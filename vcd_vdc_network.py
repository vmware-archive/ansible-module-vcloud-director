# Copyright (c) 2018 Michal Taratuta <michalta@Softcat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


# from __future__ import (absolute_import, division, print_function)
# __metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: vcd_vdc_network
short_description: Ansible module to create/delete a network in vdc in vCloud Director.
version_added: "2.7"
description:
    - "Ansible module to create/delete a network in vdc in vCloud Director."
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
    org:
        description:
            - Organization name on vCloud Director to access i.e. System.
        type: str
    org_name:
        description:
            - Name of the organization the network belongs to.
        type: str
    api_version:
        description:
            - Pyvcloud API version, required as float i.e 31 => 31.0
        type: float
    verify_ssl_certs:
        description:
            - Whether to use secure connection to vCloud Director host.
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
    gateway_ip:
        description:
            - The IP for the new network required with Isolated network type.
        type: str
    netmask:
        description:
            - The netmask for the new network required with Isolated network
              type.
        type: str
    parent_network_name:
        description:
            - The name of the external network that the new network will be
              directly connected to.
        type: str
    guest_vlan_allowed:
        description:
            - True if Network allows guest VLAN tagging.
        type: bool
    sub_interface:
        description:
            - True if Network is connected to an Edge Gateway subinterface.
        type: bool
    distributed_interface:
        description:
            - True if Network is connected to a distributed logical router.
        type: bool
    retain_net_info_across_deployments:
        description:
            - Specifies whether the network resources such as IP/MAC of router
              will be retained across deployments. Default is false.
        type: bool
        default: false
    network_cidr:
        description:
            - The CIDR of the new newtork in format 10.20.99.1/24, at the
              moment used by Routed networks.
        type: str
    state:
        description:
            - State of the Gateway.
        type: string
        default: present
        choices: ['present','absent']
'''


EXAMPLES = '''
- name: create vdc network | Direct
  create_vdc_network:
    user: "{{vcd_user}}"
    password: "{{vcd_password}}"
    host: "{{vcd_host}}"
    api_version: "{{api_version}}"
    verify_ssl_certs: "{{verify_ssl_certs}}"
    org: "{{system_org}}"
    org_name: "{{customer_org}}"
    vdc_name: "{{vdc_name}}"
    gateway_name: "{{gateway_name}}"
    network_name: "my direct network"
    description: "directly connected network"
    parent_network_name: "CLOUDLAB EXTERNAL NETWORK"
    direct: True

- name: create vdc network | ROUTED
  vcd_vdc_network:
    user: "{{vcd_user}}"
    password: "{{vcd_password}}"
    host: "{{vcd_host}}"
    api_version: "{{api_version}}"
    verify_ssl_certs: "{{verify_ssl_certs}}"
    org: "{{system_org}}"
    org_name: "{{customer_org}}"
    vdc_name: "{{vdc_name}}"
    gateway_name: "{{gw_name}}"
    network_name: "my ROUTED network"
    description: "ROUTED network"
    parent_network_name: "CLOUDLAB EXTERNAL NETWORK"
    gateway_ip: "10.10.99.1"
    netmask: "255.255.255.0"
    primary_dns_ip: 1.1.1.1
    secondary_dns_ip: 2.2.2.2
    dns_suffix: routed.com
    ip_range_start: 10.10.99.2
    ip_range_end: 10.10.99.20
    state: "{{state}}"
    shared: True
    routed: True

- name: create vdc network | ISOLATED
  vcd_vdc_network:
    user: "{{vcd_user}}"
    password: "{{vcd_password}}"
    host: "{{vcd_host}}"
    api_version: "{{api_version}}"
    verify_ssl_certs: "{{verify_ssl_certs}}"
    org: "{{system_org}}"
    org_name: "{{customer_org}}"
    vdc_name: "{{vdc_name}}"
    gateway_name: "{{gw_name}}"
    network_name: "my ISOLATED network"
    description: "directly ISOLATED network"
    state: "{{state}}"
    network_cidr: 10.20.99.1/24
    primary_dns_ip: 8.8.8.8
    secondary_dns_ip: 9.9.9.9
    dns_suffix: bob.com
    ip_range_start: 10.10.10.2
    ip_range_end: 10.10.10.20
    dhcp_enabled: True
    default_lease_time: 500
    max_lease_time: 1000
    dhcp_ip_range_start: 10.10.10.30
    dhcp_ip_range_end: 10.10.10.60
    shared: True
    isolated: True
'''


RETURN = '''
msg: success/failure message corresponding to vdc state/operation
changed: true if resource has been changed else false
'''


from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.exceptions import EntityNotFoundException


VAPP_NETWORK_STATES = ['present', 'absent']


def vdc_gw_argument_spec():
    return dict(org_name=dict(type='str', required=True),
                vdc_name=dict(type='str', required=True),
                gateway_name=dict(type='str', required=True),
                network_name=dict(type='str', required=True),
                description=dict(type='str', required=False),
                parent_network_name=dict(type='str', required=False),
                shared=dict(type='bool', required=False, default=False),
                gateway_ip=dict(type='str', required=False),
                netmask=dict(type='str', required=False),
                network_cidr=dict(type='str', required=False),
                primary_dns_ip=dict(type='str', required=False),
                secondary_dns_ip=dict(type='str', required=False),
                dns_suffix=dict(type='str', required=False),
                ip_range_start=dict(type='str', required=False),
                ip_range_end=dict(type='str', required=False),
                dhcp_enabled=dict(type='bool', required=False, default=False),
                default_lease_time=dict(type='int', required=False),
                max_lease_time=dict(type='int', required=False),
                dhcp_ip_range_start=dict(type='str', required=False),
                dhcp_ip_range_end=dict(type='str', required=False),
                force=dict(type='bool', required=False, default=False),
                state=dict(choices=VAPP_NETWORK_STATES, required=False,
                           default='present'),
                direct=dict(type='bool', required=False),
                isolated=dict(type='bool', required=False),
                routed=dict(type='bool', required=False),
                guest_vlan_allowed=dict(type='bool', required=False),
                sub_interface=dict(type='bool', required=False),
                distributed_interface=dict(type='bool', required=False),
                retain_net_info_across_deployments=dict(type='bool',
                                                        required=False))


class VdcNet(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VdcNet, self).__init__(**kwargs)
        self.vdc_name = self.params.get('vdc_name')
        self.org_name = self.params.get('org_name')
        self.gateway_name = self.params.get('gateway_name')
        self.network_name = self.params.get('network_name')
        self.description = self.params.get('description')
        self.parent_network_name = self.params.get('parent_network_name')
        self.shared = self.params.get('shared')
        self.gateway_ip = self.params.get('gateway_ip')
        self.netmask = self.params.get('netmask')
        self.network_cidr = self.params.get('network_cidr')
        self.primary_dns_ip = self.params.get('primary_dns_ip')
        self.secondary_dns_ip = self.params.get('secondary_dns_ip')
        self.dns_suffix = self.params.get('dns_suffix')
        self.ip_range_start = self.params.get('ip_range_start')
        self.ip_range_end = self.params.get('ip_range_end')
        self.dhcp_enabled = self.params.get('dhcp_enabled')
        self.default_lease_time = self.params.get('default_lease_time')
        self.max_lease_time = self.params.get('max_lease_time')
        self.dhcp_ip_range_start = self.params.get('dhcp_ip_range_start')
        self.dhcp_ip_range_end = self.params.get('dhcp_ip_range_end')
        self.force = self.params.get('force')
        self.state = self.params.get('state')
        self.direct = self.params.get('direct')
        self.isolated = self.params.get('isolated')
        self.routed = self.params.get('routed')
        self.guest_vlan_allowed = self.params.get('guest_vlan_allowed')
        self.sub_interface = self.params.get('sub_interface')
        self.distributed_interface = self.params.get('distributed_interface')
        self.retain_net_info_across_deployments = self.params.get(
            'retain_net_info_across_deployments')

        org_resource = self.client.get_org_by_name(self.org_name)
        self.org = Org(self.client, resource=org_resource)
        vdc_resource = self.org.get_vdc(self.vdc_name)
        self.vdc = VDC(self.client, name=self.vdc_name, resource=vdc_resource)


    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            if self.direct:
                return self.create_direct_network()
            elif self.isolated:
                return self.create_isolated_network()
            elif self.routed:
                return self.create_routed_network()
            else:
                raise Exception("Bool 'direct', 'isolated' or 'routed' is missing")

        if state == "absent":
            return self.delete_network()


    def create_direct_network(self):
        response = dict()

        try:
            self.vdc.get_direct_orgvdc_network(self.network_name)

        except EntityNotFoundException:
            create = self.vdc.create_directly_connected_vdc_network(
                self.network_name,
                self.parent_network_name,
                description=self.description,
                is_shared=self.shared)

            self.execute_task(create.Tasks.Task[0])

            response['msg'] = 'Network {0} created'.format(self.network_name)
            response['changed'] = True

        else:
            response['warnings'] = 'Network {0} is already present.'.format(
                self.network_name)

        return response


    def create_isolated_network(self):
        response = dict()

        try:
            self.vdc.get_isolated_orgvdc_network(self.network_name)

        except EntityNotFoundException:
            create = self.vdc.create_isolated_vdc_network(
                self.network_name,
                self.gateway_ip,
                self.netmask,
                description=self.description,
                primary_dns_ip=self.primary_dns_ip,
                secondary_dns_ip=self.secondary_dns_ip,
                dns_suffix=self.dns_suffix,
                ip_range_start=self.ip_range_start,
                ip_range_end=self.ip_range_end,
                is_dhcp_enabled=self.dhcp_enabled,
                default_lease_time=self.default_lease_time,
                max_lease_time=self.max_lease_time,
                dhcp_ip_range_start=self.dhcp_ip_range_start,
                dhcp_ip_range_end=self.dhcp_ip_range_end,
                is_shared=self.shared)

            self.execute_task(create.Tasks.Task[0])

            response['msg'] = 'Network {0} created'.format(self.network_name)
            response['changed'] = True

        else:
            response['warnings'] = 'Network {0} is already present.'.format(
                self.network_name)

        return response


    def create_routed_network(self):
        response = dict()

        try:
            self.vdc.get_routed_orgvdc_network(self.network_name)

        except EntityNotFoundException:
            create = self.vdc.create_routed_vdc_network(
                self.network_name,
                self.gateway_name,
                self.network_cidr,
                description=self.description,
                primary_dns_ip=self.primary_dns_ip,
                secondary_dns_ip=self.secondary_dns_ip,
                dns_suffix=self.dns_suffix,
                ip_range_start=self.ip_range_start,
                ip_range_end=self.ip_range_end,
                is_shared=self.shared,
                guest_vlan_allowed=self.guest_vlan_allowed,
                sub_interface=self.sub_interface,
                distributed_interface=self.distributed_interface,
                retain_net_info_across_deployments=self.retain_net_info_across_deployments)

            self.execute_task(create.Tasks.Task[0])

            response['msg'] = 'Network {0} created'.format(self.network_name)
            response['changed'] = True

        else:
            response['warnings'] = 'Network {0} is already present.'.format(
                self.network_name)

        return response


    def delete_network(self):
        response = dict()

        try:
            if self.direct:
                self.vdc.get_direct_orgvdc_network(self.network_name)
            elif self.isolated:
                self.vdc.get_isolated_orgvdc_network(self.network_name)
            elif self.routed:
                self.vdc.get_routed_orgvdc_network(self.network_name)

        except EntityNotFoundException:
            response['warnings'] = 'Network {} is not present.'.format(
                self.network_name)

        else:
            if self.direct:
                delete = self.vdc.delete_direct_orgvdc_network(
                    self.network_name,
                    force=self.force)
            elif self.isolated:
                delete = self.vdc.delete_isolated_orgvdc_network(
                    self.network_name,
                    force=self.force)
            elif self.routed:
                delete = self.vdc.delete_routed_orgvdc_network(
                    self.network_name,
                    force=self.force)

            self.execute_task(delete)
            response['msg'] = 'Network {} has been deleted.'.format(
                self.network_name)
            response['changed'] = True

        return response


def main():
    argument_spec = vdc_gw_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = VdcNet(argument_spec=argument_spec, supports_check_mode=True)

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
