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
short_description: Ansible Module to manage disks in vApp VMs in vCloud Director.
version_added: "2.4"
description:
    - "Ansible Module to manage (create/update/delete) disks in vApp VMs."

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
    disks:
        description:
            - List of Disk with its size, and attached controller
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
            - state of disk ('present'/'absent'/'update').
            - One from state or operation has to be provided.
        required: false
    operation:
        description:
            - operation on Disk ('read').
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
    disks:
        - size: 3
          controller: lsilogic
          name: Hard disk 1
    state = "present"
'''

RETURN = '''
msg: success/failure message corresponding to disk state
changed: true if resource has been changed else false
'''

import math
from pyvcloud.vcd.vm import VM
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.client import NSMAP
from pyvcloud.vcd.client import EntityType
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException


VAPP_VM_DISK_STATES = ['present', 'absent', 'update']
VAPP_VM_DISK_OPERATIONS = ['read']


def vapp_vm_disk_argument_spec():
    return dict(
        vm_name=dict(type='str', required=True),
        vapp=dict(type='str', required=True),
        vdc=dict(type='str', required=True),
        disks=dict(type='list', required=False),
        org_name=dict(type='str', required=False, default=None),
        state=dict(choices=VAPP_VM_DISK_STATES, required=False),
        operation=dict(choices=VAPP_VM_DISK_OPERATIONS, required=False),
    )


class VappVMDisk(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VappVMDisk, self).__init__(**kwargs)
        self.org = self.get_org()
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

    def get_formatted_disk_size(self, disk_size):
        '''
            Convert disk byte size into GB or MB
            MB = 1024 * 1024 ( 2 ** 20 )
            GB = 1024 * 1024 * 1024 ( 2 ** 30 )

            Note - only MB and GB are supported from vCD

        '''
        log_value = int(math.floor(math.log(disk_size, 1024)))
        pow_value = math.pow(1024, log_value)
        size_metric = ' MB' if log_value == 2 else ' GB'

        return str(round(disk_size / pow_value, 1)) + size_metric

    def add_disk(self):
        disks = self.params.get('disks')
        vm_name = self.params.get('vm_name')
        response = dict()
        response['msg'] = list()
        response['changed'] = False
        available_disks = self.read_disks().get("disks").keys()
        warnings = list()

        for disk in disks:
            disk_size = int(disk.get("size"))
            disk_controller = disk.get("controller")
            disk_name = disk.get("name")
            '''
            here the condition covers both the situtation
            1. if someone has given the disk name then first it will
            check for disk availability first before adding it.
            2. if someone has ignored giving the disk name then it will
            add a new disk any way.
            '''
            if disk_name not in available_disks:
                add_disk_task = self.vapp.add_disk_to_vm(
                    vm_name, disk_size, disk_controller)
                self.execute_task(add_disk_task)
                msg = "A disk with size {0} and controller {1} has been added to VM {2}"
                msg = msg.format(disk_size, disk_controller, vm_name)
                response['changed'] = True
                response['msg'].append(msg)
            else:
                warnings.append(disk_name)
        if warnings:
            warnings = ','.join(warnings)
            msg = "Hard disk(s) with name '{0}' are already present"
            response["warnings"] = msg.format(warnings)

        return response

    def read_disks(self):
        vm = self.get_vm()
        response = dict()
        response['changed'] = False
        response['disks'] = dict()
        disks = self.client.get_resource(
            vm.resource.get('href') + '/virtualHardwareSection/disks')

        for disk in disks.Item:
            if disk['{' + NSMAP['rasd'] + '}Description'] == "Hard disk":
                disk_name = str(disk['{' + NSMAP['rasd'] + '}ElementName'])
                disk_instance = int(disk['{' + NSMAP['rasd'] + '}InstanceID'])
                disk_size = int(disk['{' + NSMAP['rasd'] + '}VirtualQuantity'])
                disk_hostresource = disk['{' + NSMAP['rasd'] + '}HostResource']
                disk_capacity = int(disk_hostresource.get(
                    '{' + NSMAP['vcloud'] + '}capacity'))
                response['disks'][disk_name] = {
                    'InstanceID': disk_instance,
                    'VirtualQuantity': self.get_formatted_disk_size(disk_size),
                    'HostResource': str(round(disk_capacity / 1024, 1)) + ' GB'
                }

        return response

    def update_disk(self):
        disks = self.params.get('disks')
        response = dict()
        response['changed'] = False
        response['msg'] = list()
        vm = self.get_vm()

        vm_disks = self.client.get_resource(
            vm.resource.get('href') + '/virtualHardwareSection/disks')
        disk_names = [disk.get("name") for disk in disks]
        disk_sizes = [disk.get("size", None) for disk in disks]
        disk_sizes = list(filter(lambda size: size is not None, disk_sizes))
        assert len(disk_sizes) == len(disk_names)

        for index, disk_name in enumerate(disk_names):
            for vm_disk_index, disk in enumerate(vm_disks.Item):
                disk_size = int(disk_sizes[index])
                if disk['{' + NSMAP['rasd'] + '}ElementName'] == disk_name:
                    disk[
                        '{' + NSMAP['rasd'] + '}VirtualQuantity'] = disk_size
                    disk[
                        '{' + NSMAP['rasd'] + '}HostResource'].set(
                        '{' + NSMAP['vcloud'] + '}capacity', str(disk_size))
                vm_disks.Item[vm_disk_index] = disk

        update_disk_task = self.client.put_resource(
            vm.resource.get('href') + '/virtualHardwareSection/disks',
            vm_disks, EntityType.RASD_ITEMS_LIST.value)
        self.execute_task(update_disk_task)
        msg = 'Vapp VM disk with name {0} has been updated.'
        response['msg'].append(msg.format(disk_name))
        response['changed'] = True

        return response

    def delete_disk(self):
        vm = self.get_vm()
        disks = self.params.get('disks')
        disks_to_remove = [disk.get("name") for disk in disks]
        response = dict()
        response['changed'] = False

        disks = self.client.get_resource(vm.resource.get(
            'href') + '/virtualHardwareSection/disks')

        for disk in disks.Item:
            if disk['{' + NSMAP['rasd'] + '}ElementName'] in disks_to_remove:
                disks.remove(disk)
                disks_to_remove.remove(
                    disk['{' + NSMAP['rasd'] + '}ElementName'])

        if len(disks_to_remove) > 0:
            error = 'VM disk(s) with name {0} was not found.'
            error = error.format(','.join(disks_to_remove))
            raise EntityNotFoundException(error)

        remove_disk_task = self.client.put_resource(
            vm.resource.get('href') + '/virtualHardwareSection/disks',
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
        response['changed'] = False
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
