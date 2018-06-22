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
module: vcd_vapp
short_description: Ansible Module to manage (create/update/delete) vApps in vCloud Director.
version_added: "2.4"
description:
    - "Ansible Module to manage (create/update/delete) vApps in vCloud Director."

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
    vapp_name:
        description:
            - Vapp name
        required: true
    vdc:
        description:
            - Org Vdc where this VAPP gets created
        required: true
    template_name:
        description:
            - source catalog item name
        required: false
    description:
        description:
            - vApp description
        required: false
    network:
        description:
            - org network for the vapp
        required: false
    fence_mode:
        description:
            - vApp fence mode
        required: false
    deploy:
        description:
            - "true" if to deploy vApp else "false"
        required: false
    power_on:
        description:
            - "true" if to power on vApp else "false"
        required: false
    accept_all_eulas:
        description:
            - "true"/"false"
        required: false
    disk_size:
        description:
            - vApp disk size
        required: false
    memory:
        description:
            - memory size in MB
        required: false
    cpu:
        description:
            - number of CPU
        required: false
    vmpassword:
        description:
            - vm password in vApps
        required: false
    cust_script:
        description:
            - vApp customization script
        required: false
    vm_name:
        description:
            - vm name in vApp
        required: false
    hostname:
        description:
            - vApp hostname
        required: false
    ip_address:
        description:
            - vApp ip address
        required: false
    ip_allocation_mode:
        description:
            - IP Allocation mode "static"/"DHCP"
        required: false
    storage_profile:
        description:
            - storage profile to use for the vapp
        required: false
    network_adapter_type:
        description:
            - network adapter type for vApp
        required: false
    force:
        description:
            - "true" if delete vApp forcefully else "false"
        required: false
    state:
        description:
            - state of new virtual machines ('present'/'absent').
            - One from state or operation has to be provided.
        required: false
    operation:
        description:
            - operation on vApp ('poweron'/'poweroff'/'deploy'/'undeploy').
            - One from state or operation has to be provided.
        required: false

author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_vapp:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    org: Terraform
    api_version: 30
    verify_ssl_certs: False
    vapp_name = "vcdvapp"
    template_name = "vcdlab"
    catalog_name = "source1"
    vdc = "vdcname"
    network = "ORGNET1"
    ip_allocation_mode = "static"
    cpu = 4
    memory = 2000
    state="present"
    storage_profile = "SP_PERFORMANCE_SDD"
'''

RETURN = '''
msg: success/failure message corresponding to vapp state/operation
changed: true if resource has been changed else false
'''

from lxml import etree
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.client import FenceMode
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException, OperationNotSupportedException

VAPP_VM_STATES = ['present', 'absent']
VAPP_VM_OPERATIONS = ['poweron', 'poweroff', 'deploy', 'undeploy']


def vapp_argument_spec():
    return dict(
        vapp_name=dict(type='str', required=True),
        template_name=dict(type='str', required=False),
        catalog_name=dict(type='str', required=False),
        vdc=dict(type='str', required=True),
        description=dict(type='str', required=False, default=None),
        network=dict(type='str', required=False, default=None),
        fence_mode=dict(type='str', required=False, default=FenceMode.BRIDGED.value),
        ip_allocation_mode=dict(type='str', required=False, default="dhcp"),
        deploy=dict(type='bool', required=False, default=True),
        power_on=dict(type='bool', required=False, default=True),
        accept_all_eulas=dict(type='bool', required=False, default=False),
        memory=dict(type='int', required=False, default=None),
        cpu=dict(type='int', required=False, default=None),
        disk_size=dict(type='int', required=False, default=None),
        vmpassword=dict(type='str', required=False, default=None),
        cust_script=dict(type='str', required=False, default=None),
        vm_name=dict(type='str', required=False, default=None),
        hostname=dict(type='str', required=False, default=None),
        ip_address=dict(type='str', required=False, default=None),
        storage_profile=dict(type='str', required=False, default=None),
        network_adapter_type=dict(type='str', required=False, default=None),
        force=dict(type='bool', required=False, default=False),
        state=dict(choices=VAPP_VM_STATES, required=False),
        operation=dict(choices=VAPP_VM_OPERATIONS, required=False),
    )


class Vapp(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Vapp, self).__init__(**kwargs)
        logged_in_org = self.client.get_org()
        self.org = Org(self.client, resource=logged_in_org)
        vdc_resource = self.org.get_vdc(self.params.get('vdc'))
        self.vdc = VDC(self.client, href=vdc_resource.get('href'))

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.create()

        if state == "absent":
            return self.delete()

    def manage_operations(self):
        state = self.params.get('operation')
        if state == "poweron":
            return self.power_on()

        if state == "poweroff":
            return self.power_off()

        if state == "deploy":
            return self.deploy()

        if state == "undeploy":
            return self.undeploy()

    def create(self):
        params = self.params
        vapp_name = params.get('vapp_name')
        catalog_name = params.get('catalog_name')
        template_name = params.get('template_name')
        description = params.get('description')
        network = params.get('network')
        fence_mode = params.get('fence_mode')
        ip_allocation_mode = params.get('ip_allocation_mode')
        deploy = params.get('deploy')
        power_on = params.get('power_on')
        accept_all_eulas = params.get('accept_all_eulas')
        memory = params.get('memory')
        cpu = params.get('cpu')
        disk_size = params.get('disk_size')
        vmpassword = params.get('vmpassword')
        cust_script = params.get('cust_script')
        vm_name = params.get('vm_name')
        hostname = params.get('hostname')
        ip_address = params.get('ip_address')
        storage_profile = params.get('storage_profile')
        network_adapter_type = params.get('network_adapter_type')
        response = dict()
        response['changed'] = False

        try:
            self.vdc.get_vapp(vapp_name)
        except EntityNotFoundException:
            create_vapp_task = self.vdc.instantiate_vapp(
                name=vapp_name,
                catalog=catalog_name,
                template=template_name,
                description=description,
                network=network,
                fence_mode=fence_mode,
                ip_allocation_mode=ip_allocation_mode,
                deploy=deploy,
                power_on=power_on,
                accept_all_eulas=accept_all_eulas,
                memory=memory,
                cpu=cpu,
                disk_size=disk_size,
                password=vmpassword,
                cust_script=cust_script,
                vm_name=vm_name,
                hostname=hostname,
                ip_address=ip_address,
                storage_profile=storage_profile,
                network_adapter_type=network_adapter_type)
            self.execute_task(create_vapp_task.Tasks.Task[0])
            response['msg'] = 'Vapp {} has been created.'.format(vapp_name)
            response['changed'] = True
        else:
            response['warnings'] = "Vapp {} is already present.".format(vapp_name)

        return response

    def delete(self):
        vapp_name = self.params.get('vapp_name')
        force = self.params.get('force')
        response = dict()
        response['changed'] = False

        try:
            self.vdc.get_vapp(vapp_name)
        except EntityNotFoundException:
            response['warnings'] = "Vapp {} is not present.".format(vapp_name)
        else:
            delete_vapp_task = self.vdc.delete_vapp(name=vapp_name, force=force)
            self.execute_task(delete_vapp_task)
            response['msg'] = 'Vapp {} has been deleted.'.format(vapp_name)
            response['changed'] = True

        return response

    def power_on(self):
        vapp_name = self.params.get('vapp_name')
        response = dict()
        response['changed'] = False

        try:
            vapp_resource = self.vdc.get_vapp(vapp_name)
            vapp = VApp(self.client, name=vapp_name, resource=vapp_resource)
            power_on_vapp_task = vapp.power_on()
            self.execute_task(power_on_vapp_task)
            response['msg'] = 'Vapp {} has been powered on.'.format(vapp_name)
            response['changed'] = True
        except OperationNotSupportedException:
            response['warnings'] = 'Vapp {} is already powered on.'.format(vapp_name)

        return response

    def power_off(self):
        vapp_name = self.params.get('vapp_name')
        response = dict()
        response['changed'] = False

        try:
            vapp_resource = self.vdc.get_vapp(vapp_name)
            vapp = VApp(self.client, name=vapp_name, resource=vapp_resource)
            power_off_vapp_task = vapp.power_off()
            self.execute_task(power_off_vapp_task)
            response['msg'] = 'Vapp {} has been powered off.'.format(vapp_name)
            response['changed'] = True
        except OperationNotSupportedException:
            response['warnings'] = 'Vapp {} is already powered off.'.format(vapp_name)

        return response

    def deploy(self):
        vapp_name = self.params.get('vapp_name')
        response = dict()
        response['changed'] = False

        try:
            vapp_resource = self.vdc.get_vapp(vapp_name)
            vapp = VApp(self.client, name=vapp_name, resource=vapp_resource)
            deploy_vapp_task = vapp.deploy()
            self.execute_task(deploy_vapp_task)
            response['msg'] = 'Vapp {} has been deployed.'.format(vapp_name)
            response['changed'] = True
        except OperationNotSupportedException:
            response['warnings'] = 'Vapp {} is already deployed.'.format(vapp_name)

        return response

    def undeploy(self):
        vapp_name = self.params.get('vapp_name')
        response = dict()
        response['changed'] = False

        try:
            vapp_resource = self.vdc.get_vapp(vapp_name)
            vapp = VApp(self.client, name=vapp_name, resource=vapp_resource)
            undeploy_vapp_task = vapp.undeploy()
            self.execute_task(undeploy_vapp_task)
            response['msg'] = 'Vapp {} has been undeployed.'.format(vapp_name)
            response['changed'] = True
        except OperationNotSupportedException:
            response['warnings'] = 'Vapp {} is already undeployed.'.format(vapp_name)

        return response


def main():
    argument_spec = vapp_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = Vapp(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.params.get('state'):
            response = module.manage_states()
        elif module.params.get('operation'):
            response = module.manage_operations()
        else:
            raise Exception('One of the state/operation should be provided.')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
