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
client: vcd_vapp
short_description: This module is to create vApps in vCloud Director
version_added: "2.4"
description:
    - "This module is to to create vApps in vCloud Director"
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
    name:
        description:
            - Vapp name
        required: true
    template_name:
        description:
            - source catalog item name
        required: true
    catalog_name:
        description:
            - source catalog name
        required: true
    vdc:
        description:
            - Org Vdc where this VAPP gets created
        required: true
    network:
        description:
            - org network for the vapp
        required: false
    ip_allocation_mode:
        description:
            - IP Allocation mode "static"/"DHCP"
        required: false
    memory:
        description:
            - memory size in MB
        required: false
    cpu:
        description:
            - number of CPU
        required: false
    storage_profile:
        description:
            - storage profile to use for the vapp
        required: false
    power_on:
        description:
            - "true"/"false"
        required: false
    accept_all_eulas:
        description:
            - "true"/"false"
        required: false
    state:
        description:
            - state of new virtual machines ('present'/'absent').One from state or operation has to be provided. 
        required: false
    operation:
        description:
            - operation which should be performed over new virtual machines ('poweron'/'poweroff').One from state or operation has to be provided.
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
    name = "vcdvapp"
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
result: success/failure message relates to vapp operation
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
from ansible.module_utils.vcd_errors import VCDVappCreationError

VAPP_VM_STATES = ['present', 'absent']
VAPP_VM_OPERATIONS = ['poweron', 'poweroff', 'deploy', 'undeploy']


def vapp_argument_spec():
    return dict(
        name=dict(type='str', required=True),
        template_name=dict(type='str', required=True),
        catalog_name=dict(type='str', required=True),
        vdc=dict(type='str', required=True),
        network=dict(type='str', required=False),
        ip_allocation_mode=dict(type='str', required=False),
        memory=dict(type='str', required=False),
        cpu=dict(type='str', required=False),
        storage_profile=dict(type='str', required=False),
        power_on=dict(type='bool', required=False),
        accept_all_eulas=dict(type='bool', required=False),
        state=dict(choices=VAPP_VM_STATES, required=False),
        operation=dict(choices=VAPP_VM_OPERATIONS, required=False),
    )


class Vapp(object):
    def __init__(self, module):
        self.module = module

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
            raise VCDVappCreationError(
                etree.tostring(task_state, pretty_print=True))

        return 1

    def get_vdc_object(self, vdc_name):
        client = self.module.client
        logged_in_org = client.get_org()
        org = Org(client, resource=logged_in_org)
        vdc_resource = org.get_vdc(vdc_name)

        return VDC(client, href=vdc_resource.get('href'))

    def create(self):
        client = self.module.client
        params = self.module.params
        vdc_name = params.get('vdc')
        vapp_name = params.get('name')
        catalog_name = params.get('catalog_name')
        template_name = params.get('template_name')
        network = params.get('network', None)
        memory = params.get('memory', None)
        storage_profile = params.get('storage_profile', None)
        accept_all_eulas = params.get('accept_all_eulas', True)
        power_on = params.get('power_on', True)
        cpu = params.get('cpu', None)
        response = dict()

        vdc = self.get_vdc_object(vdc_name)
        result = vdc.instantiate_vapp(
            name=vapp_name,
            catalog=catalog_name,
            template=template_name,
            network=network,
            memory=memory,
            cpu=cpu,
            power_on=power_on,
            storage_profile=storage_profile,
            accept_all_eulas=accept_all_eulas)

        task_monitor = client.get_task_monitor()
        self.execute_task(task_monitor, result.Tasks.Task[0])
        response['msg'] = 'Vapp {} has been created.'.format(vapp_name)
        response['changed'] = True

        return response

    def delete(self):
        client = self.module.client
        params = self.module.params
        vdc_name = params.get('vdc')
        vapp_name = params.get('name')
        response = dict()

        vdc = self.get_vdc_object(vdc_name)
        result = vdc.delete_vapp(name=vapp_name, force=True)
        task_monitor = client.get_task_monitor()
        self.execute_task(task_monitor, result)
        response['msg'] = 'Vapp {} has been deleted.'.format(vapp_name)
        response['changed'] = True

        return response

    def power_on(self):
        try:
            client = self.module.client
            params = self.module.params
            vdc_name = params.get('vdc')
            vapp_name = params.get('name')
            response = dict()

            vdc = self.get_vdc_object(vdc_name)
            vapp_resource = vdc.get_vapp(vapp_name)
            vapp = VApp(client, name=vapp_name, resource=vapp_resource)
            resp = vapp.power_on()
            task_monitor = client.get_task_monitor()
            self.execute_task(task_monitor, resp)

        except VcdErrorResponseException:
            pass

        response['msg'] = 'Vapp {} has been powered on.'.format(vapp_name)
        response['changed'] = True

        return response

    def power_off(self):
        try:
            client = self.module.client
            params = self.module.params
            vdc_name = params.get('vdc')
            vapp_name = params.get('name')
            response = dict()

            vdc = self.get_vdc_object(vdc_name)
            vapp_resource = vdc.get_vapp(vapp_name)
            vapp = VApp(client, name=vapp_name, resource=vapp_resource)
            resp = vapp.power_off()
            task_monitor = client.get_task_monitor()
            self.execute_task(task_monitor, resp)

        except VcdErrorResponseException:
            pass

        response['msg'] = 'Vapp {} has been powered off.'.format(vapp_name)
        response['changed'] = True

        return response

    def deploy(self):
        try:
            client = self.module.client
            params = self.module.params
            vdc_name = params.get('vdc')
            vapp_name = params.get('name')
            response = dict()

            vdc = self.get_vdc_object(vdc_name)
            vapp_resource = vdc.get_vapp(vapp_name)
            vapp = VApp(client, name=vapp_name, resource=vapp_resource)
            resp = vapp.deploy()
            task_monitor = client.get_task_monitor()
            self.execute_task(task_monitor, resp)

        except MissingLinkException:
            pass

        response['msg'] = 'Vapp {} has been deployed.'.format(vapp_name)
        response['changed'] = True

        return response

    def undeploy(self):
        try:
            client = self.module.client
            params = self.module.params
            vdc_name = params.get('vdc')
            vapp_name = params.get('name')
            response = dict()

            vdc = self.get_vdc_object(vdc_name)
            vapp_resource = vdc.get_vapp(vapp_name)
            vapp = VApp(client, name=vapp_name, resource=vapp_resource)
            resp = vapp.undeploy()
            task_monitor = client.get_task_monitor()
            self.execute_task(task_monitor, resp)

        except MissingLinkException:
            pass

        response['msg'] = 'Vapp {} has been undeployed.'.format(vapp_name)
        response['changed'] = True

        return response


def manage_vapp_states(vApp):
    params = vApp.module.params
    state = params.get('state')
    if state == "present":
        return vApp.create()

    if state == "absent":
        return vApp.delete()


def manage_vapp_operations(vApp):
    params = vApp.module.params
    state = params.get('operation')
    if state == "poweron":
        return vApp.power_on()

    if state == "poweroff":
        return vApp.power_off()

    if state == "deploy":
        return vApp.deploy()

    if state == "undeploy":
        return vApp.undeploy()


def main():
    argument_spec = vapp_argument_spec()
    response = dict(
        msg=dict(type='str')
    )

    module = VcdAnsibleModule(argument_spec=argument_spec,
                              supports_check_mode=True)
    try:
        vApp = Vapp(module)
        if module.params.get('state'):
            response = manage_vapp_states(vApp)
        elif module.params.get('operation'):
            response = manage_vapp_operations(vApp)
        else:
            raise Exception('One of from state/operation should be provided.')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
