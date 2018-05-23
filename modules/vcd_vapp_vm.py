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
client: vcd_vapp_vm
short_description: This module is to create virtual machines under provided vapp
version_added: "2.4"
description:
    - "This module is to to create virtual machines under provided vapp"
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
    target_vm_name:
        description:
            - target VM name
        required: true
    target_vapp:
        description:
            - target vApp name
        required: true
    target_vdc:
        description:
            - target VDC
        required: true
    source_vapp:
        description:
            - source vApp name
        required: false
    source_vm_name:
        description:
            - source VM name
        required: false
    source_catalog_name:
        description:
            - source catalog name
        required: false
    source_template_name:
        description:
            - source template name
        required: false
    hostname:
        description:
            - target guest hostname
        required: false
    vmpassword:
        description:
            - set the administrator password for target machine
        required: true
    vmpassword_auto:
        description:
            - "true"/"false", autogenerate administrator password
        required: true
    vmpassword_reset:
        description:
            - "true" if the administrator password for this virtual machine must be reset after first use else "false"
        required: false
    cust_script:
        description:
            - script to run on guest customization
        required: false
    network:
        description:
            - Name of the vApp network to connect. If omitted, the VM won't be connected to any network
        required: false
    storage_profile:
        description:
            - the name of the storage profile to be used for this VM
        required: false
    state:
        description:
            - state of new virtual machines ('present'/'absent').One from state or operation has to be provided.
        required: false
    operation:
        description:
            - operations performed over new vapp ('poweron'/'poweroff'/'modifycpu'/'modifymemory'/'reloadvm').One from state or operation has to be provided.
        required: false
    all_eulas_accepted:
        description:
            - "true" / "false"
        required: false
    ip_allocation_mode:
        description:
            - "dhcp"
        required: false
    virtual_cpus:
        description:
            - Number of virtual cpus
        required: false
    cores_per_socket:
        description:
            - Number of cores per socket
        required: false
    memory:
        description:
            - memory size in MB
        required: false

author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_vapp_vm:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    org: Terraform
    api_version: 30
    verify_ssl_certs: False
    target_vm_name = "vm_name"
    target_vapp = "vapp1"
    target_vdc = "vdc1"
    source_vapp = "vapp1"
    source_vm_name = "sourcevm1"
    hostname = "vcdcell"
    vmpassword = "rootpass"
    vmpassword_auto = "false"
    vmpassword_reset = "false"
    cust_script = "/home/setup.sh"
    network = "MGMT"
    storage_profile = "PERFORMACE_1"
    state = "present"
    all_eulas_accepted = "true"
'''

RETURN = '''
result: success/failure message relates to vapp_vm operation
'''

from lxml import etree
from pyvcloud.vcd.vm import VM
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.client import TaskStatus
from pyvcloud.vcd.client import EntityType
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.client import VcdErrorResponseException, MissingLinkException
from ansible.module_utils.vcd_errors import VappVmCreateError


VAPP_VM_STATES = ['present', 'absent']
VAPP_VM_OPERATIONS = ['poweron', 'poweroff',
                      'modifycpu', 'modifymemory', 'reloadvm',
                      'deploy', 'undeploy']


def vapp_vm_argument_spec():
    return dict(
        target_vm_name=dict(type='str', required=True),
        target_vapp=dict(type='str', required=True),
        target_vdc=dict(type='str', required=True),
        source_vdc=dict(type='str', required=True),
        source_vapp=dict(type='str', required=False),
        source_catalog_name=dict(type='str', required=False),
        source_template_name=dict(type='str', required=False),
        source_vm_name=dict(type='str', required=False),
        hostname=dict(type='str', required=False),
        vmpassword=dict(type='str', required=False),
        vmpassword_auto=dict(type='bool', required=False),
        vmpassword_reset=dict(type='bool', required=False),
        cust_script=dict(type='str', required=False),
        network=dict(type='str', required=False),
        storage_profile=dict(type='str', required=False),
        all_eulas_accepted=dict(type='bool', required=False),
        ip_allocation_mode=dict(type='str', required=False),
        virtual_cpus=dict(type='int', required=False),
        cores_per_socket=dict(type='int', required=False),
        memory=dict(type='str', required=False),
        power_on=dict(type='bool', required=False),
        state=dict(choices=VAPP_VM_STATES, required=False),
        operation=dict(choices=VAPP_VM_OPERATIONS, required=False)
    )


def get_vapp_resources(module):
    '''
        If source_vapp and source_catalog both are
        given then priority will be given to
        source_catalog.
    '''
    client = module.client
    source_catalog_name = module.params.get('source_catalog_name', None)
    source_template_name = module.params.get('source_template_name', None)
    target_vapp = module.params.get('target_vapp', None)
    target_vdc = module.params.get('target_vdc', None)
    source_vdc = module.params.get('source_vdc', None)
    source_vapp = module.params.get('source_vapp', None)
    org_resource = Org(client, resource=client.get_org())

    if source_vapp:
        source_vdc_resource = VDC(
            client, resource=org_resource.get_vdc(source_vdc))
        target_vdc_resource = VDC(
            client, resource=org_resource.get_vdc(target_vdc))
        source_vapp_resource_href = source_vdc_resource.get_resource_href(
            name=source_vapp, entity_type=EntityType.VAPP)
        target_vapp_resource_href = target_vdc_resource.get_resource_href(
            name=target_vapp, entity_type=EntityType.VAPP)
        source_vapp_resource = client.get_resource(source_vapp_resource_href)
        target_vapp_resource = client.get_resource(target_vapp_resource_href)

    if source_catalog_name:
        target_vdc_resource = VDC(
            client, resource=org_resource.get_vdc(target_vdc))
        target_vapp_resource = target_vdc_resource.get_vapp(target_vapp)
        catalog_item = org_resource.get_catalog_item(
            source_catalog_name, source_template_name)
        source_vapp_resource = client.get_resource(
            catalog_item.Entity.get('href'))

    return source_vapp_resource, target_vapp_resource


class VappVM(object):
    def __init__(self, module, vapp_resource):
        self.module = module
        self.vapp = VApp(module.client, resource=vapp_resource)

    def execute_task(self, task_monitor, task):
        task_state = task_monitor.wait_for_status(
            task=task,
            timeout=60,
            poll_frequency=2,
            fail_on_statuses=None,
            expected_target_statuses=[
                TaskStatus.SUCCESS, TaskStatus.ABORTED, TaskStatus.ERROR,
                TaskStatus.CANCELED
            ],
            callback=None)

        task_status = task_state.get('status')
        if task_status != TaskStatus.SUCCESS.value:
            raise VappVmCreateError(etree.tostring(
                task_state, pretty_print=True))

        return 1

    def get_vm(self, vm_name):
        vapp_vm_resource = self.vapp.get_vm(vm_name)

        return VM(self.module.client, resource=vapp_vm_resource)

    def add_vms(self, source_vapp_resource):
        client = self.module.client
        params = self.module.params
        source_vm_name = params.get('source_vm_name')
        target_vm_name = params.get('target_vm_name')
        hostname = params.get('hostname')
        vmpassword = params.get('vmpassword')
        vmpassword_auto = params.get('vmpassword_auto')
        vmpassword_reset = params.get('vmpassword_reset')
        network = params.get('network')
        all_eulas_accepted = params.get('all_eulas_accepted', True)
        power_on = params.get('power_on', True)
        ip_allocation_mode = params.get('ip_allocation_mode')

        # cust_script = module.params.get('cust_script')
        # storage_profile = module.params.get('storage_profile')

        specs = [{
            'source_vm_name': source_vm_name,
            'vapp': source_vapp_resource,
            'target_vm_name': target_vm_name,
            'hostname': hostname,
            'password': vmpassword,
            'password_auto': vmpassword_auto,
            'password_reset': vmpassword_reset,
            'ip_allocation_mode': ip_allocation_mode,
            'network': network,
            # 'cust_script': cust_script,
            # 'storage_profile': storage_profile
        }]

        vm_operation_res = self.vapp.add_vms(specs,
                                             power_on=power_on,
                                             all_eulas_accepted=all_eulas_accepted)
        task_monitor = client.get_task_monitor()

        return self.execute_task(task_monitor, vm_operation_res)

    def delete_vms(self, vm_name):
        client = self.module.client

        self.undeploy_vm(vm_name)
        vm_operation_res = self.vapp.delete_vms([vm_name])
        task_monitor = client.get_task_monitor()

        return self.execute_task(task_monitor, vm_operation_res)

    def power_on_vm(self, vm_name):
        try:
            client = self.module.client
            vm = self.get_vm(vm_name)
            power_on_response = vm.power_on()
            task_monitor = client.get_task_monitor()

            return self.execute_task(task_monitor, power_on_response)

        except VcdErrorResponseException:
            # in case if VM is already powered on
            pass

    def power_off_vm(self, vm_name):
        try:
            client = self.module.client
            vm = self.get_vm(vm_name)
            vm_operation_res = vm.power_off()
            task_monitor = client.get_task_monitor()

            return self.execute_task(task_monitor, vm_operation_res)

        except VcdErrorResponseException:
            # in case if VM is already powered off
            pass

    def reload_vm(self, vm_name):
        vm = self.get_vm(vm_name)

        return vm.reload()

    def modify_cpu_of_vm(self, vm_name):
        params = self.module.params
        client = self.module.client
        vm = self.get_vm(vm_name)
        virtual_cpus = params.get('virtual_cpus')
        cores_per_socket = params.get('cores_per_socket')

        self.power_off_vm(vm_name)
        modify_cpu_response = vm.modify_cpu(virtual_cpus, cores_per_socket)
        task_monitor = client.get_task_monitor()

        return self.execute_task(task_monitor, modify_cpu_response)

    def modify_memory_of_vm(self, vm_name):
        params = self.module.params
        client = self.module.client
        vm = self.get_vm(vm_name)
        memory = params.get('memory')

        self.power_off_vm(vm_name)
        modify_memory_response = vm.modify_memory(memory)
        task_monitor = client.get_task_monitor()

        return self.execute_task(task_monitor, modify_memory_response)

    def deploy_vm(self, vm_name):
        try:
            client = self.module.client
            vm = self.get_vm(vm_name)
            vm_operation_res = vm.deploy()
            task_monitor = client.get_task_monitor()

            return self.execute_task(task_monitor, vm_operation_res)

        except MissingLinkException:
            # in case if VM is already deployed
            pass

    def undeploy_vm(self, vm_name):
        try:
            client = self.module.client
            vm = self.get_vm(vm_name)
            vm_operation_res = vm.undeploy()
            task_monitor = client.get_task_monitor()

            return self.execute_task(task_monitor, vm_operation_res)

        except MissingLinkException:
            # in case if VM is already undeployed
            pass


def manage_states(module, vApp, source_vapp_resource):
    state = module.params.get('state')
    target_vm_name = module.params.get('target_vm_name')
    if state == "present":
        vApp.add_vms(source_vapp_resource)
        return 'Vapp VM {} has been created.'.format(target_vm_name)

    if state == "absent":
        vApp.delete_vms(target_vm_name)
        return 'Vapp VM {} has been deleted.'.format(target_vm_name)


def manage_operations(module, vApp):
    operation = module.params.get('operation')
    target_vm_name = module.params.get('target_vm_name')

    if operation == "poweron":
        vApp.power_on_vm(target_vm_name)
        return 'Vapp VM {} has been powered on.'.format(target_vm_name)

    if operation == "poweroff":
        vApp.power_off_vm(target_vm_name)
        return 'Vapp VM {} has been powered off.'.format(target_vm_name)

    if operation == "modifycpu":
        vApp.modify_cpu_of_vm(target_vm_name)
        return 'Vapp VM {} has been updated.'.format(target_vm_name)

    if operation == "modifymemory":
        vApp.modify_memory_of_vm(target_vm_name)
        return 'Vapp VM {} has been updated.'.format(target_vm_name)

    if operation == "reloadvm":
        vApp.reload_vm(target_vm_name)
        return 'Vapp VM {} has been reloaded.'.format(target_vm_name)

    if operation == "deploy":
        vApp.deploy_vm(target_vm_name)
        return 'Vapp VM {} has been deployed.'.format(target_vm_name)

    if operation == "undeploy":
        vApp.undeploy_vm(target_vm_name)
        return 'Vapp VM {} has been undeployed.'.format(target_vm_name)


def main():
    argument_spec = vapp_vm_argument_spec()
    response = dict(
        msg=dict(type='str')
    )

    module = VcdAnsibleModule(
        argument_spec=argument_spec, supports_check_mode=True)

    try:
        source_vapp_resource, target_vapp_resource = get_vapp_resources(module)
        vApp = VappVM(module, target_vapp_resource)

        if module.params.get('state'):
            response['msg'] = manage_states(module, vApp, source_vapp_resource)
        elif module.params.get('operation'):
            response['msg'] = manage_operations(module, vApp)
        else:
            raise Exception('One of from state/operation should be provided.')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    response['changed'] = True
    module.exit_json(**response)


if __name__ == '__main__':
    main()
