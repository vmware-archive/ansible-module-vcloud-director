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
module: vcd_gateway_services
short_description: Manage edge gateway service in vCloud Director
version_added: "2.7"
description:
    - Manage edge gateway service in vCloud Director

options:
    user:
        description:
            - vCloud Director user name
        type: str
        required: false
    password:
        description:
            - vCloud Director user password
        type: str
        required: false
    host:
        description:
            - vCloud Director host address
        type: str
        required: false
    org:
        description:
            - Organization name on vCloud Director to access
        type: str
        required: false
    api_version:
        description:
            - Pyvcloud API version
        type: float
        required: false
    verify_ssl_certs:
        description:
            - whether to use secure connection to vCloud Director host
        type: bool
        required: false
    org_name:
        description:
            - target org name
            - required for service providers to create resources in other orgs
            - default value is module level / environment level org
        required: false
    vdc:
        description:
            - vdc name
        required: true
        type: str
    service:
        description:
            - The name of the edge gateway service
            - supported services are
                - firewall
                - nat_rule
                - static_route
                - ssl_certificates
        required: true
        type: str
    service_params:
        description:
            - A list type respective service parameters
        required: false
        type: list
    state:
        description:
            - State of the edge gateway service
        type: string
        required: true
        choices: ['present', 'update', 'absent']
    operation:
        description:
            - Operation on the edge gateway service
        type: string
        required: false
        choices: ['list']

author:
    - Mukul Taneja  <mtaneja@vmware.com>
'''

EXAMPLES = '''
- name: create gateway services
  vcd_gateway_services:
     user: acmeadmin
     password: *******
     org: Acme
     vdc: ACME_PAYG
     gateway: edge-gateway
     service: firewall
     service_params:
        - name: test_firewall
          action: accept
          type: User
          enabled: True
          logging_enabled: False
     state: present

'''


RETURN = '''
msg: success/failure message corresponding to edge gateway state
changed: true if resource has been changed else false
'''

from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.gateway import Gateway
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException
from ansible.module_utils.gateway_static_route import StaticRoutes
from ansible.module_utils.gateway_nat_rule_service import NatRuleService
from ansible.module_utils.gateway_firewall_service import FirewallService
from ansible.module_utils.gateway_ssl_certificates import SSLCertificates


EDGE_SERVICES = ["firewall", "nat_rule", "static_route", "ssl_certificates"]
EDGE_SERVICES_STATES = ['present', 'update', 'absent']
EDGE_SERVICES_OPERATIONS = ['list']


def vcd_gateway_services_argument_spec():
    return dict(
        vdc=dict(type='str', required=True),
        gateway=dict(type='str', required=True),
        service_params=dict(type='list', required=False),
        service=dict(choices=EDGE_SERVICES, required=True),
        org_name=dict(type='str', required=False, default=None),
        state=dict(choices=EDGE_SERVICES_STATES, required=False),
        operation=dict(choices=EDGE_SERVICES_OPERATIONS, required=False)
    )


class EdgeServices(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(EdgeServices, self).__init__(**kwargs)
        self.org = self.get_org()
        vdc = self.org.get_vdc(self.params.get('vdc'))
        self.vdc = VDC(self.client, href=vdc.get('href'))

    def manage_states(self):
        state = self.params.get("state")
        if state == "present":
            return self.add_service()

        if state == "update":
            return self.update_service()

        if state == "absent":
            return self.delete_service()

    def manage_operations(self):
        operation = self.params.get("operation")

        return self.apply_operation_on_service(operation)

    def get_org(self):
        org_name = self.params.get('org_name')
        org_resource = self.client.get_org()
        if org_name:
            org_resource = self.client.get_org_by_name(org_name)

        return Org(self.client, resource=org_resource)

    def get_gateway(self):
        gateway_name = self.params.get("gateway")
        gateway = self.vdc.get_gateway(gateway_name)
        if gateway is None:
            msg = "Gateway {0} not found".format(gateway_name)
            raise EntityNotFoundException(msg)

        extra_args = {"name": gateway_name, "href": gateway.get("href")}
        return Gateway(self.client, **extra_args)

    def add_service(self):
        service = self.params.get("service")
        service_params = self.params.get("service_params")
        if service == "firewall":
            service = FirewallService(self.get_gateway(), service_params)

        if service == "nat_rule":
            service = NatRuleService(self.get_gateway(), service_params)

        if service == "static_route":
            service = StaticRoutes(self.get_gateway(), service_params)

        if service == "ssl_certificates":
            service = SSLCertificates(self.get_gateway(), service_params)

        return service.manage_states(state="present")

    def delete_service(self):
        service = self.params.get("service")
        service_params = self.params.get("service_params")
        if service == "firewall":
            service = FirewallService(self.get_gateway(), service_params)

        if service == "nat_rule":
            service = NatRuleService(self.get_gateway(), service_params)

        if service == "static_route":
            service = StaticRoutes(self.get_gateway(), service_params)

        if service == "ssl_certificates":
            service = SSLCertificates(self.get_gateway(), service_params)

        return service.manage_states(state="absent")

    def update_service(self):
        service = self.params.get("service")
        service_params = self.params.get("service_params")
        if service == "firewall":
            service = FirewallService(self.get_gateway(), service_params)

        if service == "nat_rule":
            service = NatRuleService(self.get_gateway(), service_params)

        if service == "static_route":
            service = StaticRoutes(self.get_gateway(), service_params)

        return service.manage_states(state="update")

    def apply_operation_on_service(self, operation):
        service = self.params.get("service")
        if service == "firewall":
            service = FirewallService(self.get_gateway())

        if service == "nat_rule":
            service = NatRuleService(self.get_gateway())

        if service == "static_route":
            service = StaticRoutes(self.get_gateway())

        if service == "ssl_certificates":
            service = SSLCertificates(self.get_gateway())

        return service.manage_operations(operation=operation)


def main():
    argument_spec = vcd_gateway_services_argument_spec()
    response = dict(msg=dict(type='str'))
    module = EdgeServices(
        argument_spec=argument_spec, supports_check_mode=True)

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
            raise Exception('Please provide state for resource')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
