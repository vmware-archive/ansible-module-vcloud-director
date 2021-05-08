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
module: vcd_resources
short_description: Add/Delete/Update VCD Infrastructure resources
version_added: "2.4"
description:
    - Add/Delete/Update VCD Infrastructure resources

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
    nsxts:
        description:
            - List of network type of Infrastructure resource
        required: true
    state:
        description:
            - state of vcd resource ('present'/'absent'/'update').
        required: false
    operation:
        description:
            - operations on vcd resource ('read').
        required: false

author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: add vcd resources
  vcd_resources
    nsxt:
        url: ""
        username: ""
        password: ""
        networkProviderScope: ""
    state: "present"
  register: output
'''

RETURN = '''
msg: success/failure message corresponding to resource state
changed: true if resource has been changed
'''

from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.nsxt_extension import NsxtExtension
from pyvcloud.vcd.exceptions import EntityNotFoundException

VCD_RESOURCES_STATES = ['present', 'absent', 'update']
VCD_RESOURCES_OPERATIONS = ['list']


def vcd_resources_argument_spec():
    return dict(
        nsxts=dict(type='list', required=False),
        state=dict(choices=VCD_RESOURCES_STATES, required=False),
        operation=dict(choices=VCD_RESOURCES_OPERATIONS, required=False)
    )


class VcdResources(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VcdResources, self).__init__(**kwargs)
        self.nsxt_extension = NsxtExtension(self.client)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.add()

        if state == "absent":
            return self.delete()

        if state == "update":
            return self.update()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "list":
            return self.list()

    def get(self, name):
        return self.nsxt_extension.get(name)

    def add(self):
        nsxts = self.params.get('nsxts')
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        for nsxt in nsxts:
            try:
                name = nsxt.get('name')
                self.get(name)
                response['msg'].append('Nsx-T manager {0} is already exists'.format(name))
            except EntityNotFoundException:
                url = nsxt.get('url')
                username = nsxt.get('username')
                password = nsxt.get('password')
                self.nsxt_extension.add(name, url, username, password)
                response['msg'].append('NSX-T Manager {0} is added'.format(name))
                response['changed'] = True

        return response

    def delete(self):
        nsxts = self.params.get('nsxts')
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        for nsxt in nsxts:
            try:
                name = nsxt.get('name')
                self.get(name)
                self.nsxt_extension.delete(name)
                response['msg'].append('NSX-T Manager {0} is deleted'.format(name))
                response['changed'] = True
            except EntityNotFoundException:
                response['msg'].append('NSX-T Manager {0} is not present'.format(name))


        return response

    def update(self):
        nsxts = self.params.get('nsxts')
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        for nsxt in nsxts:
            try:
                name = nsxt.get('name')
                self.get(name)
                new_name = nsxt.get('new_name')
                url = nsxt.get('url')
                username = nsxt.get('username')
                password = nsxt.get('password')
                self.nsxt_extension.update(name, new_name, url, username, password)
                response['msg'].append('NSX-T Manager {0} is updated'.format(name))
                response['changed'] = True
            except EntityNotFoundException:
                response['msg'].append('NSX-T Manager {0} is not present'.format(name))

        return response

    def list(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        for nsxt_manager in self.nsxt_extension.list():
            response['msg'].append({
                'name': nsxt_manager.get('name'),
                'url': str(nsxt_manager.Url),
                'version': str(nsxt_manager.Version),
                'deployment_type': str(nsxt_manager.DeploymentType)
            })

        return response


def main():
    argument_spec = vcd_resources_argument_spec()
    response = dict(msg=dict(type='str'))
    module = VcdResources(argument_spec=argument_spec, supports_check_mode=True)

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
        response['msg'] = error.__str__()
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
