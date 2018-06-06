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
    vapp_name:
        description:
            - Vapp name
        required: false
    template_name:
        description:
            - source catalog item name
        required: false
    catalog_name:
        description:
            - source catalog name
        required: false
    vdc:
        description:
            - Org Vdc where this VAPP gets created
        required: false
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
            - state of new virtual machines ('present'/'absent').
            - One from state or operation has to be provided. 
        required: false
    operation:
        description:
            - operation which should be performed over new virtual machines ('poweron'/'poweroff'/'deploy'/'undeploy').
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
result: success/failure message relates to vapp operation
'''

from lxml import etree
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from ansible.module_utils.vcd import VcdAnsibleModule

VAPP_VM_STATES = ['present', 'absent']
VAPP_VM_OPERATIONS = ['poweron', 'poweroff', 'deploy', 'undeploy']


def vapp_argument_spec():
    return dict(
        vapp_name=dict(type='str', required=False),
        template_name=dict(type='str', required=False),
        catalog_name=dict(type='str', required=False),
        vdc=dict(type='str', required=False),
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
        network = params.get('network')
        memory = params.get('memory')
        storage_profile = params.get('storage_profile')
        accept_all_eulas = params.get('accept_all_eulas', True)
        power_on = params.get('power_on', True)
        cpu = params.get('cpu')
        response = dict()

        create_vapp_task = self.vdc.instantiate_vapp(
            name=vapp_name,
            catalog=catalog_name,
            template=template_name,
            network=network,
            memory=memory,
            cpu=cpu,
            power_on=power_on,
            storage_profile=storage_profile,
            accept_all_eulas=accept_all_eulas)
        self.execute_task(create_vapp_task.Tasks.Task[0])
        response['msg'] = 'Vapp {} has been created.'.format(vapp_name)
        response['changed'] = True

        return response

    def delete(self):
        vapp_name = self.params.get('vapp_name')
        response = dict()

        delete_vapp_task = self.vdc.delete_vapp(name=vapp_name, force=True)
        self.execute_task(delete_vapp_task)
        response['msg'] = 'Vapp {} has been deleted.'.format(vapp_name)
        response['changed'] = True

        return response

    def power_on(self):
        vapp_name = self.params.get('vapp_name')
        response = dict()

        vapp_resource = self.vdc.get_vapp(vapp_name)
        vapp = VApp(self.client, name=vapp_name, resource=vapp_resource)
        power_on_vapp_task = vapp.power_on()
        self.execute_task(power_on_vapp_task)
        response['msg'] = 'Vapp {} has been powered on.'.format(vapp_name)
        response['changed'] = True

        return response

    def power_off(self):
        vapp_name = self.params.get('vapp_name')
        response = dict()

        vapp_resource = self.vdc.get_vapp(vapp_name)
        vapp = VApp(self.client, name=vapp_name, resource=vapp_resource)
        power_off_vapp_task = vapp.power_off()
        self.execute_task(power_off_vapp_task)
        response['msg'] = 'Vapp {} has been powered off.'.format(vapp_name)
        response['changed'] = True

        return response

    def deploy(self):
        vapp_name = self.params.get('vapp_name')
        response = dict()

        vapp_resource = self.vdc.get_vapp(vapp_name)
        vapp = VApp(self.client, name=vapp_name, resource=vapp_resource)
        deploy_vapp_task = vapp.deploy()
        self.execute_task(deploy_vapp_task)
        response['msg'] = 'Vapp {} has been deployed.'.format(vapp_name)
        response['changed'] = True

        return response

    def undeploy(self):
        vapp_name = self.params.get('vapp_name')
        response = dict()

        vapp_resource = self.vdc.get_vapp(vapp_name)
        vapp = VApp(self.client, name=vapp_name, resource=vapp_resource)
        undeploy_vapp_task = vapp.undeploy()
        self.execute_task(undeploy_vapp_task)
        response['msg'] = 'Vapp {} has been undeployed.'.format(vapp_name)
        response['changed'] = True

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
            raise Exception('One of from state/operation should be provided.')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
