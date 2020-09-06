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
            - A dict type respective service parameters
        required: false
        type: dict
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
        name: test_firewall
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
from pyvcloud.vcd.firewall_rule import FirewallRule
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException


EDGE_SERVICES = ["firewall"]
EDGE_SERVICES_STATES = ['present', 'update', 'absent']
EDGE_SERVICES_OPERATIONS = ['list']


def vcd_gateway_services_argument_spec():
    return dict(
        vdc=dict(type='str', required=True),
        gateway=dict(type='str', required=True),
        service_params=dict(type='dict', required=False),
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

    def get_gateway(self, gateway_name):
        gateway = self.vdc.get_gateway(gateway_name)
        if gateway is None:
            msg = "Gateway {0} not found".format(gateway_name)
            raise EntityNotFoundException(msg)

        extra_args = {"name": gateway_name, "href": gateway.get("href")}
        return Gateway(self.client, **extra_args)

    def add_service(self):
        service = self.params.get("service")
        gateway_name = self.params.get("gateway")
        service_params = self.params.get("service_params")
        gateway = self.get_gateway(gateway_name)
        if service == "firewall":
            service = FirewallService(gateway, service_params)

        return service.manage_states(state="present")

    def delete_service(self):
        service = self.params.get("service")
        gateway_name = self.params.get("gateway")
        service_params = self.params.get("service_params")
        gateway = self.get_gateway(gateway_name)
        if service == "firewall":
            service = FirewallService(gateway, service_params)

        return service.manage_states(state="absent")

    def update_service(self):
        service = self.params.get("service")
        gateway_name = self.params.get("gateway")
        service_params = self.params.get("service_params")
        gateway = self.get_gateway(gateway_name)
        if service == "firewall":
            service = FirewallService(gateway, service_params)

        return service.manage_states(state="update")

    def apply_operation_on_service(self, operation):
        service = self.params.get("service")
        gateway_name = self.params.get("gateway")
        gateway = self.get_gateway(gateway_name)
        if service == "firewall":
            service = FirewallService(gateway)

        return service.manage_operations(operation=operation)


class FirewallService():
    def __init__(self, gateway, service_params=None):
        self.gateway = gateway
        self.service_params = service_params

    def _get_firewall_rules(self):
        return self.gateway.get_firewall_rules_list()

    def _get_firewall_rule(self, firewall_rule_name):
        firewall_rules = self._get_firewall_rules()
        for firewall_rule in firewall_rules:
            if firewall_rule["name"] == firewall_rule_name:
                firewall_rule = FirewallRule(client=self.gateway.client,
                                             gateway_name=self.gateway.name,
                                             resource_id=firewall_rule["ID"])
                return firewall_rule

        msg = "Firewall rule {0} does not exists"
        raise EntityNotFoundException(msg.format(firewall_rule_name))

    def manage_states(self, state=None):
        if state == "present":
            return self._add()

        if state == "update":
            return self._update()

        if state == "absent":
            return self._delete()

        raise Exception("Please provide a valid state for the service")

    def manage_operations(self, operation=None):
        if operation == "list":
            return self._list_firewall_rules()

        raise Exception("Please provide a valid operation for the service")

    def _add(self):
        name = self.service_params.get("name")
        action = self.service_params.get("action", 'accept')
        firewall_type = self.service_params.get("type", 'User')
        enabled = self.service_params.get("enabled", True)
        logging_enabled = self.service_params.get("logging_enabled", False)
        response = dict()
        response['changed'] = False

        try:
            self._get_firewall_rule(name)
        except EntityNotFoundException:
            self.gateway.add_firewall_rule(name=name, action=action,
                                           type=firewall_type, enabled=enabled,
                                           logging_enabled=logging_enabled)
            msg = "A new firewall rule {0} has been added"
            response['msg'] = msg.format(name)
            response['changed'] = True
        else:
            msg = "A firewall rule {0} is already present"
            response['warnings'] = msg.format(name)

        return response

    def _delete(self):
        name = self.service_params.get("name")
        response = dict()
        response['changed'] = False

        try:
            firewall_rule = self._get_firewall_rule(name)
        except EntityNotFoundException:
            msg = "firewall rule {0} does not exists"
            response['warnings'] = msg.format(name)
        else:
            firewall_rule.delete()
            msg = "firewall rule {0} has been deleted"
            response['msg'] = msg.format(name)
            response['changed'] = True

        return response

    def _list_firewall_rules(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()
        for firewall_rule in self._get_firewall_rules():
            res = {
                "name": str(firewall_rule["name"]),
                "id": int(firewall_rule["ID"]),
                "type": str(firewall_rule["ruleType"])
            }
            response['msg'].append(res)

        return response

    def _prepare_service_values(self, services):
        if services is not None:
            for service in services:
                for name, value in service.items():
                    value[value["source_port"]] = value["destination_port"]
                    del value["destination_port"], value["source_port"]

        return services

    def _prepare_route_values(self, route_values):
        response = list()
        if route_values is not None:
            for route, values in route_values.items():
                response.append("{0}:{1}".format(values, route))

        return response

    def _update(self):
        name = self.service_params.get("name")
        new_name = self.service_params.get("new_name", name)
        services = self.service_params.get("services", None)
        source_values = self.service_params.get("source_values", None)
        destination_values = self.service_params.get(
            "destination_values", None)
        response = dict()
        response['changed'] = False

        try:
            firewall_rule = self._get_firewall_rule(name)
        except EntityNotFoundException:
            msg = "firewall rule {0} does not exists"
            response['warnings'] = msg.format(name)
        else:
            services = self._prepare_service_values(services)
            source_values = self._prepare_route_values(source_values)
            destination_values = self._prepare_route_values(destination_values)
            firewall_rule.edit(source_values=source_values, services=services,
                               destination_values=destination_values,
                               new_name=new_name)
            msg = "A firewall rule {0} has been updated with {1}"
            response['msg'] = msg.format(name, new_name)
            response['changed'] = True

        return response


def main():
    argument_spec = vcd_gateway_services_argument_spec()
    response = dict(msg=dict(type='str'))
    module = EdgeServices(argument_spec=argument_spec, supports_check_mode=True)

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
