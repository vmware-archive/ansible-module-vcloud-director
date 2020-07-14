#!/usr/bin/python

# Copyright © 2018 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause OR GPL-3.0-only

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: vcd_get_edge_name_by_org
short_description: Fetch EDGE Name by running vcd_get_edge_name_by_org's provides read operations in vCloud Director Resources by Organization
version_added: "2.4"
description:
    - Fetch EDGE Name by running vcd_get_edge_name_by_org's provides read operations in vCloud Director Resources by Organization

options:
    user:
        description:
            - vCloud Director user name
        required: true
    password:
        description:
            - vCloud Director user password
        required: true
    host:
        description:
            - vCloud Director host address
        required: true
    org:
        description:
            - Organization name on vCloud Director to access
        required: true
    org_name:
        description:
            - Organization name on vCloud Director to access
        required: true
    api_version:
        description:
            - Pyvcloud API version
        required: false
    verify_ssl_certs:
        description:
            - whether to use secure connection to vCloud Director host
        required: bool
    vdc:
        description:
            - The name of the new vdc
        type: str
    vdc_org_name:
        description:
            - The name of organization the new vdc associated with
        type: str
    operation:
        description:
            - operation to perform on vcd_get_resources_by_org (read/list_networks).
            - One of operation/state has to be provided.
        required: true
author:
    Rostisalv Grigoriev - ros@woinc.ru
'''

EXAMPLES = '''
- name: Get vCloud Director Resources by Organization and Virtual Cloud Datacenter
  vcd_get_resources_by_org:
    org_name: "AIM"
    org: AIM
    vdc: "AIM_VCD01"
    vdc_org_name: AIM
    host: "vcd.example.com"
    verify_ssl_certs: False
    user: "test-user"
    password: "12345"
    operation: read
  register: output
'''

RETURN = '''
msg: success/failure message corresponding to catalog item state/operation
changed: true if resource has been changed else false
'''

from ansible.module_utils.vcd import VcdAnsibleModule
import time
import sys
import requests
from pyvcloud.vcd.system import System
from pyvcloud.vcd.platform import Platform
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.client import Client

VAPP_NETWORK_OPERATIONS = ["read_and_return"]

def vapp_network_argument_spec():
    return dict(
        host=dict(type='str', required=True),
        user=dict(type='str', required=True),
        password=dict(type='str', required=True),
        vdc=dict(type='str', required=True),
        vdc_org_name=dict(type='str', required=True),
        api_version=dict(type='str', required=True),
        org_name=dict(type='str', required=True),
        org=dict(type='str', required=True),
        operation=dict(choices=VAPP_NETWORK_OPERATIONS, required=False),
)

class VcdResource(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VcdResource, self).__init__(**kwargs)
        operation = self.params.get('operation')
        vdc = self.params.get('vdc')
        org_name = self.params.get('org_name')
        org = self.params.get('org')
        name = self.params.get('name')
        host = self.params.get('host')
        user = self.params.get('user')
        password = self.params.get('password')
        vdc_org_name = self.params.get('vdc_org_name')
        self.operation = operation
        self.vdc = vdc
        self.org_name = org_name
        self.org = org
        self.name = name
        self.host = host
        self.user = user
        self.password = password
        self.vdc_org_name = vdc_org_name
        
    def get_vdc_org_resource(self):
        if self.params.get(self.vdc_org_name):
            return self.client.get_org_by_name(self.params.get(self.vdc_org_name))
        return self.client.get_org()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "read_and_return":
            return self.read_and_return()

    def read_and_return(self):
        response = dict()
        vdc_resources = dict()
        vdc_resources = self.get_vdc_org_resource()
        self.vdc_resources = vdc_resources
        self.org = Org(self.client, resource=self.client.get_org())
        platform = ""
        #platform = Platform(self.org.client)
        self.platform = platform
        vddc_name = self.vdc_org_name
        vdc_response = VDC(self.client, name=self.vdc, resource=(self.org.get_vdc(self.vdc)))
        result = vdc_response.list_edge_gateways()
        response['edge-gw'] = result
        for e in result:
                del e['href']
        self.vdc_response = vdc_response
        response['changed'] = True
        return response

def main():

    argument_spec = vapp_network_argument_spec()
    response = dict(msg=dict(type='str'))
    module = VcdResource(argument_spec=argument_spec, supports_check_mode=True)
    # return response

    try:
        if module.params.get('operation'):
            response = module.manage_operations()
        else:
            raise Exception('Please provide the state for the resource')

        module.exit_json(**response)

    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)
    
if __name__ == '__main__':
    main()

