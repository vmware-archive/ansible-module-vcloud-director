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
client: vcd_user
short_description: This module helps to manage users on vCloud Director.
version_added: "2.4"
description:
    - "This module helps to manage users on vCloud Director."
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
            - state of the user ('present'/'absent')
        required: false
    operation:
        description:
            - operations performed for the user ('update')
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
result: success/failure message relates to vapp_vm operation
'''

from pyvcloud.vcd.org import Org
from ansible.module_utils.vcd import VcdAnsibleModule


USER_STATES = ['present', 'absent']
USER_OPERATIONS = ['update']


def user_argument_spec():
    return dict(
        username=dict(type='str', required=False),
        userpassword=dict(type='str', required=False),
        role_name=dict(type='str', required=False),
        full_username=dict(type='str', required=False),
        description=dict(type='str', required=False),
        email=dict(type='str', required=False),
        telephone=dict(type='str', required=False),
        im=dict(type='str', required=False),
        alert_email=dict(type='str', required=False),
        alert_email_prefix=dict(type='str', required=False),
        stored_vm_quota=dict(type='str', required=False),
        deployed_vm_quota=dict(type='str', required=False),
        is_group_role=dict(type='str', required=False),
        is_default_cached=dict(type='str', required=False),
        is_external=dict(type='str', required=False),
        is_alert_enabled=dict(type='str', required=False),
        is_enabled=dict(type='str', required=False),
        state=dict(choices=USER_STATES, required=False),
        operation=dict(choices=USER_OPERATIONS, required=False)
    )


class User(object):
    def __init__(self, module):
        self.module = module

    def get_org(self):
        client = self.module.client
        logged_in_org = client.get_org()

        return Org(client, resource=logged_in_org)

    def create(self):
        params = self.module.params
        org = self.get_org()
        role = org.get_role_record(params.get('role_name'))
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

        org.create_user(
            username, userpassword, role_href, full_username, description,
            email, telephone, im, alert_email, alert_email_prefix,
            stored_vm_quota, deployed_vm_quota, is_group_role,
            is_default_cached, is_external, is_alert_enabled,
            is_enabled)
        response['msg'] = 'User {} has been created.'.format(username)
        response['changed'] = True

        return response

    def delete(self):
        params = self.module.params
        org = self.get_org()
        username = params.get('username')
        response = dict()

        org.delete_user(username)
        response['msg'] = 'User {} has been deleted.'.format(username)
        response['changed'] = True

        return response

    def update(self):
        params = self.module.params
        org = self.get_org()
        username = params.get('username')
        is_enabled = params.get('is_enabled')
        response = dict()

        org.update_user(username, is_enabled)
        response['msg'] = 'User {} has been updated.'.format(username)
        response['changed'] = True

        return response


def manage_user_states(user):
    params = user.module.params
    state = params.get('state')
    if state == "present":
        return user.create()

    if state == "absent":
        return user.delete()


def manage_user_operations(user):
    params = user.module.params
    operation = params.get('operation')

    if operation == "update":
        return user.update()


def main():
    argument_spec = user_argument_spec()
    response = dict(
        msg=dict(type='str')
    )

    module = VcdAnsibleModule(argument_spec=argument_spec,
                              supports_check_mode=True)

    try:
        user = User(module)

        if module.params.get('state'):
            response = manage_user_states(user)
        elif module.params.get('operation'):
            response = manage_user_operations(user)
        else:
            raise Exception('One of from state/operation should be provided.')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
