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
short_description: Manage VM's state/operations in vCloud Director
version_added: "2.4"
description:
    - Manage VM's state/operations in vCloud Director

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
    target_vm_name:
        description:
            - target VM name
        required: true
    target_vapp:
        description:
            - target vApp name
        required: true
    source_vdc:
        description:
            - source VDC
        required: false
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
        required: false
    vmpassword_auto:
        description:
            - true/false, autogenerate administrator password
        required: false
    vmpassword_reset:
        description:
            - true/false to reset administrator password
        required: false
    cust_script:
        description:
            - script to run on guest customization
        required: false
    network:
        description:
            - Name of the vApp network to connect
            - If omitted, the VM won't be connected to any network
        required: false
    storage_profile:
        description:
            - the name of the storage profile to be used for this VM
        required: false
    all_eulas_accepted:
        description:
            - true / false
        required: false
    ip_allocation_mode:
        description:
            - dhcp
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
    deploy:
        description:
            - deploy VMs
        required: false
    power_on:
        description:
            - power on VMs
        required: false
    state:
        description:
            - state of new virtual machines (present/absent)
            - One from state or operation has to be provided
        required: false
    operation:
        description:
            - operation to perform on new vapp
            - Available operations are
                - poweron
                - poweroff
                - modifycpu
                - modifymemory
                - reloadvm
                - list_disks
                - list_nics
            - One from state or operation has to be provided.
        required: false
    force_customization:
        description:
            - whether or not to force customization
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
    storage_profile = "Standard"
    state = "present"
    all_eulas_accepted = "true"
    properties = {"hostname": "vm_name"}
'''

RETURN = '''
msg: success/failure message corresponding to vapp vm state/operation
changed: true if resource has been changed else false
'''

from lxml import etree
from pyvcloud.vcd.vm import VM
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.client import E
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.client import E_OVF
from pyvcloud.vcd.client import NSMAP
from pyvcloud.vcd.client import EntityType
from pyvcloud.vcd.client import RelationType
from pyvcloud.vcd.client import MetadataDomain
from pyvcloud.vcd.client import MetadataValueType
from pyvcloud.vcd.client import MetadataVisibility
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException, OperationNotSupportedException


VAPP_VM_STATES = ['present', 'absent', 'update']
VAPP_VM_METADATA_DOMAINS = ['GENERAL', 'SYSTEM']
VAPP_VM_METADATA_VISIBILITY = ['PRIVATE', 'READONLY', 'READWRITE']
VAPP_VM_SET_METADATA_VALUE_TYPE = ['String', 'Number', 'Boolean', 'DateTime']
VAPP_VM_OPERATIONS = ['poweron', 'poweroff', 'reloadvm',
                      'deploy', 'undeploy', 'list_disks', 'list_nics',
                      'set_meta', 'get_meta', 'remove_meta']


def vapp_vm_argument_spec():
    return dict(
        target_vm_name=dict(type='str', required=True),
        target_vapp=dict(type='str', required=True),
        target_vdc=dict(type='str', required=True),
        source_vdc=dict(type='str', required=False),
        source_vapp=dict(type='str', required=False),
        source_catalog_name=dict(type='str', required=False),
        source_template_name=dict(type='str', required=False),
        source_vm_name=dict(type='str', required=False),
        hostname=dict(type='str', required=False),
        vmpassword=dict(type='str', required=False),
        vmpassword_auto=dict(type='bool', required=False),
        vmpassword_reset=dict(type='bool', required=False),
        cust_script=dict(type='str', required=False, default=''),
        network=dict(type='str', required=False),
        storage_profile=dict(type='str', required=False, default=''),
        ip_allocation_mode=dict(type='str', required=False, default='DHCP'),
        virtual_cpus=dict(type='int', required=False),
        cores_per_socket=dict(type='int', required=False, default=None),
        memory=dict(type='int', required=False),
        deploy=dict(type='bool', required=False, default=True),
        power_on=dict(type='bool', required=False, default=True),
        all_eulas_accepted=dict(type='bool', required=False, default=None),
        metadata=dict(type='dict', required=False, default=None),
        metadata_type=dict(type='str', required=False, default='String',
                           choices=VAPP_VM_SET_METADATA_VALUE_TYPE),
        metadata_visibility=dict(type='str', required=False,
                                 default='READWRITE',
                                 choices=VAPP_VM_METADATA_VISIBILITY),
        metadata_domain=dict(type='str', required=False, default='GENERAL',
                             choices=VAPP_VM_METADATA_DOMAINS),
        org_name=dict(type='str', required=False, default=None),
        force_customization=dict(type='bool', required=False, default=False),
        state=dict(choices=VAPP_VM_STATES, required=False),
        operation=dict(choices=VAPP_VM_OPERATIONS, required=False),
        compute_policy_href=dict(type='str', required=False)
    )


class VappVM(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VappVM, self).__init__(**kwargs)
        self.org = self.get_org()
        vapp_resource = self.get_target_resource()
        self.vapp = VApp(self.client, resource=vapp_resource)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.add_vm()

        if state == "absent":
            return self.delete_vm()

        if state == "update":
            return self.update_vm()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "poweron":
            return self.power_on_vm()

        if operation == "poweroff":
            return self.power_off_vm()

        if operation == "reloadvm":
            return self.reload_vm()

        if operation == "deploy":
            return self.deploy_vm()

        if operation == "undeploy":
            return self.undeploy_vm()

        if operation == "list_disks":
            return self.list_disks()

        if operation == "list_nics":
            return self.list_nics()

        if operation == "set_meta":
            return self.set_meta()

        if operation == "get_meta":
            return self.get_meta()

        if operation == "remove_meta":
            return self.remove_meta()

    def get_org(self):
        org_name = self.params.get('org_name')
        org_resource = self.client.get_org()
        if org_name:
            org_resource = self.client.get_org_by_name(org_name)

        return Org(self.client, resource=org_resource)

    def get_source_resource(self):
        source_catalog_name = self.params.get('source_catalog_name')
        source_template_name = self.params.get('source_template_name')
        source_vdc = self.params.get('source_vdc')
        source_vapp = self.params.get('source_vapp')
        source_vapp_resource = None

        if source_vapp:
            source_vdc_resource = VDC(
                self.client, resource=self.org.get_vdc(source_vdc))
            source_vapp_resource_href = source_vdc_resource.get_resource_href(
                name=source_vapp, entity_type=EntityType.VAPP)
            source_vapp_resource = self.client.get_resource(
                source_vapp_resource_href)

        if source_catalog_name:
            catalog_item = self.org.get_catalog_item(
                source_catalog_name, source_template_name)
            source_vapp_resource = self.client.get_resource(
                catalog_item.Entity.get('href'))

        return source_vapp_resource

    def get_target_resource(self):
        target_vapp = self.params.get('target_vapp')
        target_vdc = self.params.get('target_vdc')
        target_vapp_resource = None

        target_vdc_resource = VDC(
            self.client, resource=self.org.get_vdc(target_vdc))
        target_vapp_resource = target_vdc_resource.get_vapp(target_vapp)

        return target_vapp_resource

    def get_storage_profile(self, profile_name):
        target_vdc = self.params.get('target_vdc')
        vdc_resource = VDC(
            self.client, resource=self.org.get_vdc(target_vdc))

        return vdc_resource.get_storage_profile(profile_name)

    def get_vm(self):
        vapp_vm_resource = self.vapp.get_vm(self.params.get('target_vm_name'))

        return VM(self.client, resource=vapp_vm_resource)

    def add_vm(self):
        params = self.params
        source_vapp_resource = self.get_source_resource()
        target_vm_name = params.get('target_vm_name')
        source_vm_name = params.get('source_vm_name')
        hostname = params.get('hostname')
        vmpassword = params.get('vmpassword')
        vmpassword_auto = params.get('vmpassword_auto')
        vmpassword_reset = params.get('vmpassword_reset')
        network = params.get('network')
        all_eulas_accepted = params.get('all_eulas_accepted')
        power_on = params.get('power_on')
        deploy = params.get('deploy')
        ip_allocation_mode = params.get('ip_allocation_mode')
        cust_script = params.get('cust_script')
        storage_profile = params.get('storage_profile')
        response = dict()
        response['changed'] = False

        try:
            self.get_vm()
        except EntityNotFoundException:
            spec = {
                'source_vm_name': source_vm_name,
                'vapp': source_vapp_resource,
                'target_vm_name': target_vm_name,
                'hostname': hostname,
                'password': vmpassword,
                'password_auto': vmpassword_auto,
                'password_reset': vmpassword_reset,
                'ip_allocation_mode': ip_allocation_mode,
                'network': network,
                'cust_script': cust_script
            }

            spec = {k: v for k, v in spec.items() if v}
            if storage_profile:
                spec['storage_profile'] = self.get_storage_profile(storage_profile)
            specs = [spec]
            args = {
                "specs": specs,
                "deploy": deploy,
                "power_on": power_on,
                "all_eulas_accepted": all_eulas_accepted
            }
            add_vms_task = self.vapp.add_vms(**args)
            self.execute_task(add_vms_task)
            response['msg'] = 'VM {} has been created.'.format(target_vm_name)
            response['changed'] = True
        else:
            msg = 'VM {} is already present.'
            response['warnings'] = msg.format(target_vm_name)

        return response

    def delete_vm(self):
        vm_name = self.params.get('target_vm_name')
        response = dict()
        response['changed'] = False

        try:
            vm = self.get_vm()
        except EntityNotFoundException:
            response['warnings'] = 'VM {} is not present.'.format(vm_name)
        else:
            if not vm.is_powered_off():
                self.undeploy_vm()
            delete_vms_task = self.vapp.delete_vms([vm_name])
            self.execute_task(delete_vms_task)
            response['msg'] = 'VM {} has been deleted.'.format(vm_name)
            response['changed'] = True

        return response

    def update_vm(self):
        vm_name = self.params.get('target_vm_name')
        response = dict()
        response['changed'] = False

        if self.params.get("virtual_cpus"):
            self.update_vm_cpu()
            response['changed'] = True

        if self.params.get("memory"):
            self.update_vm_memory()
            response['changed'] = True

        if self.params.get('compute_policy_href'):
            self.update_vm_compute_policy()
            response['changed'] = True

        response['msg'] = 'VM {} has been updated.'.format(vm_name)

        return response

    def update_vm_cpu(self):
        virtual_cpus = self.params.get('virtual_cpus')
        cores_per_socket = self.params.get('cores_per_socket')

        vm = self.get_vm()
        update_cpu_task = vm.modify_cpu(virtual_cpus, cores_per_socket)

        return self.execute_task(update_cpu_task)

    def update_vm_memory(self):
        memory = self.params.get('memory')

        vm = self.get_vm()
        update_memory_task = vm.modify_memory(memory)

        return self.execute_task(update_memory_task)

    def update_vm_compute_policy(self):
        compute_policy_href = self.params.get('compute_policy_href')

        vm = self.get_vm()
        update_compute_policy_task = vm.update_compute_policy(compute_policy_href)

        return self.execute_task(update_compute_policy_task)

    def power_on_vm(self):
        vm_name = self.params.get('target_vm_name')
        response = dict()
        response['changed'] = False

        vm = self.get_vm()
        if not vm.is_powered_on():
            self.deploy_vm()
            response['msg'] = 'VM {} has been powered on.'.format(vm_name)
            response['changed'] = True
        else:
            response['warnings'] = 'VM {} is powered on.'.format(vm_name)

        return response

    def power_off_vm(self,):
        vm_name = self.params.get('target_vm_name')
        response = dict()
        response['changed'] = False

        vm = self.get_vm()
        if not vm.is_powered_off():
            self.undeploy_vm()
            response['msg'] = 'VM {} has been powered off.'.format(vm_name)
            response['changed'] = True
        else:
            response['warnings'] = 'VM {} is powered off.'.format(vm_name)

        return response

    def reload_vm(self):
        vm_name = self.params.get('target_vm_name')
        response = dict()
        response['changed'] = False

        vm = self.get_vm()
        vm.reload()
        response['msg'] = 'VM {} has been reloaded.'.format(vm_name)
        response['changed'] = True

        return response

    def deploy_vm(self):
        vm_name = self.params.get('target_vm_name')
        force_customization = self.params.get('force_customization')
        response = dict()
        response['changed'] = False

        vm = self.get_vm()
        if not vm.is_deployed():
            deploy_vm_task = vm.deploy(force_customization=force_customization)
            self.execute_task(deploy_vm_task)
            msg = 'VM {} has been deployed'
            response['msg'] = msg.format(vm_name)
            response['changed'] = True
        else:
            msg = 'VM {} is already deployed'
            response['warnings'] = msg.format(vm_name)

        return response

    def undeploy_vm(self):
        vm_name = self.params.get('target_vm_name')
        response = dict()
        response['changed'] = False

        vm = self.get_vm()
        if not vm.is_deployed():
            undeploy_vm_task = vm.undeploy(action="powerOff")
            self.execute_task(undeploy_vm_task)
            msg = 'VM {} has been undeployed'
            response['msg'] = msg.format(vm_name)
            response['changed'] = True
        else:
            msg = 'VM {} is already undeployed'
            response['warnings'] = msg.format(vm_name)

        return response

    def list_disks(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        vm = self.get_vm()
        response['msg'] = vm.list_virtual_hardware_section(
            is_cpu=False, is_memory=False, is_disk=True)

        return response

    def list_nics(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        vm = self.get_vm()
        response['msg'] = vm.list_nics()

        return response

    def set_meta(self):
        response = dict()
        response['changed'] = False
        vm_name = self.params.get('target_vm_name')
        metadata = self.params.get('metadata')
        domain = self.params.get("metadata_domain")
        visibility = self.params.get("metadata_visibility")
        metadata_type = self.params.get("metadata_type")
        metadata_type = "Metadata{0}Value".format(metadata_type)
        domain = MetadataDomain(domain)
        visibility = MetadataVisibility(visibility)
        metadata_type = MetadataValueType(metadata_type)
        vm = self.get_vm()
        set_meta_task = vm.set_multiple_metadata(
            metadata, domain=domain, visibility=visibility,
            metadata_value_type=metadata_type)
        self.execute_task(set_meta_task)
        msg = "Metadata {0} have been set to vm {1}"
        response["msg"] = msg.format(list(metadata.keys()), vm_name)

        return response

    def get_meta(self):
        response = dict()
        response['changed'] = False
        response['msg'] = dict()
        vm = self.get_vm()
        metadata = vm.get_metadata()
        response['msg'] = {
             metadata.MetadataEntry.Key.text: metadata.MetadataEntry.TypedValue.Value.text
        }

        return response

    def remove_meta(self):
        response = dict()
        response['changed'] = False
        vm_name = self.params.get('target_vm_name')
        domain = self.params.get("metadata_domain")
        vm = self.get_vm()
        metadata = self.params.get('metadata')
        domain = MetadataDomain(domain)
        response['msg'] = list()
        for key in metadata:
            remove_meta_task = vm.remove_metadata(key, domain=domain)
            self.execute_task(remove_meta_task)
        msg = "Metadata {0} have been removed from vm {1}"
        response["msg"] = msg.format(list(metadata.keys()), vm_name)

        return response


def main():
    argument_spec = vapp_vm_argument_spec()
    response = dict(msg=dict(type='str'))
    module = VappVM(argument_spec=argument_spec, supports_check_mode=True)

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
