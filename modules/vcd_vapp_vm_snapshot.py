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
short_description: Ansible Module to manage (create/delete) VM snapshots in vApps in vCloud Director.
version_added: "2.4"
description:
    - "Ansible Module to manage (create/delete) VM snapshots in vApps."

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
    vdc_name:
        description:
            - vCloud Director ORG VDC Name
        required: true
    vapp_name:
        description:
            - vApp Name which VM is part of
        required: true
    vm_name:
        description:
            - Name of Virtual Machine
        required: true
    snapshot_name:
        description:
            - Name of Virtual Machine's snapshot
        required: false
    mem_snapshot:
        description:
            - boolean flag true if snapshot should include Virtual Machine's memory else false
        required: false
    vm_quiesce:
        description:
            - boolean flag true if the file system of the Virtual Machine
              should be quiesced before the snapshot is created. Requires VMware
              tools to be installed on the vm else false
        required: false
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

from pyvcloud.vcd.vm import VM
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from ansible.module_utils.vcd import VcdAnsibleModule


VM_SNAPSHOT_OPERATIONS = ['revert']
VM_SNAPSHOT_STATES = ['present', 'absent']


def vm_snapshot_argument_spec():
    return dict(
        vdc_name=dict(type='str', required=True),
        vapp_name=dict(type='str', required=True),
        vm_name=dict(type='str', required=True),
        snapshot_name=dict(type='str', required=False),
        mem_snapshot=dict(type='bool', required=False, default=None),
        vm_quiesce=dict(type='bool', required=False, default=None),
        state=dict(choices=VM_SNAPSHOT_STATES, required=False),
        operation=dict(choices=VM_SNAPSHOT_OPERATIONS, required=False),
    )


class VMSnapShot(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VMSnapShot, self).__init__(**kwargs)
        self.vm = self.get_vm()

    def get_vm(self):
        vapp_name = self.params.get('vapp_name')
        vdc_name = self.params.get('vdc_name')
        vm_name = self.params.get('vm_name')
        org_resource = Org(self.client, resource=self.client.get_org())
        vdc_resource = VDC(self.client, resource=org_resource.get_vdc(vdc_name))
        vapp_resource = vdc_resource.get_vapp(vapp_name)
        vapp = VApp(self.client, resource=vapp_resource)

        return VM(self.client, resource=vapp.get_vm(vm_name))

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

    def create_snapshot(self):
        response = dict()
        response['changed'] = False
        vm_name = self.params.get("vm_name")
        vm_quiesce = self.params.get('vm_quiesce')
        mem_snapshot = self.params.get('mem_snapshot')
        snapshot_name = self.params.get("snapshot_name")
        snapshot_name = snapshot_name if snapshot_name else "{0}_snapshot".format(vm_name)
        create_task = self.vm.snapshot_create(memory=mem_snapshot, quiesce=vm_quiesce, name=snapshot_name)
        self.execute_task(create_task)
        response['msg'] = "Snapshot {0} has been created of VM {1}".format(snapshot_name, vm_name)
        response['changed'] = True

        return response

    def delete_snapshot(self):
        response = dict()
        response['changed'] = False
        vm_name = self.params.get("vm_name")
        delete_task = self.vm.snapshot_remove_all()
        self.execute_task(delete_task)
        response['msg'] = "All snapshots for VM {0} has been deleted".format(vm_name)
        response['changed'] = True

        return response

    def revert_snapshot(self):
        response = dict()
        response['changed'] = False
        vm_name = self.params.get("vm_name")
        revert_task = self.vm.snapshot_revert_to_current()
        self.execute_task(revert_task)
        response['msg'] = "VM {0} has been reverted to current snapshot successfully".format(vm_name)
        response['changed'] = True

        return response


def main():
    argument_spec = vm_snapshot_argument_spec()
    response = dict(msg=dict(type='str'))
    module = VMSnapShot(argument_spec=argument_spec, supports_check_mode=True)

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
