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
module: vcd_vapp_network
short_description: Manage vApp Network's states/operation in vCloud Director
version_added: "2.4"
description:
    - Manage vApp Network's states/operation in vCloud Director

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
    org_name:
        description:
            - target org name
            - required for service providers to create resources in other orgs
            - default value is module level / environment level org
        required: false
    vapp:
        description:
            - vApp name
        required: true
    vdc:
        description:
            - VDC name
        required: true
    network:
        description:
            - Network name
        required: true
    new_network:
        description:
            - Name of the new Network in case of update vApp Network
        required: false
    network_cidr:
        description:
            - CIDR in the format of 192.168.1.1/24
        required: false
    description:
        description:
            - description of vApp network
        required: false
    primary_dns_ip:
        description:
            - IP address of primary DNS server
        required: false
    secondary_dns_ip:
        description:
            - IP address of secondary DNS Server
        required: false
    dns_suffix:
        description:
            - DNS suffix
        required: false
    ip_ranges:
        description:
            - list of IP ranges used for static pool allocation in the network
            - For example,
                - [192.168.1.2-192.168.1.49, 192.168.1.100-192.168.1.149]
        required: false
    is_guest_vlan_allowed:
        description:
            - True if guest vlan allowed in vApp network else False
        required: false
    state:
        description:
            - state of network (present/update/absent)
        required: false
    operation:
        description:
            - operation on network (read)
        required: false
author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_vapp_network:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    org: Terraform
    api_version: 30
    verify_ssl_certs: False
    network: uplink
    vapp: vapp1
    vdc: vdc1
    dns_suffix: test_suffix
    ip_ranges:
        - 192.168.1.2-192.168.1.49
        - 192.168.1.100-192.168.1.149
    network_cidr: 192.168.1.1/24
    primary_dns_ip: 192.168.1.50
    state: present
'''

RETURN = '''
msg: success/failure message corresponding to vapp network state
changed: true if resource has been changed else false
'''

from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from collections import defaultdict
from pyvcloud.vcd.client import NSMAP
from pyvcloud.vcd.client import EntityType
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException
from pyvcloud.vcd.exceptions import OperationNotSupportedException


VAPP_NETWORK_STATES = ['present', 'update', 'absent']
VAPP_NETWORK_OPERATIONS = ['read']


def vapp_network_argument_spec():
    return dict(
        vdc=dict(type='str', required=False),
        vapp=dict(type='str', required=False),
        network=dict(type='str', required=False),
        new_network=dict(type='str', required=False),
        dns_suffix=dict(type='str', required=False),
        ip_ranges=dict(type='list', required=False),
        description=dict(type='str', required=False),
        network_cidr=dict(type='str', required=False),
        primary_dns_ip=dict(type='str', required=False),
        secondary_dns_ip=dict(type='str', required=False),
        is_guest_vlan_allowed=dict(type='bool', required=False),
        org_name=dict(type='str', required=False, default=None),
        state=dict(choices=VAPP_NETWORK_STATES, required=False),
        operation=dict(choices=VAPP_NETWORK_OPERATIONS, required=False),
    )


class VappNetwork(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VappNetwork, self).__init__(**kwargs)
        self.org = self.get_org()
        vapp_resource = self.get_resource()
        self.vapp = VApp(self.client, resource=vapp_resource)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.add_network()

        if state == "update":
            return self.update_network()

        if state == "absent":
            return self.delete_network()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "read":
            return self.get_all_networks()

    def get_org(self):
        org_name = self.params.get('org_name')
        org_resource = self.client.get_org()
        if org_name:
            org_resource = self.client.get_org_by_name(org_name)

        return Org(self.client, resource=org_resource)

    def get_resource(self):
        vapp = self.params.get('vapp')
        vdc = self.params.get('vdc')
        vdc_resource = VDC(self.client, resource=self.org.get_vdc(vdc))
        vapp_resource_href = vdc_resource.get_resource_href(
            name=vapp, entity_type=EntityType.VAPP)
        vapp_resource = self.client.get_resource(vapp_resource_href)

        return vapp_resource

    def get_network(self):
        network_name = self.params.get('network')
        networks = self.vapp.get_all_networks()
        for network in networks:
            if network.get('{' + NSMAP['ovf'] + '}name') == network_name:
                return network
        raise EntityNotFoundException('Can\'t find the specified vApp network')

    def get_all_networks(self):
        response = dict()
        response['changed'] = False
        response['msg'] = defaultdict(dict)

        for network in self.vapp.get_all_networks():
            name = network.get('{' + NSMAP['ovf'] + '}name')
            n = {'description': str(network.Description)}
            response['msg'][name] = n

        return response

    def add_network(self):
        network_name = self.params.get('network')
        network_cidr = self.params.get('network_cidr')
        network_description = self.params.get('description')
        primary_dns_ip = self.params.get('primary_dns_ip')
        secondary_dns_ip = self.params.get('secondary_dns_ip')
        dns_suffix = self.params.get('dns_suffix')
        ip_ranges = self.params.get('ip_ranges')
        is_guest_vlan_allowed = self.params.get('is_guest_vlan_allowed')
        response = dict()
        response['changed'] = False

        try:
            self.get_network()
        except EntityNotFoundException:
            add_network_task = self.vapp.create_vapp_network(
                name=network_name, network_cidr=network_cidr,
                description=network_description, primary_dns_ip=primary_dns_ip,
                secondary_dns_ip=secondary_dns_ip, dns_suffix=dns_suffix,
                ip_ranges=ip_ranges,
                is_guest_vlan_allowed=is_guest_vlan_allowed)
            self.execute_task(add_network_task)
            msg = 'Vapp Network {} has been added'
            response['msg'] = msg.format(network_name)
            response['changed'] = True
        else:
            msg = 'Vapp Network {} is already present'
            response['warnings'] = msg.format(network_name)

        return response

    def update_network(self):
        network_name = self.params.get('network')
        new_network_name = self.params.get('new_network')
        network_description = self.params.get('description')
        response = dict()
        response['changed'] = False

        try:
            self.get_network()
        except EntityNotFoundException:
            msg = 'Vapp Network {} is not present'
            response['warnings'] = msg.format(network_name)
        else:
            update_network_task = self.vapp.update_vapp_network(
                network_name=network_name, new_net_name=new_network_name,
                new_net_desc=network_description)
            self.execute_task(update_network_task)
            msg = 'Vapp Network {} has been updated'
            response['msg'] = msg.format(network_name)
            response['changed'] = True

        return response

    def delete_network(self):
        network_name = self.params.get('network')
        response = dict()
        response['changed'] = False

        try:
            self.get_network()
        except EntityNotFoundException:
            msg = 'Vapp Network {} is not present'
            response['warnings'] = msg.format(network_name)
        else:
            delete_network_task = self.vapp.delete_vapp_network(network_name)
            self.execute_task(delete_network_task)
            msg = 'Vapp Network {} has been deleted'
            response['msg'] = msg.format(network_name)
            response['changed'] = True

        return response


def main():
    argument_spec = vapp_network_argument_spec()
    response = dict(msg=dict(type='str'))
    module = VappNetwork(argument_spec=argument_spec, supports_check_mode=True)

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
            raise Exception('Please provide the state for the resource')

    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
