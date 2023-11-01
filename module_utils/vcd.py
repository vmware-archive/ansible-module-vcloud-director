# Copyright © 2018 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause OR GPL-3.0-only

from lxml import etree
from pyvcloud.vcd.client import Client
from pyvcloud.vcd.client import TaskStatus
from ansible.module_utils.basic import AnsibleModule, env_fallback
from pyvcloud.vcd.client import BasicLoginCredentials
from requests.packages import urllib3
from requests import post

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def vcd_argument_spec():
    return dict(
        user=dict(type='str', required=True, fallback=(env_fallback, ['env_user'])),
        password=dict(type='str', required=True, no_log=True, fallback=(env_fallback, ['env_password'])),
        org=dict(type='str', required=True, fallback=(env_fallback, ['env_org'])),
        host=dict(type='str', required=True, fallback=(env_fallback, ['env_host'])),
        api_version=dict(type='str', fallback=(env_fallback, ['env_api_version']), default='30.0'),
        verify_ssl_certs=dict(type='bool', fallback=(env_fallback, ['env_verify_ssl_certs']), default=False)
    )


class VcdAnsibleModule(AnsibleModule):
    def __init__(self, *args, **kwargs):
        argument_spec = vcd_argument_spec()
        argument_spec.update(kwargs.get('argument_spec', dict()))
        kwargs['argument_spec'] = argument_spec

        super(VcdAnsibleModule, self).__init__(*args, **kwargs)
        self.login()

    def login(self):
        try:
            user = self.params.get('user')
            password = self.params.get('password')
            org = self.params.get('org')
            host = self.params.get('host')
            api_version = self.params.get('api_version')
            verify_ssl_certs = self.params.get('verify_ssl_certs')
            self.client = Client(host,
                                 api_version=api_version,
                                 verify_ssl_certs=verify_ssl_certs)

            if user == 'API_TOKEN':
                oAuthResponse = post(
                    'https://{}/oauth/tenant/{}/token'.format(host, org),
                    data={'grant_type': 'refresh_token', 'refresh_token': password},
                ).json()
                access_token = oAuthResponse['access_token']
                self.client.rehydrate_from_token(access_token, True)
            else:
                self.client.set_credentials(BasicLoginCredentials(user, org, password))

        except Exception as error:
            self.fail_json(msg='Login failed for user {} to org {}'.format(user, org))

    def execute_task(self, task):
        task_monitor = self.client.get_task_monitor()
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
            raise Exception(etree.tostring(task_state, pretty_print=True))

        return 1
