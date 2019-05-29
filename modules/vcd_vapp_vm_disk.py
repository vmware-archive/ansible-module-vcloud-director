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
module: vcd_vapp_vm_disk
short_description: Ansible Module to manage (create/update/delete) Disks in vApp VMs in vCloud Director.
version_added: "2.4"
description:
    - "Ansible Module to manage (create/update/delete) Disks in vApp VMs."

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
    disk_name:
        description:
            - Disk Name
        required: false
    disks:
        description:
            - List of Disk Names
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
            - operation on Disk ('update'/'read').
            - One from state or operation has to be provided.
        required: false
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
    disk_name = "Hard disk 1"
    size = "2147483648"
    state = "present"
'''

RETURN = '''
msg: success/failure message corresponding to disk state
changed: true if resource has been changed else false
'''

import math
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.vm import VM
from pyvcloud.vcd.client import EntityType
from pyvcloud.vcd.client import NSMAP
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException


VAPP_VM_DISK_STATES = ['present', 'absent', 'update']
VAPP_VM_DISK_OPERATIONS = ['read']


def vapp_vm_disk_argument_spec():
    return dict(
        vm_name=dict(type='str', required=True),
        vapp=dict(type='str', required=True),
        vdc=dict(type='str', required=True),
        disk_name=dict(type='str', required=False),
        disks=dict(type='list', required=False),
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

        if state == "update":
            return self.update_disk()

        if state == "absent":
            return self.delete_disk()

    def manage_operations(self):
        operation = self.params.get('operation')

        if operation == "read":
            return self.read_disks()

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

    def add_disk(self):
        size = self.params.get('size')
        vm_name = self.params.get('vm_name')
        response = dict()
        response['changed'] = False

        disks = self.read_disks().get('disks')
        last_disk = list(disks.keys())[-1]
        last_disk_instance_id = int(disks[last_disk]['InstanceID'])
        new_disk_name = str(int(last_disk.split(' ')[2]) + 1)
        new_disk_instance_id = last_disk_instance_id + 1
        add_disk_task = self.vapp.add_disk_to_vm(vm_name, size)
        self.execute_task(add_disk_task)
        msg = 'Vapp VM disk of size {0} has been added.'
        response['msg'] = msg.format(str(size))
        response['metadata'] = {
            'new_disk_name': 'Hard disk {0}'.format(new_disk_name),
            'new_disk_size': size,
            'new_disk_instance_id': new_disk_instance_id
        }
        response['changed'] = True

        return response

    def read_disks(self):
        vm = self.get_vm()
        response = dict()
        response['changed'] = False
        response['disks'] = dict()
        disks = self.client.get_resource(vm.resource.get('href') + '/virtualHardwareSection/disks')
        for disk in disks.Item:
            if disk['{' + NSMAP['rasd'] + '}Description'] == "Hard disk":
                disk_name = str(disk['{' + NSMAP['rasd'] + '}ElementName'])
                disk_instance = int(disk['{' + NSMAP['rasd'] + '}InstanceID'])
                disk_size = int(disk['{' + NSMAP['rasd'] + '}VirtualQuantity'])
                disk_hostresource = disk['{' + NSMAP['rasd'] + '}HostResource']
                disk_capacity = int(disk_hostresource.get('{' + NSMAP['vcloud'] + '}capacity'))
                response['disks'][disk_name] = {
                    'InstanceID': disk_instance,
                    'VirtualQuantity': self.convert_bytes_to_gb(disk_size),
                    'HostResource': str(round(disk_capacity / 1024, 1)) + ' GB'
                }

        return response

    def convert_bytes_to_gb(self, disk_size):
        log_value = int(math.floor(math.log(disk_size, 1024)))
        pow_value = math.pow(1024, log_value)

        return str(round(disk_size / pow_value, 1)) + ' GB'

    def update_disk(self):
        vm = self.get_vm()
        disk_name = self.params.get('disk_name')
        size = self.params.get('size')
        response = dict()
        response['changed'] = False
        index = -1

        if not size:
            err = '''Hard disk size argument is missing. Disk \'update\' operation only allows disk size to be updated
            for the exisiting VM\'s.'''
            raise Exception(err)

        disks = self.client.get_resource(vm.resource.get('href') + '/virtualHardwareSection/disks')
        for i, disk in enumerate(disks.Item):
            if disk['{' + NSMAP['rasd'] + '}ElementName'] == disk_name:
                index = i

        if index < 0:
            err = 'Can\'t find the specified VM disk with name {0}'
            err = err.format(disk_name)
            raise EntityNotFoundException(err)

        disk_size = int(disks.Item[index]['{' + NSMAP['rasd'] + '}VirtualQuantity'])
        if disk_size == (size * 1024 * 1024):
            msg = 'Vapp VM disk with name {0} already has target size {1}.'
            response['msg'] = msg.format(disk_name,self.convert_bytes_to_gb(size * 1024 * 1024))
        elif disk_size > (size * 1024 * 1024):
            msg = 'Vapp VM disk with name {0} may only be increased, not decreased: current size {1}.'
            response['msg'] = msg.format(disk_name,self.convert_bytes_to_gb(disk_size))
            response['failed'] = True
        else:
            disks.Item[index]['{' + NSMAP['rasd'] + '}VirtualQuantity'] = size * 1024 * 1024
            disks.Item[index]['{' + NSMAP['rasd'] + '}HostResource'].set(
                '{' + NSMAP['vcloud'] + '}capacity', str(size))
            update_disk_task = self.client.put_resource(
                vm.resource.get('href') +
                '/virtualHardwareSection/disks', disks, EntityType.RASD_ITEMS_LIST.value)
            self.execute_task(update_disk_task)

            msg = 'Vapp VM disk with name {0} has been updated.'
            response['msg'] = msg.format(disk_name)
            response['changed'] = True

        return response

    def delete_disk(self):
        vm = self.get_vm()
        disks_to_remove = self.params.get('disks')
        response = dict()
        response['changed'] = False

        disks = self.client.get_resource(vm.resource.get('href') + '/virtualHardwareSection/disks')

        for disk in disks.Item:
            if disk['{' + NSMAP['rasd'] + '}ElementName'] in disks_to_remove:
                disks.remove(disk)
                disks_to_remove.remove(disk['{' + NSMAP['rasd'] + '}ElementName'])

        if len(disks_to_remove) > 0:
            err = 'VM disk(s) with name {0} was not found.'
            err = err.format(','.join(disks_to_remove))

            raise EntityNotFoundException(err)

        remove_disk_task = self.client.put_resource(vm.resource.get(
            'href') + '/virtualHardwareSection/disks',
            disks, EntityType.RASD_ITEMS_LIST.value)
        self.execute_task(remove_disk_task)
        response['msg'] = 'VM disk(s) has been deleted.'
        response['changed'] = True

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
        response['changed'] = False
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
