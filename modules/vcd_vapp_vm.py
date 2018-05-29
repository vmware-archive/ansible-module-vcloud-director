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
        required: false
    target_vapp:
        description:
            - target vApp name
        required: false
    target_vdc:
        description:
            - target VDC
        required: false
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
        required: false
    vmpassword_auto:
        description:
            - "true"/"false", autogenerate administrator password
        required: false
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
from ansible.module_utils.vcd_errors import VappVmCreateError


VAPP_VM_STATES = ['present', 'absent']
VAPP_VM_OPERATIONS = ['poweron', 'poweroff',
                      'updatecpu', 'updatememory', 'reloadvm',
                      'deploy', 'undeploy']


def vapp_vm_argument_spec():
    return dict(
        target_vm_name=dict(type='str', required=False),
        target_vapp=dict(type='str', required=False),
        target_vdc=dict(type='str', required=False),
        source_vdc=dict(type='str', required=False),
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

    def execute_task(self, task):
        client = self.module.client
        task_monitor = client.get_task_monitor()
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
            raise VappVmCreateError(etree.tostring(task_state, pretty_print=True))

        return 1

    def get_vm(self, vm_name):
        vapp_vm_resource = self.vapp.get_vm(vm_name)

        return VM(self.module.client, resource=vapp_vm_resource)

    def add_vms(self, target_vm_name, source_vapp_resource):
        params = self.module.params
        source_vm_name = params.get('source_vm_name')
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
        response = dict()

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
        add_vms_task = self.vapp.add_vms(specs, power_on=power_on,
                                         all_eulas_accepted=all_eulas_accepted)
        self.execute_task(add_vms_task)
        response['msg'] = 'Vapp VM {} has been created.'.format(target_vm_name)
        response['changed'] = True

        return response

    def delete_vms(self, vm_name):
        response = dict()

        self.undeploy_vm(vm_name)
        delete_vms_task = self.vapp.delete_vms([vm_name])
        self.execute_task(delete_vms_task)
        response['msg'] = 'Vapp VM {} has been deleted.'.format(vm_name)
        response['changed'] = True

        return response

    def power_on_vm(self, vm_name):
        vm = self.get_vm(vm_name)
        response = dict()

        power_on_task = vm.power_on()
        self.execute_task(power_on_task)
        response['msg'] = 'Vapp VM {} has been powered on.'.format(vm_name)
        response['changed'] = True

        return response

    def power_off_vm(self, vm_name):
        vm = self.get_vm(vm_name)
        response = dict()

        power_off_task = vm.power_off()
        self.execute_task(power_off_task)
        response['msg'] = 'Vapp VM {} has been powered off.'.format(vm_name)
        response['changed'] = True

        return response

    def reload_vm(self, vm_name):
        vm = self.get_vm(vm_name)
        response = dict()

        vm.reload()
        response['msg'] = 'Vapp VM {} has been reloaded.'.format(vm_name)
        response['changed'] = True

        return response

    def update_cpu_of_vm(self, vm_name):
        params = self.module.params
        vm = self.get_vm(vm_name)
        virtual_cpus = params.get('virtual_cpus')
        cores_per_socket = params.get('cores_per_socket')
        response = dict()

        self.power_off_vm(vm_name)
        update_cpu_task = vm.modify_cpu(virtual_cpus, cores_per_socket)
        self.execute_task(update_cpu_task)
        response['msg'] = 'Vapp VM {} has been updated.'.format(vm_name)
        response['changed'] = True

        return response

    def update_memory_of_vm(self, vm_name):
        params = self.module.params
        vm = self.get_vm(vm_name)
        memory = params.get('memory')
        response = dict()

        self.power_off_vm(vm_name)
        update_memory_task = vm.modify_memory(memory)
        self.execute_task(update_memory_task)
        response['msg'] = 'Vapp VM {} has been updated.'.format(vm_name)
        response['changed'] = True

        return response

    def deploy_vm(self, vm_name):
        vm = self.get_vm(vm_name)
        response = dict()

        deploy_vm_task = vm.deploy()
        self.execute_task(deploy_vm_task)
        response['msg'] = 'Vapp VM {} has been deployed.'.format(vm_name)
        response['changed'] = True

        return response

    def undeploy_vm(self, vm_name):
        vm = self.get_vm(vm_name)
        response = dict()

        undeploy_vm_task = vm.undeploy()
        self.execute_task(undeploy_vm_task)
        response['msg'] = 'Vapp VM {} has been undeployed.'.format(vm_name)
        response['changed'] = True

        return response


def manage_vappvm_states(vApp, source_vapp_resource):
    params = vApp.module.params
    state = params.get('state')
    target_vm_name = params.get('target_vm_name')
    if state == "present":
        return vApp.add_vms(target_vm_name, source_vapp_resource)

    if state == "absent":
        return vApp.delete_vms(target_vm_name)


def manage_vappvm_operations(vApp):
    params = vApp.module.params
    operation = params.get('operation')
    target_vm_name = params.get('target_vm_name')

    if operation == "poweron":
        return vApp.power_on_vm(target_vm_name)

    if operation == "poweroff":
        return vApp.power_off_vm(target_vm_name)

    if operation == "updatecpu":
        return vApp.update_cpu_of_vm(target_vm_name)

    if operation == "updatememory":
        return vApp.update_memory_of_vm(target_vm_name)

    if operation == "reloadvm":
        return vApp.reload_vm(target_vm_name)

    if operation == "deploy":
        return vApp.deploy_vm(target_vm_name)

    if operation == "undeploy":
        return vApp.undeploy_vm(target_vm_name)


def main():
    argument_spec = vapp_vm_argument_spec()
    response = dict(
        msg=dict(type='str')
    )

    module = VcdAnsibleModule(argument_spec=argument_spec,
                              supports_check_mode=True)

    try:
        source_vapp_resource, target_vapp_resource = get_vapp_resources(module)
        vApp = VappVM(module, target_vapp_resource)

        if module.params.get('state'):
            response = manage_vappvm_states(vApp, source_vapp_resource)
        elif module.params.get('operation'):
            response = manage_vappvm_operations(vApp)
        else:
            raise Exception('One of from state/operation should be provided.')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
