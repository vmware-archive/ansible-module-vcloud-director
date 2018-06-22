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
module: vcd_org
short_description: Ansible module to manage (create/update/delete) orgs in vCloud Director
version_added: "2.4"
description:
    - Ansible module to manage (create/update/delete) orgs in vCloud Director

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
            - name of the org
        required: true
    full_name:
        description:
            - full name of the org
        required: false
    is_enabled:
        description:
            - enable organization if True. The default value is False
        required: false
    force:
        description:
            - force delete org
        required: false
    recursive:
        description:
            - recursive delete org
        required: false
    state:
        description:
            - state of org
                - present
                - absent
                - update
            - One from state or operation has to be provided.
        required: false
    operation:
        description:
            - operation which should be performed over org
                - read : read org metadata
            - One from state or operation has to be provided.
        required: false
author:
    - pcpandey@mail.com
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_org:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    api_version: 30
    verify_ssl_certs: False
    org_name = "vcdvapp"
    full_name = "vcdlab"
    is_enabled = True
    state="present"
'''

RETURN = '''
msg: success/failure message corresponding to org state/operation
changed: true if resource has been changed else false
'''


from lxml import etree
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.system import System
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException, BadRequestException

VCD_ORG_STATES = ['present', 'absent', 'update']
VCD_ORG_OPERATIONS = ['read']


def org_argument_spec():
    return dict(
        org_name=dict(type='str', required=True),
        full_name=dict(type='str', required=False),
        is_enabled=dict(type='bool', required=False, default=False),
        force=dict(type='bool', required=False, default=None),
        recursive=dict(type='bool', required=False, default=None),
        state=dict(choices=VCD_ORG_STATES, required=False),
        operation=dict(choices=VCD_ORG_OPERATIONS, required=False),
    )


class VCDOrg(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VCDOrg, self).__init__(**kwargs)
        sys_admin = self.client.get_admin()
        self.system = System(self.client, admin_resource=sys_admin)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.create()

        if state == "absent":
            return self.delete()

        if state == "update":
            return self.update()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "read":
            return self.read()

    def create(self):
        org_name = self.params.get('org_name')
        full_name = self.params.get('full_name')
        is_enabled = self.params.get('is_enabled')
        response = dict()
        response['changed'] = False

        try:
            self.system.create_org(org_name, full_name, is_enabled)
            response['msg'] = 'Org {} has been created.'.format(org_name)
            response['changed'] = True
        except BadRequestException:
            response['warnings'] = 'Org {} is already present.'.format(org_name)

        return response

    def read(self):
        org_name = self.params.get('org_name')
        response = dict()
        org_details = dict()
        response['changed'] = False

        resource = self.client.get_org_by_name(org_name)
        org = Org(self.client, resource=resource)
        org_admin_resource = org.client.get_resource(org.href_admin)
        org_details['org_name'] = org_name
        org_details['full_name'] = str(org_admin_resource['FullName'])
        org_details['is_enabled'] = str(org_admin_resource['IsEnabled'])
        response['msg'] = org_details

        return response

    def update(self):
        org_name = self.params.get('org_name')
        is_enabled = self.params.get('is_enabled')
        response = dict()
        response['changed'] = False

        resource = self.client.get_org_by_name(org_name)
        org = Org(self.client, resource=resource)
        org.update_org(is_enabled)
        response['msg'] = "Org {} has been updated.".format(org_name)
        response['changed'] = True

        return response

    def delete(self):
        org_name = self.params.get('org_name')
        force = self.params.get('force')
        recursive = self.params.get('recursive')
        response = dict()
        response['changed'] = False

        try:
            delete_org_task = self.system.delete_org(org_name, force, recursive)
            self.execute_task(delete_org_task)
            response['msg'] = "Org {} has been deleted.".format(org_name)
            response['changed'] = True
        except EntityNotFoundException:
            response['warnings'] = "Org {} is not present.".format(org_name)

        return response


def main():
    argument_spec = org_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = VCDOrg(argument_spec=argument_spec, supports_check_mode=True)

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
