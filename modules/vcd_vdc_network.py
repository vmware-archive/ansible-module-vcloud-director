# Copyright © 2018 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause OR GPL-3.0-only

# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
module: vcd_vdc_network
short_description: Manage VDC Network's states/operations in vCloud Director
version_added: "2.7"
description:
    -  Manage VDC Network's states/operations in vCloud Director
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
    api_version:
        description:
            - Pyvcloud API version, required as float i.e 31 => 31.0
        type: float
    verify_ssl_certs:
        description:
            - Whether to use secure connection to vCloud Director host.
        type: bool
    org_name:
        description:
            - target org name
            - required for service providers to create resources in other orgs
            - default value is module level / environment level org
        required: false
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
    vdc_name: "{{vdc_name}}"
    network_name: "my direct network"
    description: "directly connected network"
    parent_network_name: "CLOUDLAB EXTERNAL NETWORK"
    shared: True
    direct: True
    state: "{{state}}"

- name: create vdc network | ROUTED
  vcd_vdc_network:
    user: "{{vcd_user}}"
    password: "{{vcd_password}}"
    host: "{{vcd_host}}"
    api_version: "{{api_version}}"
    verify_ssl_certs: "{{verify_ssl_certs}}"
    org: "{{system_org}}"
    vdc_name: "{{vdc_name}}"
    gateway_name: "{{gw_name}}"
    network_name: "my ROUTED network"
    description: "ROUTED network"
    parent_network_name: "CLOUDLAB EXTERNAL NETWORK"
    primary_dns_ip: 1.1.1.1
    network_cidr: 10.20.99.1/24
    secondary_dns_ip: 2.2.2.2
    dns_suffix: routed.com
    ip_range_start: 10.10.99.2
    ip_range_end: 10.10.99.20
    shared: True
    routed: True
    state: "{{state}}"

- name: create vdc network | ISOLATED
  vcd_vdc_network:
    user: "{{vcd_user}}"
    password: "{{vcd_password}}"
    host: "{{vcd_host}}"
    api_version: "{{api_version}}"
    verify_ssl_certs: "{{verify_ssl_certs}}"
    org: "{{system_org}}"
    vdc_name: "{{vdc_name}}"
    network_name: "my ISOLATED network"
    description: "directly ISOLATED network"
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
    state: "{{state}}"
'''


RETURN = '''
msg: success/failure message corresponding to vdc state/operation
changed: true if resource has been changed else false
'''


from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException


ORG_VDC_NETWORK_STATES = ['present', 'absent']


def org_vdc_network_argument_spec():
    return dict(
        vdc_name=dict(type='str', required=True),
        network_name=dict(type='str', required=True),
        description=dict(type='str', required=False, default=None),
        gateway_name=dict(type='str', required=False),
        parent_network_name=dict(type='str', required=False),
        shared=dict(type='bool', required=False, default=False),
        network_cidr=dict(type='str', required=False),
        primary_dns_ip=dict(type='str', required=False, default=None),
        secondary_dns_ip=dict(type='str', required=False, default=None),
        dns_suffix=dict(type='str', required=False, default=None),
        ip_range_start=dict(type='str', required=False, default=None),
        ip_range_end=dict(type='str', required=False, default=None),
        dhcp_enabled=dict(type='bool', required=False, default=False),
        default_lease_time=dict(type='int', required=False, default=None),
        max_lease_time=dict(type='int', required=False, default=None),
        dhcp_ip_range_start=dict(type='str', required=False, default=None),
        dhcp_ip_range_end=dict(type='str', required=False, default=None),
        force=dict(type='bool', required=False, default=False),
        direct=dict(type='bool', required=False, default=None),
        isolated=dict(type='bool', required=False, default=None),
        routed=dict(type='bool', required=False, default=None),
        guest_vlan_allowed=dict(type='bool', required=False),
        sub_interface=dict(type='bool', required=False),
        distributed_interface=dict(type='bool', required=False),
        retain_net_info_across_deployments=dict(type='bool', required=False),
        org_name=dict(type='str', required=False, default=None),
        state=dict(choices=ORG_VDC_NETWORK_STATES, required=True)
    )


class OrgVdcNetwork(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(OrgVdcNetwork, self).__init__(**kwargs)
        self.vdc_name = self.params.get('vdc_name')
        self.org = self.get_org()
        vdc_resource = self.org.get_vdc(self.vdc_name)
        self.vdc = VDC(self.client, name=self.vdc_name, resource=vdc_resource)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.create_org_vdc_network()

        if state == "absent":
            return self.delete_org_vdc_network()

    def get_org(self):
        org_name = self.params.get('org_name')
        org_resource = self.client.get_org()
        if org_name:
            org_resource = self.client.get_org_by_name(org_name)

        return Org(self.client, resource=org_resource)

    def create_org_vdc_network(self):
        direct = self.params.get('direct')
        isolated = self.params.get('isolated')
        routed = self.params.get('routed')

        if direct:
            return self.create_org_vdc_direct_network()
        elif isolated:
            return self.create_org_vdc_isolated_network()
        elif routed:
            return self.create_org_vdc_routed_network()

        raise ValueError("Bool 'direct', 'isolated' or 'routed' is missing")

    def create_org_vdc_direct_network(self):
        response = dict()
        response['changed'] = False
        network_name = self.params.get('network_name')
        parent_network_name = self.params.get('parent_network_name')
        description = self.params.get('description')
        shared = self.params.get('shared')

        try:
            self.vdc.get_direct_orgvdc_network(network_name)
        except EntityNotFoundException:
            create_task = self.vdc.create_directly_connected_vdc_network(
                network_name, parent_network_name, description=description,
                is_shared=shared)
            self.execute_task(create_task.Tasks.Task[0])
            msg = 'Org VDC Direct Network {0} has been created'
            response['msg'] = msg.format(network_name)
            response['changed'] = True
        else:
            msg = 'Org VDC Direct Network {0} is already present'
            response['warnings'] = msg.format(network_name)

        return response

    def create_org_vdc_isolated_network(self):
        response = dict()
        response['changed'] = False
        network_name = self.params.get('network_name')
        network_cidr = self.params.get('network_cidr')
        description = self.params.get('description')
        shared = self.params.get('shared')
        primary_dns_ip = self.params.get('primary_dns_ip')
        secondary_dns_ip = self.params.get('secondary_dns_ip')
        dns_suffix = self.params.get('dns_suffix')
        ip_range_start = self.params.get('ip_range_start')
        ip_range_end = self.params.get('ip_range_end')
        dhcp_enabled = self.params.get('dhcp_enabled')
        default_lease_time = self.params.get('default_lease_time')
        max_lease_time = self.params.get('max_lease_time')
        dhcp_ip_range_start = self.params.get('dhcp_ip_range_start')
        dhcp_ip_range_end = self.params.get('dhcp_ip_range_end')

        try:
            self.vdc.get_isolated_orgvdc_network(network_name)
        except EntityNotFoundException:
            create_task = self.vdc.create_isolated_vdc_network(
                network_name, network_cidr, description=description,
                primary_dns_ip=primary_dns_ip,
                secondary_dns_ip=secondary_dns_ip,
                dns_suffix=dns_suffix, ip_range_start=ip_range_start,
                ip_range_end=ip_range_end, is_dhcp_enabled=dhcp_enabled,
                default_lease_time=default_lease_time,
                max_lease_time=max_lease_time,
                dhcp_ip_range_start=dhcp_ip_range_start,
                dhcp_ip_range_end=dhcp_ip_range_end, is_shared=shared)
            self.execute_task(create_task.Tasks.Task[0])
            msg = 'Org VDC Isolated Network {0} has been created'
            response['msg'] = msg.format(network_name)
            response['changed'] = True

        else:
            msg = 'Org VDC Isolated Network {0} is already present'
            response['warnings'] = msg.format(network_name)

        return response

    def create_org_vdc_routed_network(self):
        response = dict()
        response['changed'] = False
        network_name = self.params.get('network_name')
        gateway_name = self.params.get('gateway_name')
        network_cidr = self.params.get('network_cidr')
        description = self.params.get('description')
        shared = self.params.get('shared')
        primary_dns_ip = self.params.get('primary_dns_ip')
        secondary_dns_ip = self.params.get('secondary_dns_ip')
        dns_suffix = self.params.get('dns_suffix')
        ip_range_start = self.params.get('ip_range_start')
        ip_range_end = self.params.get('ip_range_end')
        guest_vlan_allowed = self.params.get('guest_vlan_allowed')
        sub_interface = self.params.get('sub_interface')
        distributed_interface = self.params.get('distributed_interface')
        retain_net_info_across_deployments = self.params.get(
            'retain_net_info_across_deployments')

        try:
            self.vdc.get_routed_orgvdc_network(network_name)
        except EntityNotFoundException:
            create_task = self.vdc.create_routed_vdc_network(
                network_name, gateway_name, network_cidr,
                description=description, primary_dns_ip=primary_dns_ip,
                secondary_dns_ip=secondary_dns_ip, dns_suffix=dns_suffix,
                ip_range_start=ip_range_start, ip_range_end=ip_range_end,
                is_shared=shared, guest_vlan_allowed=guest_vlan_allowed,
                sub_interface=sub_interface,
                distributed_interface=distributed_interface,
                retain_net_info_across_deployments=retain_net_info_across_deployments)
            self.execute_task(create_task.Tasks.Task[0])
            msg = 'Org VDC Routed Network {0} has been created'
            response['msg'] = msg.format(network_name)
            response['changed'] = True

        else:
            msg = 'Org VDC Routed Network {0} is already present'
            response['warnings'] = msg.format(network_name)

        return response

    def delete_org_vdc_network(self):
        response = dict()
        response['changed'] = False
        direct = self.params.get('direct')
        isolated = self.params.get('isolated')
        routed = self.params.get('routed')

        if direct:
            return self.delete_org_vdc_direct_network()

        if isolated:
            return self.delete_org_vdc_isolated_network()

        if routed:
            return self.delete_org_vdc_routed_network()

        raise ValueError("Bool 'direct', 'isolated' or 'routed' is missing")

    def delete_org_vdc_direct_network(self):
        response = dict()
        response['changed'] = False
        network_name = self.params.get('network_name')
        force = self.params.get('force')

        try:
            self.vdc.get_direct_orgvdc_network(network_name)
        except EntityNotFoundException:
            msg = "Org VDC Direct Network {0} is not present"
            response['warnings'] = msg.format(network_name)
        else:
            delete_task = self.vdc.delete_direct_orgvdc_network(
                network_name, force=force)
            self.execute_task(delete_task)
            msg = 'Org VDC Direct Network {} has been deleted'
            response['msg'] = msg.format(network_name)
            response['changed'] = True

        return response

    def delete_org_vdc_isolated_network(self):
        response = dict()
        response['changed'] = False
        network_name = self.params.get('network_name')
        force = self.params.get('force')

        try:
            self.vdc.get_isolated_orgvdc_network(network_name)
        except EntityNotFoundException:
            msg = "Org VDC Direct Network {0} is not present"
            response['warnings'] = msg.format(network_name)
        else:
            delete_task = self.vdc.delete_isolated_orgvdc_network(
                network_name, force=force)
            self.execute_task(delete_task)
            msg = 'Org VDC Direct Network {} has been deleted'
            response['msg'] = msg.format(network_name)
            response['changed'] = True

        return response

    def delete_org_vdc_routed_network(self):
        response = dict()
        response['changed'] = False
        network_name = self.params.get('network_name')
        force = self.params.get('force')

        try:
            self.vdc.get_routed_orgvdc_network(network_name)
        except EntityNotFoundException:
            msg = "Org VDC Direct Network {0} is not present"
            response['warnings'] = msg.format(network_name)
        else:
            delete_task = self.vdc.delete_routed_orgvdc_network(
                network_name, force=force)
            self.execute_task(delete_task)
            msg = 'Org VDC Direct Network {} has been deleted'
            response['msg'] = msg.format(network_name)
            response['changed'] = True

        return response


def main():
    argument_spec = org_vdc_network_argument_spec()
    response = dict(msg=dict(type='str'))
    module = OrgVdcNetwork(
        argument_spec=argument_spec, supports_check_mode=True)
    try:
        if module.check_mode:
            response = dict()
            response['changed'] = False
            response['msg'] = "skipped, running in check mode"
            response['skipped'] = True
        elif module.params.get('state'):
            response = module.manage_states()
        else:
            raise Exception('Please provide the state for the resource')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
