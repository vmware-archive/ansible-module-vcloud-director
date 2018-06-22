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
module: vcd_user
short_description: Ansible module to manage (create/update/delete) users in vCloud Director
version_added: "2.4"
description:
    - Ansible module to manage (create/update/delete) users in vCloud Director

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
    username:
        description:
            - name of the user
        required: true
    userpassword:
        description:
            - password of the user
        required: false
    role_name:
        description:
            - role of the user
        required: false
    full_username:
        description:
            - full name of the user
        required: false
    description:
        description:
            - description for the User
        required: false
    email:
        description:
            - user email address
        required: false
    telephone:
        description:
            - user contact number
        required: false
    im:
        description:
            - im address of the user
        required: false
    alert_email:
        description:
            - user alert email address
        required: false
    alert_email_prefix:
        description:
            - string to prepend to the alert message subject line
        required: false
    stored_vm_quota:
        description:
            - quota of vApps that this user can store
        required: false
    deployed_vm_quota:
        description:
            - quota of vApps that this user can deploy concurrently
        required: false
    is_group_role:
        description:
            - indicates if the user has a group role
        required: false
    is_default_cached:
        description:
            - indicates if user should be cached
        required: false
    is_external:
        description:
            - indicates if user is imported from an external source
        required: false
    is_alert_enabled:
        description:
            - True if the alert email address is enabled else False
        required: false
    is_enabled:
        description:
            - True if the user is enabled else False
        required: false
    state:
        description:
            - state of the user ('present'/'absent'/'update')
        required: false

author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_user:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    org: Terraform
    api_version: 30
    verify_ssl_certs: False
    username: "pcp_pcp_google_4"
    userpassword: "123456"
    role_name: "Organization Administrator"
    full_username: "USER_FULL_NAME"
    description: "USER_DESCRIPTION"
    email: "USER_EMAIL"
    telephone: "12345678"
    im: "i_m_val"
    alert_email: "ALERT_EMAIL"
    alert_email_prefix: "ALERT_EMAIL_PREFIX"
    stored_vm_quota: 0
    deployed_vm_quota: 0
    is_group_role: False
    is_default_cached: False
    is_external: False
    is_alert_enabled: False
    is_enabled: True
    state: "present"
'''

RETURN = '''
msg: success/failure message corresponding to user state/operation
changed: true if resource has been changed else false
'''

from pyvcloud.vcd.org import Org
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException


USER_STATES = ['present', 'absent', 'update']


def user_argument_spec():
    return dict(
        username=dict(type='str', required=True),
        userpassword=dict(type='str', required=False),
        role_name=dict(type='str', required=False),
        full_username=dict(type='str', required=False, default=''),
        description=dict(type='str', required=False, default=''),
        email=dict(type='str', required=False, default=''),
        telephone=dict(type='str', required=False, default=''),
        im=dict(type='str', required=False, default=''),
        alert_email=dict(type='str', required=False, default=''),
        alert_email_prefix=dict(type='str', required=False, default=''),
        stored_vm_quota=dict(type='str', required=False, default=0),
        deployed_vm_quota=dict(type='str', required=False, default=0),
        is_group_role=dict(type='bool', required=False, default=False),
        is_default_cached=dict(type='bool', required=False, default=False),
        is_external=dict(type='bool', required=False, default=False),
        is_alert_enabled=dict(type='bool', required=False, default=False),
        is_enabled=dict(type='bool', required=False, default=True),
        state=dict(choices=USER_STATES, required=False),
    )


class User(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        logged_in_org = self.client.get_org()
        self.org = Org(self.client, resource=logged_in_org)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.create()

        if state == "absent":
            return self.delete()

        if state == "update":
            return self.update()

    def create(self):
        params = self.params
        role = self.org.get_role_record(params.get('role_name'))
        role_href = role.get('href')
        username = params.get('username')
        userpassword = params.get('userpassword')
        full_username = params.get('full_username')
        description = params.get('description')
        email = params.get('email')
        telephone = params.get('telephone')
        im = params.get('im')
        alert_email = params.get('alert_email')
        alert_email_prefix = params.get('alert_email_prefix')
        stored_vm_quota = params.get('stored_vm_quota')
        deployed_vm_quota = params.get('deployed_vm_quota')
        is_group_role = params.get('is_group_role')
        is_default_cached = params.get('is_default_cached')
        is_external = params.get('is_external')
        is_alert_enabled = params.get('is_alert_enabled')
        is_enabled = params.get('is_enabled')
        response = dict()
        response['changed'] = False

        try:
            self.org.get_user(username)
        except EntityNotFoundException:
            self.org.create_user(
                username, userpassword, role_href, full_username, description,
                email, telephone, im, alert_email, alert_email_prefix,
                stored_vm_quota, deployed_vm_quota, is_group_role,
                is_default_cached, is_external, is_alert_enabled,
                is_enabled)
            response['msg'] = "User {} has been created.".format(username)
            response['changed'] = True
        else:
            response['warnings'] = "User {} is already present.".format(username)

        return response

    def delete(self):
        username = self.params.get('username')
        response = dict()
        response['changed'] = False

        try:
            self.org.get_user(username)
        except EntityNotFoundException:
            response['warnings'] = "User {} is not present.".format(username)
        else:
            self.org.delete_user(username)
            response['msg'] = "User {} has been deleted.".format(username)
            response['changed'] = True

        return response

    def update(self):
        username = self.params.get('username')
        enabled = self.params.get('is_enabled')
        response = dict()
        response['changed'] = False

        self.org.get_user(username)
        self.org.update_user(username, enabled)
        response['msg'] = "User {} has been updated".format(username)
        response['changed'] = True

        return response


def main():
    argument_spec = user_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = User(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if not module.params.get('state'):
            raise Exception('Please provide the state for the resource.')

        response = module.manage_states()
        module.exit_json(**response)

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)


if __name__ == '__main__':
    main()
