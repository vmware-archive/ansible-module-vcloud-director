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
module: vcd_vapp_vm
short_description: Manage VM snapshots states/operations in vCloud Director
version_added: "2.4"
description:
    - Manage VM snapshots states/operations in vCloud Director

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
    vdc_name:
        description:
            - vCloud Director ORG VDC Name
        required: true
    vapp_name:
        description:
            - vApp Name which VM is part of
        required: true
    vms:
        description:
            - Name of Virtual Machines
        required: true
        type:
            - list
    state:
        description:
            - state of virtual machine snapshots (present/absent)
        required: false
    operation:
        description:
            - operation of virtual machine snapshots (revert)
        required: false
author:
    - mtaneja@vmware.com
'''

RETURN = '''
msg: success/failure message corresponding to vapp vm snapshot state
changed: true if resource has been changed else false
'''

import math
from pyvcloud.vcd.vm import VM
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import OperationNotSupportedException


VM_SNAPSHOT_OPERATIONS = ['revert', 'list']
VM_SNAPSHOT_STATES = ['present', 'absent']


def vm_snapshot_argument_spec():
    return dict(
        vdc_name=dict(type='str', required=True),
        vapp_name=dict(type='str', required=True),
        vms=dict(type='list', required=True),
        org_name=dict(type='str', required=False, default=None),
        state=dict(choices=VM_SNAPSHOT_STATES, required=False),
        operation=dict(choices=VM_SNAPSHOT_OPERATIONS, required=False),
    )


class VMSnapShot(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VMSnapShot, self).__init__(**kwargs)
        self.org = self.get_org()

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.create_snapshot()

        if state == "absent":
            return self.delete_snapshot()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "revert":
            return self.revert_snapshot()

        if operation == "list":
            return self.list_snapshots()

    def get_org(self):
        org_name = self.params.get('org_name')
        org_resource = self.client.get_org()
        if org_name:
            org_resource = self.client.get_org_by_name(org_name)

        return Org(self.client, resource=org_resource)

    def get_vm(self, vm_name):
        vapp_name = self.params.get('vapp_name')
        vdc_name = self.params.get('vdc_name')
        vdc_resource = VDC(
            self.client, resource=self.org.get_vdc(vdc_name))
        vapp_resource = vdc_resource.get_vapp(vapp_name)
        vapp = VApp(self.client, resource=vapp_resource)

        return VM(self.client, resource=vapp.get_vm(vm_name))

    def create_snapshot(self):
        response = dict()
        response['changed'] = False
        vms = self.params.get("vms")
        for vm in vms:
            vm_name = vm.get("name")
            mem_snapshot = vm.get("mem_snapshot")
            vm_quiesce = vm.get("vm_quiesce")
            snapshot_name = vm.get("snapshot_name", vm_name)
            vm = self.get_vm(vm_name)
            create_task = vm.snapshot_create(
                memory=mem_snapshot, quiesce=vm_quiesce, name=snapshot_name)
            self.execute_task(create_task)

        msg = "Snapshot(s) have been created of VMs {0}"
        response['msg'] = msg.format([vm.get("name") for vm in vms])
        response['changed'] = True

        return response

    def delete_snapshot(self):
        response = dict()
        response['changed'] = False
        vms = self.params.get("vms")
        warnings = list()
        operated_vms = list()
        for vm in vms:
            try:
                vm_name = vm.get("name")
                vm = self.get_vm(vm_name)
                delete_task = vm.snapshot_remove_all()
                self.execute_task(delete_task)
                operated_vms.append(vm_name)
            except (OperationNotSupportedException, Exception) as ex:
                warnings.append({vm_name: str(ex)})
        if operated_vms:
            msg = "All snapshots for VMs {0} has been deleted"
            response['msg'] = msg.format(operated_vms)
            response['changed'] = True
        if warnings:
            response['warnings'] = str(warnings)

        return response

    def revert_snapshot(self):
        response = dict()
        response['changed'] = False
        vms = self.params.get("vms")
        warnings = list()
        operated_vms = list()
        for vm in vms:
            try:
                vm_name = vm.get("name")
                vm = self.get_vm(vm_name)
                revert_task = vm.snapshot_revert_to_current()
                self.execute_task(revert_task)
                operated_vms.append(vm_name)
            except (OperationNotSupportedException, Exception) as ex:
                warnings.append({vm_name: str(ex)})
        if operated_vms:
            msg = "VMs {0} has been reverted to current snapshot successfully"
            response['msg'] = msg.format(operated_vms)
            response['changed'] = True
        if warnings:
            response['warnings'] = str(warnings)

        return response

    def get_formatted_snapshot_size(self, snapshot_size):
        '''
            Convert disk byte size into GB or MB
            MB = 1024 * 1024 ( 2 ** 20 )
            GB = 1024 * 1024 * 1024 ( 2 ** 30 )

            Note - only MB and GB are supported from vCD

        '''
        log_value = int(math.floor(math.log(snapshot_size, 1024)))
        pow_value = math.pow(1024, log_value)
        size_metric = ' MB' if log_value == 2 else ' GB'

        return str(round(snapshot_size / pow_value, 1)) + size_metric

    def list_snapshots(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()
        vms = self.params.get("vms")
        warnings = list()
        for vm in vms:
            try:
                vm_name = vm.get("name")
                vm = self.get_vm(vm_name)
                snapshot = dict()
                for key, value in vm.resource.SnapshotSection.Snapshot.items():
                    if key == "size":
                        value = self.get_formatted_snapshot_size(float(value))
                    snapshot[key] = value
                response['msg'].append({
                    "vm_name": vm_name,
                    "snapshot": snapshot
                })
            except (OperationNotSupportedException, Exception) as ex:
                warnings.append({vm_name: str(ex)})
        if warnings:
            response['warnings'] = str(warnings)

        return response


def main():
    argument_spec = vm_snapshot_argument_spec()
    response = dict(msg=dict(type='str'))
    module = VMSnapShot(argument_spec=argument_spec, supports_check_mode=True)

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
