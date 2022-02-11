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
module: vcd_vdc_vm
short_description: Ansible Module to create auto natured vApp from a VM template in vCloud Director.
version_added: "2.4"
description:
    - "Ansible Module to create auto natured vApp."

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
    target_vdc:
        description:
            - target VDC
        required: true
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
            - true if the administrator password for this virtual machine must be reset after first use else false
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
    all_eulas_accepted:
        description:
            - true / false
        required: false
    ip_allocation_mode:
        description:
            - dhcp
        required: false
    power_on:
        description:
            - power on VMs
        required: false
    state:
        description:
            - state of new virtual machines (present).One from state or operation has to be provided.
        required: false
author:
    - rsv@arenadata.io
'''

EXAMPLES = '''
- name: Test with a message
  vcd_vdc_vm:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    org: Terraform
    api_version: 30
    verify_ssl_certs: False
    target_vm_name = "vm_name"
    target_vdc = "vdc"
    source_vapp = "folder_name"
    source_vm_name = "template_name"
    hostname = "vcdcell"
    vmpassword = "rootpass"
    vmpassword_auto = "false"
    vmpassword_reset = "false"
    cust_script = "/home/setup.sh"
    network = "MGMT"
    storage_profile = "Standard"
    state = "present"
    all_eulas_accepted = "true"
'''

RETURN = '''
msg: task details
changed: true if resource has been changed else false
'''

from ansible.module_utils.vcd import VcdAnsibleModule
from lxml.objectify import StringElement
from pyvcloud.vcd.client import E_OVF, E, RelationType
from pyvcloud.vcd.exceptions import EntityNotFoundException
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.utils import task_to_dict
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vm import VM

VM_STATES = ['present', 'absent']


def vm_argument_spec():
    return dict(
        target_vm_name=dict(type='str', required=True),
        target_vdc=dict(type='str', required=True),
        target_vapp=dict(type='str', required=False),
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
        power_on=dict(type='bool', required=False, default=True),
        all_eulas_accepted=dict(type='bool', required=False, default=None),
        state=dict(choices=VM_STATES, required=False),
    )


class VdcVM(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VdcVM, self).__init__(**kwargs)
        self.vdc = self.get_target_resource()

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.add_vm()
        if state == "absent":
            return self.delete_vm()

    def get_source_resource(self):
        source_catalog_name = self.params.get('source_catalog_name')
        source_template_name = self.params.get('source_template_name')
        org_resource = Org(self.client, resource=self.client.get_org())
        source_vapp_resource = None

        if source_catalog_name:
            catalog_item = org_resource.get_catalog_item(
                source_catalog_name, source_template_name)
            source_vapp_resource = self.client.get_resource(
                catalog_item.Entity.get('href'))

        return source_vapp_resource

    def get_target_resource(self):
        target_vdc = self.params.get('target_vdc')
        org_resource = Org(self.client, resource=self.client.get_org())

        vdc = VDC(
            self.client, resource=org_resource.get_vdc(target_vdc))

        return vdc

    def get_storage_profile(self, profile_name):

        return self.vdc.get_storage_profile(profile_name)

    def get_vm(self):
        vapp = VApp(self.client, resource=self.vdc.get_vapp(self.params.get('target_vapp')))
        vapp_vm_resource = vapp.get_vm(self.params.get('target_vm_name'))

        return VM(self.client, resource=vapp_vm_resource)

    def to_instantiate_vm_template_params(self, spec):
        source_vapp = VApp(self.client, resource=spec['vapp'])
        vm_template = source_vapp.get_vm(spec['source_vm_name'])

        params = E.InstantiateVmTemplateParams(
            E.SourcedVmTemplateItem(
                E.Source(
                    href=vm_template.get('href'),
                    id=vm_template.get('id'),
                    type=vm_template.get('type'),
                    name=vm_template.get('name'),
                )
            ),
            name=spec['target_vm_name'],
            powerOn='true' if spec['power_on'] else 'false')

        vm_general_params = E.VmGeneralParams()
        vm_instantiation_param = E.VmTemplateInstantiationParams()

        if spec.get('network'):
            primary_index = int(vm_template.NetworkConnectionSection.
                                PrimaryNetworkConnectionIndex.text)
            vm_instantiation_param.append(
                E.NetworkConnectionSection(
                    E_OVF.Info(),
                    E.NetworkConnection(
                        E.NetworkConnectionIndex(primary_index),
                        E.IsConnected(True),
                        E.IpAddressAllocationMode(spec['ip_allocation_mode'].upper()),
                        network=spec['network'])))

        needs_customization = 'disk_size' in spec or 'password' in spec or \
            'cust_script' in spec or 'hostname' in spec
        if needs_customization:
            guest_customization_param = E.GuestCustomizationSection(
                E_OVF.Info(),
                E.Enabled(True),
            )
            if spec.get('password'):
                guest_customization_param.append(E.AdminPasswordEnabled(True))
                guest_customization_param.append(E.AdminPasswordAuto(False))
                guest_customization_param.append(
                    E.AdminPassword(spec['password']))
            else:
                if spec.get('password_auto'):
                    guest_customization_param.append(
                        E.AdminPasswordEnabled(True))
                    guest_customization_param.append(E.AdminPasswordAuto(True))
                else:
                    guest_customization_param.append(
                        E.AdminPasswordEnabled(False))
            if spec.get('password_reset'):
                guest_customization_param.append(
                    E.ResetPasswordRequired(spec['password_reset']))
            if spec.get('cust_script'):
                guest_customization_param.append(
                    E.CustomizationScript(spec['cust_script']))
            if spec.get('hostname'):
                guest_customization_param.append(
                    E.ComputerName(spec['hostname']))
            vm_instantiation_param.append(guest_customization_param)

        vm_general_params.append(E.NeedsCustomization(needs_customization))

        params.SourcedVmTemplateItem.append(vm_general_params)
        params.SourcedVmTemplateItem.append(vm_instantiation_param)

        if spec.get('storage_profile'):
            sp = spec['storage_profile']
            storage_profile = E.StorageProfile(
                href=sp.get('href'),
                id=sp.get('href').split('/')[-1],
                type=sp.get('type'),
                name=sp.get('name'))
            params.SourcedVmTemplateItem.append(storage_profile)

        return params

    def add_vm(self):
        params = self.params
        source_vapp_resource = self.get_source_resource()
        target_vm_name = params.get('target_vm_name')
        hostname = params.get('hostname')
        source_vm_name = params.get('source_vm_name')
        target_vapp = params.get('target_vapp')
        vmpassword = params.get('vmpassword')
        vmpassword_auto = params.get('vmpassword_auto')
        vmpassword_reset = params.get('vmpassword_reset')
        network = params.get('network')
        power_on = params.get('power_on')
        ip_allocation_mode = params.get('ip_allocation_mode')
        cust_script = params.get('cust_script')
        storage_profile_name = params.get('storage_profile')
        storage_profile = None
        all_eulas_accepted = params.get('all_eulas_accepted')
        response = dict()
        response['msg'] = dict()
        response['changed'] = False

        if storage_profile_name:
            storage_profile = self.get_storage_profile(storage_profile_name)

        try:
            self.vdc.get_vapp(target_vapp)
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
                'cust_script': cust_script,
                'storage_profile': storage_profile,
                'power_on': power_on
            }

            params = self.to_instantiate_vm_template_params(spec)

            if all_eulas_accepted is not None:
                params.append(E.AllEULAsAccepted(all_eulas_accepted))

            add_vms_task = self.client.post_linked_resource(
                self.vdc.resource, RelationType.ADD,
                'application/vnd.vmware.vcloud.instantiateVmTemplateParams+xml', params)
            result = self.execute_task(add_vms_task)
            result = task_to_dict(result)
            if isinstance(result.get('details'), StringElement):
                del result['details']
            response['msg'].update(result)
            response['changed'] = True

        else:
            response['warnings'] = "Vapp {} is already present.".format(target_vapp)

        return response

    def delete_vm(self):
        vm_name = self.params.get('target_vm_name')
        response = dict()
        response['changed'] = False

        try:
            self.get_vm()
        except EntityNotFoundException:
            response['warnings'] = 'VM {} is not present.'.format(vm_name)
        else:
            self.undeploy_vm()
            delete_vms_task = self.client.delete_resource(
                self.get_vm().resource.get('href'))
            self.execute_task(delete_vms_task)
            response['msg'] = 'VM {} has been deleted.'.format(vm_name)
            response['changed'] = True

        return response

    def undeploy_vm(self):
        vm_name = self.params.get('target_vm_name')
        response = dict()
        response['changed'] = False

        vm = self.get_vm()
        if vm.get_resource().get('deployed') == 'true':
            undeploy_vm_task = vm.undeploy()
            self.execute_task(undeploy_vm_task)
            response['msg'] = 'VM {} has been undeployed.'.format(vm_name)
            response['changed'] = True
        else:
            response['warnings'] = 'VM {} is already undeployed.'.format(
                vm_name)

        return response


def main():
    argument_spec = vm_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = VdcVM(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.params.get('state'):
            response = module.manage_states()
        else:
            raise Exception('One of the state/operation should be provided.')

    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
