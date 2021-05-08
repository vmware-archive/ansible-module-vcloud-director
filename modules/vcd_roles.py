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
module: vcd_roles
short_description: Manage role's states/operations in vCloud Director
version_added: "2.4"
description:
    - Manage role's states/operations in vCloud Director

options:
    user:
        description:
            - vCloud Director user name
        type: str
    password:
        description:
            - vCloud Director user password
        type: str
    host:
        description:
            - vCloud Director host address
        type: str
    org:
        description:
            - Organization name on vCloud Director to access
        type: str
    api_version:
        description:
            - Pyvcloud API version, required as float i.e 31 => 31.0
        type: float
    verify_ssl_certs:
        description:
            - whether to use secure connection to vCloud Director host
        type: bool
    org_name:
        description:
            - target org name
            - required for service providers to create resources in other orgs
            - default value is module level / environment level org
        required: false
    role_name:
        description:
            - The name of the role
        type: str
    role_description:
        description:
            - The description of the role
        type: str
    role_rights:
        description:
            - list of rights attached to the new role
        type: list
    state:
        description:
            - state of new role ('present'/'absent'/'update').
            - One from state or operation has to be provided.
        type: str
        choices: ['present', 'absent', 'update']
    operation:
        description:
            - list operations on available roles & rights inside an org
        type: str
        choices: ['list_roles', 'list_rights']

author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_org_vdc:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    org: Terraform
    api_version: 30.0
    verify_ssl_certs: False
    role_name: sample_role
    role_description: sample role
    role_rights:
        - "Catalog: Import Media from vSphere"
    state: "present"
'''

RETURN = '''
msg: success/failure message corresponding to roles state/operation
changed: true if resource has been changed else false
'''


from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.client import E
from pyvcloud.vcd.system import System
from pyvcloud.vcd.client import EntityType
from pyvcloud.vcd.client import RelationType
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException


VCD_ROLE_STATES = ['present', 'absent', 'update']
VCD_ROLE_OPERATIONS = ['list_rights', 'list_roles']


def vcd_roles_argument_spec():
    return dict(
        role_name=dict(type='str', required=False),
        role_description=dict(type='str', required=False, default=''),
        role_rights=dict(type='list', required=False),
        org_name=dict(type='str', required=False, default=None),
        state=dict(choices=VCD_ROLE_STATES, required=False),
        operation=dict(choices=VCD_ROLE_OPERATIONS, required=False),
    )


class Roles(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Roles, self).__init__(**kwargs)
        self.org = self.get_org()

    def manage_states(self):
        state = self.params.get('state')
        if state == 'present':
            return self.create()

        if state == 'absent':
            return self.delete()

        if state == 'update':
            return self.update()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "list_rights":
            return self.list_rights()

        if operation == "list_roles":
            return self.list_roles()

    def get_org(self):
        org_name = self.params.get('org_name')
        org_resource = self.client.get_org()
        if org_name:
            org_resource = self.client.get_org_by_name(org_name)

        return Org(self.client, resource=org_resource)

    def create(self):
        role_name = self.params.get('role_name')
        role_description = self.params.get('role_description')
        role_rights = self.params.get('role_rights')
        response = dict()
        response['changed'] = False

        try:
            self.org.get_role_record(role_name)
        except EntityNotFoundException:
            self.org.create_role(role_name, role_description, role_rights)
            response['msg'] = 'Role {} has been created'.format(role_name)
            response['changed'] = True
        else:
            response['warnings'] = 'Role {} is already present'.format(role_name)

        return response

    def update(self):
        role_name = self.params.get('role_name')
        role_description = self.params.get('role_description')
        role_rights = self.params.get('role_rights')
        response = dict()
        response['changed'] = False

        role = self.org.get_role_record(role_name)
        role_resource = self.org.get_role_resource(role_name)
        role_resource.Description = E.Description(role_description)
        role_rights = tuple() if role_rights is None else role_rights

        for role_right in tuple(role_rights):
            role_right_record = self.org.get_right_record(role_right)
            role_resource.RightReferences.append(
                E.RightReference(
                    name=role_right_record.get('name'),
                    href=role_right_record.get('href'),
                    type=EntityType.RIGHT.value))

        self.client.put_resource(
            role.get('href'), role_resource, EntityType.ROLE.value)
        response['msg'] = 'Role {} has been updated.'.format(role_name)
        response['changed'] = True

        return response

    def delete(self):
        role_name = self.params.get('role_name')
        response = dict()
        response['changed'] = False

        try:
            self.org.get_role_record(role_name)
            self.org.delete_role(role_name)
            response['msg'] = 'Role {} has been deleted'.format(role_name)
            response['changed'] = True
        except EntityNotFoundException:
            response['warnings'] = 'Role {} is not present'.format(role_name)

        return response

    def list_rights(self):
        response = dict()
        response['changed'] = False
        response['msg'] = self.org.list_rights_of_org()

        return response

    def list_roles(self):
        response = dict()
        response['changed'] = False
        response['msg'] = self.org.list_roles()

        return response


def main():
    argument_spec = vcd_roles_argument_spec()
    response = dict(msg=dict(type='str'))
    module = Roles(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.check_mode:
            response = dict()
            response['changed'] = False
            response['msg'] = "skipped, running in check mode"
            response['skipped'] = True
        elif module.params.get("state"):
            response = module.manage_states()
        elif module.params.get("operation"):
            response = module.manage_operations()
        else:
            raise Exception("Please provide state/operation for resource")

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
