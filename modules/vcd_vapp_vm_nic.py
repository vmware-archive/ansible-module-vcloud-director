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
    vm: vm1
    vapp = vapp1
    vdc = vdc1
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
        nic_ids=dict(type='list', required=False),
        ip_address=dict(type='str', required=False, default=None),
        network=dict(type='str', required=False),
        is_primary=dict(type='bool', required=False, default=False),
        is_connected=dict(type='bool', required=False, default=False),
        ip_allocation_mode=dict(choices=IP_ALLOCATION_MODE, required=False),
        adapter_type=dict(choices=NETWORK_ADAPTER_TYPE, required=False),
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
        network = self.params.get('network')
        ip_address = self.params.get('ip_address')
        ip_allocation_mode = self.params.get('ip_allocation_mode')
        adapter_type = self.params.get('adapter_type')
        is_primary = self.params.get('is_primary')
        is_connected = self.params.get('is_connected')
        response = dict()
        response['changed'] = False

        add_nic_task = vm.add_nic(adapter_type=adapter_type,
                                  is_primary=is_primary,
                                  is_connected=is_connected,
                                  network_name=network,
                                  ip_address_mode=ip_allocation_mode,
                                  ip_address=ip_address)
        self.execute_task(add_nic_task)
        response['msg'] = 'A new nic has been added to VM {0}'.format(vm_name)
        response['changed'] = True

        return response

    def update_nic(self):
        vm = self.get_vm()
        vm_name = self.params.get('vm_name')
        network = self.params.get('network')
        ip_address = self.params.get('ip_address')
        ip_allocation_mode = self.params.get('ip_allocation_mode')
        adapter_type = self.params.get('adapter_type')
        is_primary = self.params.get('is_primary')
        is_connected = self.params.get('is_connected')
        response = dict()
        response['changed'] = False

        try:
            update_nic_task = vm.update_nic(network_name=network,
                                            is_connected=is_connected,
                                            is_primary=is_primary,
                                            adapter_type=adapter_type,
                                            ip_address=ip_address,
                                            ip_address_mode=ip_allocation_mode)
            self.execute_task(update_nic_task)
            msg = 'A nic attached with VM {0} has been updated'
            response['msg'] = msg.format(vm_name)
            response['changed'] = True
        except EntityNotFoundException as error:
            response['msg'] = error.__str__()

        return response

    def read_nics(self):
        vm = self.get_vm()
        response = dict()
        response['changed'] = False
        response['msg'] = vm.list_nics()

        return response

    def delete_nic(self):
        vm = self.get_vm()
        nic_ids = self.params.get('nic_ids')
        vm_name = self.params.get('vm_name')
        response = dict()
        response['changed'] = False

        # VM should be powered off before deleting a nic
        if not vm.is_powered_off():
            msg = "VM {0} is powered on. Cant remove nics in the current state"
            raise OperationNotSupportedException(msg.format(vm_name))

        for nic_id in nic_ids:
            try:
                delete_nic_task = vm.delete_nic(nic_id)
                self.execute_task(delete_nic_task)
                response['changed'] = True
            except InvalidParameterException as error:
                response['msg'] = error.__str__()
            else:
                response['msg'] = 'VM nic(s) has been deleted'

        return response


def main():
    argument_spec = vapp_vm_nic_argument_spec()
    response = dict(msg=dict(type='str'))
    module = VappVMNIC(argument_spec=argument_spec, supports_check_mode=True)
    try:
        if module.params.get('state'):
            response = module.manage_states()
        elif module.params.get('operation'):
            response = module.manage_operations()
        else:
            raise Exception('Please provide state/operation for resource')

    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
