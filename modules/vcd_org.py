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
client: vcd_org
short_description: This module is to create org in vCloud Director
version_added: "2.4"
description:
    - "This module is to to create org in vCloud Director"
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
            - name of the org
        required: true
    full_name:
        description:
            - full name of the org
        required: true

    force:
        description:
            - force delete org 
        required: true

    recursive:
        description:
            - recursive delete org
        required: true                
    
    state:
        description:
            - state of org
                - present 
                - absent  
            - One from state or operation has to be provided. 
        required: false

    operation:
        description:
            - operation which should be performed over org 
                - enable : enable org
                - disable : disable org
                - read : read org metadata
            - One from state or operation has to be provided.
        required: false
author:
    - pcpandey@mail.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_org:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    api_version: 30
    verify_ssl_certs: False
    name = "vcdvapp"
    full_name = "vcdlab"
    is_enabled = True
    state="present"
'''

RETURN = '''
result: success/failure message relates to org operation
'''


from lxml import etree
from pyvcloud.vcd.system import System
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.client import TaskStatus
from ansible.module_utils.vcd import VcdAnsibleModule
from ansible.module_utils.vcd_errors import OrgDeletionError

VCD_ORG_STATES = ['present', 'absent']
VCD_ORG_OPERATIONS = ['read', 'enable', 'disable']

def vapp_argument_spec():
    return dict(
        name=dict(type='str', required=True),
        full_name=dict(type='str', required=False),
        is_enabled=dict(type='bool', required=False),
        force=dict(type='bool', required=False),
        recursive=dict(type='bool', required=False),
        state=dict(choices=VCD_ORG_STATES, required=False),
        operation=dict(choices=VCD_ORG_OPERATIONS, required=False),
    )

class VCDOrg(object):
    """
        Org class is already defined in pvcloud, hence using class name 'VCDOrg'
    """
    
    def __init__(self, module):
        self.module = module  

    def get_system_object(self):
        client = self.module.client
        sys_admin = client.get_admin()
        system = System(client, admin_resource=sys_admin)

        return system      

    def create(self):
        params = self.module.params
        name = params.get('name')
        full_name = params.get('full_name')
        is_enabled = params.get('is_enabled')

        response = dict()
        
        system = self.get_system_object()
        system.create_org(name, full_name, is_enabled)
        response['msg'] = 'Org {} has been created.'.format(name)
        response['changed'] = True

        return response

    def read(self):
        params = self.module.params
        name = params.get('name')

        response = dict()

        client = self.module.client
        resource = client.get_org_by_name(name)
        org = Org(client, resource=resource)
        org_admin_resource = org.client.get_resource(org.href_admin)

        org_details = dict()
        org_details['name'] = name    
        org_details['full_name'] = str(org_admin_resource['FullName'])
        org_details['is_enabled'] = str(org_admin_resource['IsEnabled'])

        response['msg'] = org_details
        response['changed'] = False

        return response


    def enable(self):
        params = self.module.params
        name = params.get('name')
        is_enabled = True

        response = dict()

        client = self.module.client
        resource = client.get_org_by_name(name)
        org = Org(client, resource=resource)
        org.update_org(is_enabled)

        response['msg'] = 'Org {} has been enabled.'.format(name)
        response['changed'] = True

        return response

    def disable(self):
        params = self.module.params
        name = params.get('name')
        is_enabled = False

        response = dict()

        client = self.module.client
        resource = client.get_org_by_name(name)
        org = Org(client, resource=resource)
        org.update_org(is_enabled)

        response['msg'] = 'Org {} has been disabled.'.format(name)
        response['changed'] = True

        return response       

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
            raise Exception(
                etree.tostring(task_state, pretty_print=True))

        return 1        

    def delete(self):
        params = self.module.params
        name = params.get('name')
        force = params.get('force')
        recursive = params.get('recursive')

        response = dict()

        try:
            system = self.get_system_object()
            delete_org_resp = system.delete_org(name, force, recursive)

            self.execute_task(delete_org_resp)
            response['msg'] = 'Org {} has been deleted.'.format(name)
            response['changed'] = True

            return response
        except Exception as e:
            raise OrgDeletionError(str(e))          


def manage_org_states(org):
    params = org.module.params
    state = params.get('state')
    if state == "present":
        return org.create()

    if state == "absent":
        return org.delete()

def manage_org_operations(org):
    params = org.module.params
    state = params.get('operation')
    if state == "read":
        return org.read()

    if state == "enable":
        return org.enable()

    if state == "disable":
        return org.disable() 

def main():
    argument_spec = vapp_argument_spec()
    response = dict(
        msg=dict(type='str')
    )

    module = VcdAnsibleModule(argument_spec=argument_spec,
                              supports_check_mode=True)
    try:
        org = VCDOrg(module)
        if module.params.get('state'):
            response = manage_org_states(org)
        elif module.params.get('operation'):
            response = manage_org_operations(org)
        else:
            raise Exception('One of from state/operation should be provided.')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()        




               
