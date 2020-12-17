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
    vdc:
        description:
            - vdc name
        required: true
        type: str
    service:
        description:
            - The name of the edge gateway service
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
import traceback
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.gateway import Gateway
from pyvcloud.vcd.firewall_rule import FirewallRule
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException, BadRequestException


EDGE_SERVICES = ["firewall"]
EDGE_SERVICES_STATES = ['present', 'update', 'absent']
EDGE_SERVICES_OPERATIONS = ['list']


def vcd_gateway_services_argument_spec():
    return dict(
        vdc=dict(type='str', required=True),
        gateway=dict(type='str', required=True),
        service_params=dict(type='list', required=False),
        service=dict(choices=EDGE_SERVICES, required=True),
        state=dict(choices=EDGE_SERVICES_STATES, required=False),
        operation=dict(choices=EDGE_SERVICES_OPERATIONS, required=False)
    )


class EdgeServices(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(EdgeServices, self).__init__(**kwargs)
        self.org = Org(self.client, resource=self.client.get_org())
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

        return service.manage_states(state="present")

    def delete_service(self):
        service = self.params.get("service")
        service_params = self.params.get("service_params")
        if service == "firewall":
            service = FirewallService(self.get_gateway(), service_params)

        return service.manage_states(state="absent")

    def update_service(self):
        service = self.params.get("service")
        service_params = self.params.get("service_params")
        if service == "firewall":
            service = FirewallService(self.get_gateway(), service_params)

        return service.manage_states(state="update")

    def apply_operation_on_service(self, operation):
        service = self.params.get("service")
        if service == "firewall":
            service = FirewallService(self.get_gateway())

        return service.manage_operations(operation=operation)


class FirewallService():
    def __init__(self, gateway, service_params=None):
        self.gateway = gateway
        self.service_params = service_params

    def get_firewall_rules(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        fw_rules = self.gateway.get_firewall_rules_list()
        for fw_rule in fw_rules:
            response['msg'].append({
                "name": str(fw_rule["name"]),
                "id": int(fw_rule["ID"]),
                "type": str(fw_rule["ruleType"])
            })

        return response

    def get_firewall_rule(self, fw_rule_name):
        fw_rules = self.get_firewall_rules()['msg']
        for fw_rule in fw_rules:
            if fw_rule["name"] == fw_rule_name:
                return FirewallRule(client=self.gateway.client,
                                    gateway_name=self.gateway.name,
                                    resource_id=fw_rule["id"])

        msg = "Firewall rule {0} does not exists"
        raise EntityNotFoundException(msg.format(fw_rule_name))

    def manage_states(self, state=None):
        if state == "present":
            return self.add()

        if state == "update":
            return self.update()

        if state == "absent":
            return self.delete()

        raise Exception("Please provide a valid state for the service")

    def manage_operations(self, operation=None):
        if operation == "list":
            return self.get_firewall_rules()

        raise Exception("Please provide a valid operation for the service")

    def _update_response(self, response, msg, warnings):
        if response['msg']:
            response['msg'] = msg.format(response['msg'])
        if response['warnings']:
            response['warnings'] = warnings.format(response['warnings'])

        return response

    def _prepare_service_values(self, services):
        if services is not None:
            for service in services:
                for name, value in service.copy().items():
                    service[name] = {
                        value["source_port"]: value["destination_port"]
                    }

        return services

    def _prepare_route_values(self, route_values):
        response = list()
        if route_values is not None:
            for route_value in route_values:
                for route, value in route_value.items():
                    response.append("{0}:{1}".format(value[0], route))

        return response

    def add(self):
        response = dict()
        response['changed'] = False
        response['warnings'] = list()
        response['msg'] = list()
        msg = 'Firewall rule(s) {0} have been created'
        warnings = 'Firewall rule(s) {0} are already present'

        for service_param in self.service_params:
            name = service_param.get("name")
            action = service_param.get("action") or 'accept'
            firewall_type = service_param.get("type") or 'User'
            enabled = service_param.get("enabled") or True
            logging_enabled = service_param.get("logging_enabled") or False

            try:
                self.get_firewall_rule(name)
            except EntityNotFoundException:
                self.gateway.add_firewall_rule(name=name, action=action,
                                               type=firewall_type,
                                               enabled=enabled,
                                               logging_enabled=logging_enabled)
                try:
                    self.update([service_param])
                except Exception:
                    self.delete([service_param])
                    raise Exception(traceback.format_exc())
                else:
                    response['msg'].append(name)
                    response['changed'] = True
            else:
                response['warnings'].append(name)

        return self._update_response(response, msg, warnings)

    def update(self, service_params=None):
        response = dict()
        response['changed'] = False
        response['msg'] = list()
        response['warnings'] = list()
        msg = 'Firewall rule(s) {0} have been updated'
        warnings = 'Firewall rule(s) {0} are not present'

        service_params = service_params or self.service_params
        for service_param in service_params:
            name = service_param.get("name")
            new_name = service_param.get("new_name") or name
            services = service_param.get("services") or None
            source_values = service_param.get("source_values") or None
            destination_values = service_param.get(
                "destination_values") or None

            try:
                firewall_rule = self.get_firewall_rule(name)
                services = self._prepare_service_values(services)
                source_values = self._prepare_route_values(source_values)
                destination_values = self._prepare_route_values(
                    destination_values)
                firewall_rule.edit(source_values=source_values,
                                   services=services,
                                   destination_values=destination_values,
                                   new_name=new_name)
                response['msg'].append(name)
                response['changed'] = True
            except EntityNotFoundException:
                response['warnings'].append(name)
            except BadRequestException as ex:
                raise Exception(ex)

        return self._update_response(response, msg, warnings)

    def delete(self, service_params=None):
        response = dict()
        response['changed'] = False
        response['msg'] = list()
        response['warnings'] = list()
        msg = 'Firewall rule(s) {0} have been deleted'
        warnings = 'Firewall rule(s) {0} are not present'

        service_params = service_params or self.service_params
        for service_param in service_params:
            try:
                name = service_param.get("name")
                firewall_rule = self.get_firewall_rule(name)
            except EntityNotFoundException:
                response['warnings'].append(name)
            else:
                firewall_rule.delete()
                response['msg'].append(name)
                response['changed'] = True

        return self._update_response(response, msg, warnings)


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
