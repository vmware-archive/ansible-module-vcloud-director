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
short_description: Manage VM NIC's states/operations in vCloud Director
version_added: "2.4"
description:
    - Manage VM NIC's states/operations in vCloud Director

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
    nics:
        description:
            - List of NICs
        required: false
    network:
        description:
            - VApp network name
        required: false
    vm_name:
        description:
            - VM name
        required: true
    adapter_type:
        description:
            - nic adapter type.One of NetworkAdapterType values
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
            - state of nic (present/update/absent).
            - One from state or operation has to be provided.
        required: true
    operation:
        description:
            - operation on nic (read).
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
    vm_name: vm1
    vapp = vapp1
    vdc = vdc1
    nics:
      - nic_id: 1
        network: acme_internal_direct
        ip_allocation_mode: DHCP
        is_connected: True
        adapter_type: E1000
    state = "present"
'''

RETURN = '''
msg: success/failure message corresponding to nic state
changed: true if resource has been changed else false
'''

from pyvcloud.vcd.vm import VM
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.client import EntityType
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import OperationNotSupportedException
from pyvcloud.vcd.exceptions import EntityNotFoundException, InvalidParameterException


VAPP_VM_NIC_OPERATIONS = ['read']
IP_ALLOCATION_MODE = ["DHCP", "POOL", "MANUAL"]
VAPP_VM_NIC_STATES = ['present', 'absent', 'update']
NETWORK_ADAPTER_TYPE = ['VMXNET', 'VMXNET2',
                        'VMXNET3', 'E1000', 'E1000E', 'PCNet32']


def vapp_vm_nic_argument_spec():
    return dict(
        vm_name=dict(type='str', required=True),
        vapp=dict(type='str', required=True),
        vdc=dict(type='str', required=True),
        nics=dict(type='list', required=False),
        ip_address=dict(type='str', required=False, default=None),
        network=dict(type='str', required=False),
        is_primary=dict(type='bool', required=False, default=False),
        is_connected=dict(type='bool', required=False, default=False),
        ip_allocation_mode=dict(choices=IP_ALLOCATION_MODE, required=False),
        adapter_type=dict(choices=NETWORK_ADAPTER_TYPE, required=False),
        org_name=dict(type='str', required=False, default=None),
        state=dict(choices=VAPP_VM_NIC_STATES, required=False),
        operation=dict(choices=VAPP_VM_NIC_OPERATIONS, required=False),
    )


class VappVMNIC(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VappVMNIC, self).__init__(**kwargs)
        self.org = self.get_org()
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

    def get_vm(self):
        vapp_vm_resource = self.vapp.get_vm(self.params.get('vm_name'))

        return VM(self.client, resource=vapp_vm_resource)

    def get_vm_nics(self):
        vm = self.get_vm()

        return self.client.get_resource(
            vm.resource.get('href') + '/networkConnectionSection')

    def add_nic(self):
        vm = self.get_vm()
        vm_name = self.params.get('vm_name')
        nics = self.params.get('nics')
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        for nic in nics:
            try:
                network = nic.get('network')
                nic_id = nic.get('nic_id')
                ip_address = nic.get('ip_address')
                ip_allocation_mode = nic.get('ip_allocation_mode')
                adapter_type = nic.get('adapter_type')
                is_primary = nic.get('is_primary')
                is_connected = nic.get('is_connected')
                add_nic_task = vm.add_nic(adapter_type=adapter_type,
                                          is_primary=is_primary,
                                          is_connected=is_connected,
                                          network_name=network,
                                          ip_address_mode=ip_allocation_mode,
                                          ip_address=ip_address)
                self.execute_task(add_nic_task)
                msg = 'Nic {0} has been added to VM {1}'
                msg = msg.format(nic_id, vm_name)
                response['changed'] = True
            except OperationNotSupportedException as error:
                msg = 'Nic {0} throws following error: {1}'
                msg = msg.format(nic_id, error.__str__())
            response['msg'].append(msg)

        return response

    def update_nic(self):
        vm = self.get_vm()
        nics = self.params.get('nics')
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        for nic in nics:
            try:
                network = nic.get('network')
                nic_id = nic.get('nic_id')
                ip_address = nic.get('ip_address')
                ip_allocation_mode = nic.get('ip_allocation_mode')
                adapter_type = nic.get('adapter_type')
                is_primary = nic.get('is_primary')
                is_connected = nic.get('is_connected')
                update_nic_task = vm.update_nic(
                    network_name=network, nic_id=nic_id,
                    is_connected=is_connected, is_primary=is_primary,
                    adapter_type=adapter_type, ip_address=ip_address,
                    ip_address_mode=ip_allocation_mode)
                self.execute_task(update_nic_task)
                msg = 'Nic {0} has been updated'.format(nic_id)
                response['changed'] = True
            except EntityNotFoundException as error:
                msg = 'Nic {0} throws following error: {1}'
                msg = msg.format(nic_id, error.__str__())
            response['msg'].append(msg)

        return response

    def read_nics(self):
        vm = self.get_vm()
        response = dict()
        response['changed'] = False
        response['msg'] = vm.list_nics()

        return response

    def delete_nic(self):
        vm = self.get_vm()
        nics = self.params.get('nics')
        vm_name = self.params.get('vm_name')
        response = dict()
        response['msg'] = list()
        response['changed'] = False

        # check if VM is powered off
        if not vm.is_powered_off():
            msg = "VM {0} is powered on. Cant remove nics in the current state"
            raise OperationNotSupportedException(msg.format(vm_name))

        for nic in nics:
            try:
                nic_id = nic.get('nic_id')
                delete_nic_task = vm.delete_nic(nic_id)
                self.execute_task(delete_nic_task)
                msg = 'VM nic {0} has been deleted'.format(nic_id)
                response['changed'] = True
            except (InvalidParameterException, EntityNotFoundException) as error:
                msg = 'Nic {0} throws following error: {1}'
                msg = msg.format(nic_id, error.__str__())
            response['msg'].append(msg)

        return response


def main():
    argument_spec = vapp_vm_nic_argument_spec()
    response = dict(msg=dict(type='str'))
    module = VappVMNIC(argument_spec=argument_spec, supports_check_mode=True)
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
        response['msg'] = error
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
