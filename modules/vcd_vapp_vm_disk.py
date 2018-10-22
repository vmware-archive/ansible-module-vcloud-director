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
module: vcd_vapp_vm_disk
short_description: Ansible Module to manage (create/delete) Disks in vApp VMs in vCloud Director.
version_added: "2.4"
description:
    - "Ansible Module to manage (create/delete) Disks in vApp VMs."

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
    disk_id:
        description:
            - Disk ID
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
    size:
        description:
            - Disk size in MB
        required: false
    state:
        description:
            - state of disk ('present'/'absent').
            - One from state or operation has to be provided.
        required: true
    operation:
        description:
            - operation on Disk ('update').
            - One from state or operation has to be provided.
        required:
            - false
author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_vapp_vm_disk:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    org: Terraform
    api_version: 30
    verify_ssl_certs: False
    vm: "vm1"
    vapp = "vapp1"
    vdc = "vdc1"
    disk_id = "2000"
    size = "2147483648"
    state = "present"
'''

RETURN = '''
msg: success/failure message corresponding to disk state
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


VAPP_VM_DISK_STATES = ['present', 'absent']
VAPP_VM_DISK_OPERATIONS = ['update']


def vapp_vm_disk_argument_spec():
    return dict(
        vm_name=dict(type='str', required=True),
        vapp=dict(type='str', required=True),
        vdc=dict(type='str', required=True),
        disk_id=dict(type='int', required=False),
        size=dict(type='int', required=False),
        state=dict(choices=VAPP_VM_DISK_STATES, required=False),
        operation=dict(choices=VAPP_VM_DISK_OPERATIONS, required=False),
    )


class VappVMDisk(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VappVMDisk, self).__init__(**kwargs)
        vapp_resource = self.get_resource()
        self.vapp = VApp(self.client, resource=vapp_resource)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.add_disk()

        if state == "absent":
            return self.delete_disk()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "update":
            return self.update_disk()

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

    def add_disk(self):
        vm = self.get_vm()
        disk_id = self.params.get('disk_id')
        size = self.params.get('size')
        response = dict()
        response['changed'] = False

        # Some day, we well learn how to add a disk properly.
        # For now, do what pyvcloud does: Copy another disk.
        disks = self.client.get_resource(vm.resource.get('href') + '/virtualHardwareSection/disks')
        base_disk = None
        for disk in disks.Item:
            if disk['{'+NSMAP['rasd']+'}ResourceType'] == 17:
                base_disk = deepcopy(disk)
            if disk_id is not None and disk['{'+NSMAP['rasd']+'}InstanceID'] == disk_id:
                response['warnings'] = 'Disk is already present.'
                return response
        assert base_disk is not None

        address = base_disk['{'+NSMAP['rasd']+'}AddressOnParent'] + 1
        instance_id = base_disk['{'+NSMAP['rasd']+'}InstanceID'] + 1

        base_disk['{'+NSMAP['rasd']+'}AddressOnParent'] = address
        base_disk['{'+NSMAP['rasd']+'}InstanceID'] = instance_id if disk_id is None else disk_id
        base_disk['{'+NSMAP['rasd']+'}Description'] = 'Hard disk'
        base_disk['{'+NSMAP['rasd']+'}ElementName'] = 'Hard disk %s' % address
        base_disk['{'+NSMAP['rasd']+'}VirtualQuantity'] = size*1024*1024
        base_disk['{'+NSMAP['rasd']+'}HostResource'].set('{'+NSMAP['vcloud']+'}capacity', str(size))
        disks.append(base_disk)
        add_disk_task = self.client.put_resource(
            vm.resource.get('href') + '/virtualHardwareSection/disks', disks,
            EntityType.RASD_ITEMS_LIST.value)
        self.execute_task(add_disk_task)

        response['msg'] = 'Vapp VM disk has been added.'
        response['changed'] = True

        return response

    def delete_disk(self):
        vm = self.get_vm()
        disk_id = self.params.get('disk_id')
        response = dict()
        response['changed'] = False

        disks = self.client.get_resource(vm.resource.get('href') + '/virtualHardwareSection/disks')
        for disk in disks.Item:
            if disk['{'+NSMAP['rasd']+'}InstanceID'] == disk_id:
                disks.remove(disk)
                remove_disk_task = self.client.put_resource(
                    vm.resource.get('href') + '/virtualHardwareSection/disks', disks,
                    EntityType.RASD_ITEMS_LIST.value)
                self.execute_task(remove_disk_task)
                response['msg'] = 'VM disk has been deleted.'
                response['changed'] = True
                return response

        response['warnings'] = 'VM disk was not found'
        return response

    def update_disk(self):
        vm = self.get_vm()
        disk_id = self.params.get('disk_id')
        disk_name = self.params.get('disk_name')
        size = self.params.get('size')
        response = dict()
        response['changed'] = False

        disks = self.client.get_resource(vm.resource.get('href') + '/virtualHardwareSection/disks')
        index = -1

        for i, disk in enumerate(disks.Item):
            if disk['{'+NSMAP['rasd']+'}InstanceID'] == disk_id:
                index = i

        if index < 0:
            EntityNotFoundException('Can\'t find the specified VM disk')

        if size:
            disks.Item[index]['{'+NSMAP['rasd']+'}VirtualQuantity'] = size*1024*1024
            disks.Item[index]['{'+NSMAP['rasd']+'}HostResource'].set(
                '{' + NSMAP['vcloud'] + '}capacity', str(size))
            response['changed'] = True

        if disk_name:
            disks.Item[index]['{'+NSMAP['rasd']+'}ElementName'] = disk_name
            response['changed'] = True

        if response['changed']:
            update_disk_task = self.client.put_resource(
                vm.resource.get('href') + '/virtualHardwareSection/disks', disks,
                EntityType.RASD_ITEMS_LIST.value)
            self.execute_task(update_disk_task)
            response['msg'] = 'Vapp VM disk has been updated.'

        return response

def main():
    argument_spec = vapp_vm_disk_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = VappVMDisk(argument_spec=argument_spec, supports_check_mode=True)

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
