# Copyright © 2018 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause

# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: vcd_vapp_vm_nic
short_description: Ansible Module to manage (create/delete) NICs in vApp VMs in vCloud Director.
version_added: "2.4"
description:
    - "Ansible Module to manage (create/delete) NICs in vApp VMs."

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
    state:
        description:
            - state of nic ('present'/'absent').
            - One from state or operation has to be provided.
        required: true
    operation:
        description:
            - operation on nic ('update').
            - One from state or operation has to be provided.
        required:
            - false
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
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.vm import VM
from pyvcloud.vcd.client import E
from pyvcloud.vcd.client import E_RASD
from pyvcloud.vcd.client import EntityType
from pyvcloud.vcd.client import NSMAP
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException, OperationNotSupportedException


VAPP_VM_NIC_STATES = ['present', 'absent']
VAPP_VM_NIC_OPERATIONS = ['update']


def vapp_vm_nic_argument_spec():
    return dict(
        vm_name=dict(type='str', required=True),
        vapp=dict(type='str', required=True),
        vdc=dict(type='str', required=True),
        nic_id=dict(type='int', required=False),
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

        if state == "absent":
            return self.delete_nic()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "update":
            return self.update_nic()

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

    def add_nic(self):
        vm = self.get_vm()
        nic_id = self.params.get('nic_id')
        network = self.params.get('network')
        response = dict()
        response['changed'] = False
        max_id = -1;

        nics = self.client.get_resource(vm.resource.get('href') + '/networkConnectionSection')
        for nic in nics.NetworkConnection:
            if nic.NetworkConnectionIndex == nic_id:
                response['warnings'] = 'NIC is already present.'
                return response
            if nic.NetworkConnectionIndex > max_id:
                max_id = int(nic.NetworkConnectionIndex.text)

        nic = E.NetworkConnection(
            E.NetworkConnectionIndex(max_id+1 if nic_id is None else nic_id),
            E.IsConnected(True),
            E.IpAddressAllocationMode('DHCP'),
            network=network)
        nics.NetworkConnection.addnext(nic)

        add_nic_task = self.client.put_resource(
            vm.resource.get('href') + '/networkConnectionSection', nics,
            EntityType.NETWORK_CONNECTION_SECTION.value)
        self.execute_task(add_nic_task)

        response['msg'] = 'Vapp VM NIC has been added.'
        response['changed'] = True

        return response

    def delete_nic(self):
        vm = self.get_vm()
        nic_id = self.params.get('nic_id')
        response = dict()
        response['changed'] = False

        nics = self.client.get_resource(vm.resource.get('href') + '/networkConnectionSection')
        for nic in nics.NetworkConnection:
            if nic.NetworkConnectionIndex == nic_id:
                nics.remove(nic)
                remove_nic_task = self.client.put_resource(
                    vm.resource.get('href') + '/networkConnectionSection', nics,
                    EntityType.NETWORK_CONNECTION_SECTION.value)
                self.execute_task(remove_nic_task)
                response['msg'] = 'VM nic has been deleted.'
                response['changed'] = True
                return response

        response['warnings'] = 'VM nic was not found'
        return response

    def update_nic(self):
        vm = self.get_vm()
        nic_id = self.params.get('nic_id')
        network = self.params.get('network')
        response = dict()
        response['changed'] = False

        nics = self.client.get_resource(vm.resource.get('href') + '/networkConnectionSection')
        index = -1

        for i, nic in enumerate(nics.NetworkConnection):
            if nic.NetworkConnectionIndex == nic_id:
                index = i

        if index < 0:
            EntityNotFoundException('Can\'t find the specified VM nic')

        if network:
            nics.NetworkConnection[index].set('network', network)
            response['changed'] = True

        if response['changed']:
            update_nic_task = self.client.put_resource(
                vm.resource.get('href') + '/networkConnectionSection', nics,
                EntityType.NETWORK_CONNECTION_SECTION.value)
            self.execute_task(update_nic_task)
            response['msg'] = 'Vapp VM nic has been updated.'

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
