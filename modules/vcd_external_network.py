# Copyright © 2018 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause OR GPL-3.0-only

# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: vcd_external_network
short_description: Manage external_network's states/operations in vCloud Director
version_added: "2.4"
description:
    - Manage external_network's states/operations in vCloud Director

options:
    user:
        description:
            - vCloud Director user name
        required: false
    password:
        description:
            - vCloud Director user password
        required: false
    host:
        description:
            - vCloud Director host address
        required: false
    org:
        description:
            - Organization name on vCloud Director to access
        required: false
    api_version:
        description:
            - Pyvcloud API version
        required: false
    verify_ssl_certs:
        description:
            - whether to use secure connection to vCloud Director host
        required: false
    vc_name:
        description:
            - Name of underlying vCenter
        required: false
    port_group_names:
        description:
            - vCenter port groups external network may get attached with
        type: list
        required: false
    network_name:
        description:
            - external network name
        required: false
    description:
        description:
            - description text for external network
        required: false
    new_network_name:
        description:
            - new external network name to update exisiting network name
        required: false
    gateway_ip:
        description:
            - IP address of the gateway of the new network
        required: false
    netmask:
        description:
            - Netmask of the gateway
        required: false
    ip_ranges:
        description:
            - list of IP ranges used for static pool allocation in the network
        required: false
    new_ip_ranges:
        description:
            - IP ranges used for static pool allocation in the network
        type: list
        required: false
    primary_dns_ip:
        description:
            - IP address of primary DNS server
        required: false
        default: None
    secondary_dns_ip:
        description:
            - IP address of secondary DNS Server
        required: false
        default: None
    dns_suffix:
        description:
            - DNS suffix
        required: false
        default: None
    force_delete:
        description:
            - boolean flag to force to delete a network
        required: false
        default: False
    enable_subnet:
        description:
            - boolean flag to enable/disable subnet
        required: false
        default: True
    state:
        description:
            - state of external network ('present' / 'update' / 'absent').
            - One from state or operation has to be provided.
        required: false
    operation:
        description:
            - operation of external network ('list').
            - One from state or operation has to be provided.
        required: false

author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: create external network
  vcd_external_networks:
    vc_name: vc.0
    port_group_names:
        - VM Network
    network_name: external-network
    gateway_ip: 10.176.3.253
    netmask: 255.255.0.0
    ip_ranges:
        - 10.176.7.68-10.176.7.69
    state: "present"
  register: output
'''

RETURN = '''
msg: success/failure message corresponding to external networks state/operation
changed: true if resource has been changed else false
'''

from pyvcloud.vcd.platform import Platform
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.external_network import ExternalNetwork
from pyvcloud.vcd.exceptions import EntityNotFoundException


VCD_EXTERNAL_NETWORKS_STATES = ['present', 'update', 'absent']
VCD_EXTERNAL_NETWORKS_OPERATIONS = ['list_networks', 'add_subnet',
                                    'add_ip_ranges', 'modify_ip_ranges',
                                    'delete_ip_ranges', 'enable_subnet',
                                    'attach_port_group', 'detach_port_group']


def vcd_external_network_argument_spec():
    return dict(
        vc_name=dict(type='str', required=False),
        port_group_names=dict(type='list', required=False),
        network_name=dict(type='str', required=False),
        new_network_name=dict(type='str', required=False),
        force_delete=dict(type='bool', required=False, default=False),
        description=dict(type='str', required=False, default=None),
        gateway_ip=dict(type='str', required=False),
        netmask=dict(type='str', required=False),
        ip_ranges=dict(type='list', required=False),
        new_ip_ranges=dict(type='list', required=False),
        primary_dns_ip=dict(type='str', required=False, default=None),
        secondary_dns_ip=dict(type='str', required=False, default=None),
        dns_suffix=dict(type='str', required=False, default=None),
        enable_subnet=dict(type='bool', required=False, default=True),
        state=dict(choices=VCD_EXTERNAL_NETWORKS_STATES, required=False),
        operation=dict(choices=VCD_EXTERNAL_NETWORKS_OPERATIONS, required=False)
    )


class VcdExternalNetwork(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VcdExternalNetwork, self).__init__(**kwargs)
        self.platform = Platform(self.client)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.create()

        if state == "update":
            return self.update()

        if state == "absent":
            return self.delete()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "list_networks":
            return self.list_external_networks()

        if operation == "add_subnet":
            return self.add_subnet()

        if operation == "add_ip_ranges":
            return self.add_ip_ranges()

        if operation == "modify_ip_ranges":
            return self.modify_ip_ranges()

        if operation == "delete_ip_ranges":
            return self.delete_ip_ranges()

        if operation == "enable_subnet":
            return self.enable_subnet()

        if operation == "attach_port_group":
            return self.attach_port_group()

        if operation == "detach_port_group":
            return self.detach_port_group()

    def create(self):
        vc_name = self.params.get('vc_name')
        port_group_names = self.params.get('port_group_names')
        network_name = self.params.get('network_name')
        gateway_ip = self.params.get('gateway_ip')
        netmask = self.params.get('netmask')
        ip_ranges = self.params.get('ip_ranges')
        primary_dns_ip = self.params.get('primary_dns_ip')
        secondary_dns_ip = self.params.get('secondary_dns_ip')
        dns_suffix = self.params.get('dns_suffix')
        description = self.params.get('description')
        response = dict()
        response['changed'] = False

        try:
            self.platform.get_external_network(network_name)
        except EntityNotFoundException:
            self.platform.create_external_network(network_name, vc_name,
                                                  port_group_names, gateway_ip,
                                                  netmask, ip_ranges,
                                                  description,
                                                  primary_dns_ip,
                                                  secondary_dns_ip,
                                                  dns_suffix)
            msg = "External Network {0} is created"
            response['msg'] = msg.format(network_name)
            response['changed'] = True
        else:
            msg = "External Network {0} is already present"
            response['warnings'] = msg.format(network_name)

        return response

    def update(self):
        network_name = self.params.get('network_name')
        new_network_name = self.params.get('new_network_name')
        description = self.params.get('description')
        response = dict()
        response['changed'] = False

        try:
            self.platform.get_external_network(network_name)
            self.platform.update_external_network(
                network_name, new_network_name, description)
        except EntityNotFoundException:
            msg = "External Network {0} does not exists"
            response['msg'] = msg.format(network_name)
        else:
            msg = "External Network {0} has been updated with {1}"
            response['msg'] = msg.format(network_name, new_network_name)
            response['changed'] = True

        return response

    def delete(self):
        network_name = self.params.get('network_name')
        force_delete = self.params.get('force_delete')
        response = dict()
        response['changed'] = False

        try:
            task = self.platform.delete_external_network(
                network_name, force_delete)
            self.execute_task(task)
        except EntityNotFoundException:
            msg = "External Network {0} does not exists"
            response['msg'] = msg.format(network_name)
        else:
            msg = "External Network {0} has been deleted"
            response['msg'] = msg.format(network_name)
            response['changed'] = True

        return response

    def list_external_networks(self):
        response = dict()
        response['msg'] = list()
        response['changed'] = False

        networks = self.platform.list_external_networks()
        response['msg'] = [v for k, v in networks.items() if k == "name"]

        return response

    def add_subnet(self):
        network_name = self.params.get('network_name')
        gateway_ip = self.params.get('gateway_ip')
        netmask = self.params.get('netmask')
        ip_ranges = self.params.get('ip_ranges')
        primary_dns_ip = self.params.get('primary_dns_ip')
        secondary_dns_ip = self.params.get('secondary_dns_ip')
        dns_suffix = self.params.get('dns_suffix')
        response = dict()
        response['changed'] = False

        network = self.get_network(network_name)
        network.add_subnet(network_name, gateway_ip, netmask, ip_ranges,
                           primary_dns_ip, secondary_dns_ip, dns_suffix)
        msg = "A new subnet has been added to network {0}"
        response['msg'] = msg.format(network_name)
        response['changed'] = True

        return response

    def add_ip_ranges(self):
        network_name = self.params.get('network_name')
        gateway_ip = self.params.get('gateway_ip')
        ip_ranges = self.params.get('ip_ranges')
        response = dict()
        response['changed'] = False

        network = self.get_network(network_name)
        network.add_ip_range(gateway_ip, ip_ranges)
        msg = "A new ip ranges has been added to network {0}"
        response['msg'] = msg.format(network_name)
        response['changed'] = True

        return response

    def modify_ip_ranges(self):
        network_name = self.params.get('network_name')
        gateway_ip = self.params.get('gateway_ip')
        ip_ranges = self.params.get('ip_ranges')
        new_ip_ranges = self.params.get('new_ip_ranges')
        response = dict()
        response['changed'] = False

        if len(ip_ranges) != len(new_ip_ranges):
            raise ValueError(
                "ip_ranges and new_ip_ranges should have same length")

        network = self.get_network(network_name)
        for i in range(len(ip_ranges)):
            network.modify_ip_range(gateway_ip, ip_ranges[i], new_ip_ranges[i])

        msg = "Ip ranges have been updated to network {0}"
        response['msg'] = msg.format(network_name)
        response['changed'] = True

        return response

    def delete_ip_ranges(self):
        network_name = self.params.get('network_name')
        gateway_ip = self.params.get('gateway_ip')
        ip_ranges = self.params.get('ip_ranges')
        response = dict()
        response['changed'] = False

        network = self.get_network(network_name)
        network.delete_ip_range(gateway_ip, ip_ranges)
        msg = "Ip ranges have been deleted from network {0}"
        response['msg'] = msg.format(network_name)
        response['changed'] = True

        return response

    def enable_subnet(self):
        network_name = self.params.get('network_name')
        gateway_ip = self.params.get('gateway_ip')
        enable_subnet = self.params.get('enable_subnet')
        response = dict()
        response['changed'] = False

        network = self.get_network(network_name)
        network.enable_subnet(gateway_ip, enable_subnet)
        s = "has been enabled" if enable_subnet else "has been disabled"
        msg = "subnet with gatway {0} {1} now in network {2}"
        response['msg'] = msg.format(gateway_ip, s, network_name)
        response['changed'] = True

        return response

    def attach_port_group(self):
        network_name = self.params.get('network_name')
        vc_name = self.params.get('vc_name')
        port_group_names = self.params.get('port_group_names')
        response = dict()
        response['changed'] = False

        network = self.get_network(network_name)
        for port_group_name in port_group_names:
            network.attach_port_group(vc_name, port_group_name)

        msg = "port groups {0} have been attached now from network {1}"
        response['msg'] = msg.format(','.join(port_group_names), network_name)
        response['changed'] = True

        return response

    def detach_port_group(self):
        network_name = self.params.get('network_name')
        vc_name = self.params.get('vc_name')
        port_group_names = self.params.get('port_group_names')
        response = dict()
        response['changed'] = False
        network = self.get_network(network_name)

        for port_group_name in port_group_names:
            network.detach_port_group(vc_name, port_group_name)

        msg = "port groups {0} have been detached now from network {1}"
        response['msg'] = msg.format(','.join(port_group_names), network_name)
        response['changed'] = True

        return response

    def get_network(self, network_name):
        network_resource = self.platform.get_external_network(network_name)

        return ExternalNetwork(self.client, resource=network_resource)


def main():
    argument_spec = vcd_external_network_argument_spec()
    response = dict(msg=dict(type='str'))
    module = VcdExternalNetwork(
        argument_spec=argument_spec, supports_check_mode=True)

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
            raise Exception("Please provide state/operation for resource")

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
