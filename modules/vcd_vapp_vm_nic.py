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
module: vcd_vapp_vm_nic
short_description: Ansible Module to manage (create/delete/update) NICs in vApp VMs in vCloud Director.
version_added: "2.4"
description:
    - "Ansible Module to manage (create/delete/update) NICs in vApp VMs."

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
    nic_id:
        description:
            - NIC ID
        required: false
    nic_ids:
        description:
            - List of NIC IDs
        required: false
    network:
        description:
            - VApp network name
        required: false
    vm_name:
        description:
            - VM name
        required: true
    vapp:
        description:
            - vApp name
        required: true
    vdc:
        description:
            - VDC name
        required: true
    ip_allocation_mode:
        description:
            - IP allocation mode (DHCP, POOL or MANUAL)
        required: false
    ip_address:
        description:
            - NIC IP address (required for MANUAL IP allocation mode)
        required: false
    state:
        description:
            - state of nic (present/absent).
            - One from state or operation has to be provided.
        required: true
    operation:
        description:
            - operation on nic (update/read).
            - One from state or operation has to be provided.
        required: false
author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_vapp_vm_nic:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    org: Terraform
    api_version: 30
    verify_ssl_certs: False
    vm: "vm1"
    vapp = "vapp1"
    vdc = "vdc1"
    nic_id = "2000"
    state = "present"
'''

RETURN = '''
msg: success/failure message corresponding to nic state
changed: true if resource has been changed else false
'''

from copy import deepcopy
from lxml import etree
from pyvcloud.vcd.vm import VM
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.client import E
from pyvcloud.vcd.vapp import VApp
from collections import defaultdict
from pyvcloud.vcd.client import E_RASD
from pyvcloud.vcd.client import NSMAP
from pyvcloud.vcd.client import EntityType
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException, OperationNotSupportedException


VAPP_VM_NIC_STATES = ['present', 'absent', 'update']
VAPP_VM_NIC_OPERATIONS = ['read']


def vapp_vm_nic_argument_spec():
    return dict(
        vm_name=dict(type='str', required=True),
        vapp=dict(type='str', required=True),
        vdc=dict(type='str', required=True),
        nic_id=dict(type='int', required=False),
        nic_ids=dict(type='list', required=False),
        ip_allocation_mode=dict(type='str', required=False),
        ip_address=dict(type='str', required=False,),
        network=dict(type='str', required=False),
        state=dict(choices=VAPP_VM_NIC_STATES, required=False),
        operation=dict(choices=VAPP_VM_NIC_OPERATIONS, required=False),
    )


class VappVMNIC(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VappVMNIC, self).__init__(**kwargs)
        vapp_resource = self.get_resource()
        self.vapp = VApp(self.client, resource=vapp_resource)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.add_nic()

        if state == "update":
            return self.update_nic()

        if state == "absent":
            return self.delete_nic()

    def manage_operations(self):
        operation = self.params.get('operation')

        if operation == "read":
            return self.read_nics()

    def get_resource(self):
        vapp = self.params.get('vapp')
        vdc = self.params.get('vdc')
        org_resource = Org(self.client, resource=self.client.get_org())
        vdc_resource = VDC(self.client, resource=org_resource.get_vdc(vdc))
        vapp_resource_href = vdc_resource.get_resource_href(name=vapp, entity_type=EntityType.VAPP)
        vapp_resource = self.client.get_resource(vapp_resource_href)

        return vapp_resource

    def get_vm(self):
        vapp_vm_resource = self.vapp.get_vm(self.params.get('vm_name'))

        return VM(self.client, resource=vapp_vm_resource)

    def get_vm_nics(self):
        vm = self.get_vm()

        return self.client.get_resource(vm.resource.get('href') + '/networkConnectionSection')

    def add_nic(self):
        '''
            Error - More than 10 Nics are not permissible in vCD
        '''
        vm = self.get_vm()
        network = self.params.get('network')
        ip_address = self.params.get('ip_address')
        ip_allocation_mode = self.params.get('ip_allocation_mode')
        uri = vm.resource.get('href') + '/networkConnectionSection'
        response = defaultdict(dict)
        response['changed'] = False
        new_nic_id = None

        nics = self.get_vm_nics()
        nics_indexes = [int(nic.NetworkConnectionIndex) for nic in nics.NetworkConnection]
        nics_indexes.sort()
        for index, nic_index in enumerate(nics_indexes):
            new_nic_id = nic_index + 1
            if index != nic_index:
                new_nic_id = index
                break

        if ip_allocation_mode not in ('DHCP', 'POOL', 'MANUAL'):
            raise Exception('IpAllocationMode should be one of DHCP/POOL/MANUAL')

        if ip_allocation_mode in ('DHCP', 'POOL'):
            nic = E.NetworkConnection(
                E.NetworkConnectionIndex(new_nic_id),
                E.IsConnected(True),
                E.IpAddressAllocationMode(ip_allocation_mode),
                network=network)
        else:
            if not ip_address:
                raise Exception('IpAddress is missing.')
            nic = E.NetworkConnection(
                E.NetworkConnectionIndex(new_nic_id),
                E.IpAddress(ip_address),
                E.IsConnected(True),
                E.IpAddressAllocationMode(ip_allocation_mode),
                network=network)

        nics.NetworkConnection.addnext(nic)
        add_nic_task = self.client.put_resource(uri, nics, EntityType.NETWORK_CONNECTION_SECTION.value)
        self.execute_task(add_nic_task)
        response['msg'] = {
            'nic_id': new_nic_id,
            'ip_allocation_mode': ip_allocation_mode,
            'ip_address': ip_address
        }
        response['changed'] = True

        return response

    def update_nic(self):
        '''
            Following update scenarios are covered
            1. MANUAL mode to DHCP
            2. Update IP address in MANUAL mode
            3. DHCP to MANUAL mode
        '''
        vm = self.get_vm()
        nic_id = self.params.get('nic_id')
        network = self.params.get('network')
        ip_address = self.params.get('ip_address')
        ip_allocation_mode = self.params.get('ip_allocation_mode')
        uri = vm.resource.get('href') + '/networkConnectionSection'
        response = defaultdict(dict)
        response['changed'] = False

        nics = self.get_vm_nics()
        nic_indexs = [nic.NetworkConnectionIndex for nic in nics.NetworkConnection]
        if nic_id not in nic_indexs:
            raise EntityNotFoundException('Can\'t find the specified VM nic')
        nic_to_update = nic_indexs.index(nic_id)

        if network:
            nics.NetworkConnection[nic_to_update].set('network', network)
            response['changed'] = True

        if ip_allocation_mode:
            allocation_mode_element = E.IpAddressAllocationMode(ip_allocation_mode)
            nics.NetworkConnection[nic_to_update].IpAddressAllocationMode = allocation_mode_element
            response['changed'] = True

        if ip_address:
            response['changed'] = True
            if hasattr(nics.NetworkConnection[nic_to_update], 'IpAddress'):
                nics.NetworkConnection[nic_to_update].IpAddress = E.IpAddress(ip_address)
            else:
                network = nics.NetworkConnection[nic_to_update].get('network')
                nics.NetworkConnection[nic_to_update] = E.NetworkConnection(
                    E.NetworkConnectionIndex(nic_id),
                    E.IpAddress(ip_address),
                    E.IsConnected(True),
                    E.IpAddressAllocationMode(ip_allocation_mode),
                    network=network)

        if response['changed']:
            update_nic_task = self.client.put_resource(uri, nics, EntityType.NETWORK_CONNECTION_SECTION.value)
            self.execute_task(update_nic_task)
            response['msg'] = 'Vapp VM nic has been updated.'

        return response

    def read_nics(self):
        response = defaultdict(dict)
        response['changed'] = False

        nics = self.get_vm_nics()
        for nic in nics.NetworkConnection:
            meta = defaultdict(dict)
            nic_id = str(nic.NetworkConnectionIndex)
            meta['MACAddress'] = str(nic.MACAddress)
            meta['IsConnected'] = str(nic.IsConnected)
            meta['NetworkAdapterType'] = str(nic.NetworkAdapterType)
            meta['NetworkConnectionIndex'] = str(nic.NetworkConnectionIndex)
            meta['IpAddressAllocationMode'] = str(nic.IpAddressAllocationMode)

            if hasattr(nic, 'IpAddress'):
                meta['IpAddress'] = str(nic.IpAddress)

            response['msg'][nic_id] = meta

        return response

    def delete_nic(self):
        vm = self.get_vm()
        nic_ids = self.params.get('nic_ids')
        response = defaultdict(dict)
        response['changed'] = False
        uri = vm.resource.get('href') + '/networkConnectionSection'

        nics = self.get_vm_nics()
        for nic in nics.NetworkConnection:
            if nic.NetworkConnectionIndex in nic_ids:
                nics.remove(nic)
                nic_ids.remove(nic.NetworkConnectionIndex)

        if len(nic_ids) > 0:
            nic_ids = [str(nic_id) for nic_id in nic_ids]
            err_msg = 'Can\'t find the specified VM nic(s) {0}'.format(','.join(nic_ids))
            raise EntityNotFoundException(err_msg)

        remove_nic_task = self.client.put_resource(uri, nics, EntityType.NETWORK_CONNECTION_SECTION.value)
        self.execute_task(remove_nic_task)
        response['msg'] = 'VM nic(s) has been deleted.'
        response['changed'] = True

        return response


def main():
    argument_spec = vapp_vm_nic_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = VappVMNIC(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.params.get('state'):
            response = module.manage_states()
        elif module.params.get('operation'):
            response = module.manage_operations()
        else:
            raise Exception('One of the state/operation should be provided.')

    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
