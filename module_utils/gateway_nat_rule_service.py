
from pyvcloud.vcd.nat_rule import NatRule
from pyvcloud.vcd.utils import build_network_url_from_gateway_url
from pyvcloud.vcd.network_url_constants import NAT_RULE_URL_TEMPLATE


class NatRuleService():
    def __init__(self, gateway, service_params=None):
        self.gateway = gateway
        self.service_params = service_params

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
            return self.get_nat_rules()

        raise Exception("Please provide a valid operation for the service")

    def get_nat_rule_href(self, nat_rule_id):
        network_url = build_network_url_from_gateway_url(self.gateway.href)
        nat_href = network_url + NAT_RULE_URL_TEMPLATE

        return nat_href.format(nat_rule_id)

    def get_nat_rules(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        nat_rules_resource = self.gateway.get_nat_rules()
        if (hasattr(nat_rules_resource.natRules, 'natRule')):
            for nat_rule in nat_rules_resource.natRules.natRule:
                nat_rule_info = {}
                nat_rule_info['ID'] = int(nat_rule.ruleId)
                nat_rule_info['Action'] = str(nat_rule.action)
                nat_rule_info['Enabled'] = str(nat_rule.enabled)
                if hasattr(nat_rule, 'description'):
                    nat_rule_info['Description'] = str(nat_rule.description)
                nat_rule_info['href'] = self.get_nat_rule_href(
                    nat_rule_info['ID'])
                response['msg'].append(nat_rule_info)

        return response

    def add(self):
        response = dict()
        response['changed'] = False

        for service_param in self.service_params:
            action = service_param.get("action")
            original_address = service_param.get("original_address")
            translated_address = service_param.get("translated_address")
            description = service_param.get("description", '')
            protocol = service_param.get("protocol", 'any')
            original_port = service_param.get("original_port", 'any')
            translated_port = service_param.get("translated_port", 'any')
            access_type = service_param.get("access_type", 'User')
            icmp_type = service_param.get("icmp_type", 'any')
            enabled = service_param.get("enabled", True)
            logging_enabled = service_param.get("logging_enabled", False)
            vnic = service_param.get("vnic", 0)

            self.gateway.add_nat_rule(action, original_address,
                                      translated_address, description,
                                      protocol, original_port,
                                      translated_port, access_type,
                                      icmp_type, logging_enabled,
                                      enabled, vnic)
        response['msg'] = 'Nat rule(s) are added'
        response['changed'] = True

        return response

    def update(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        for service_param in self.service_params:
            nat_rule_id = service_param.get("nat_rule_id")
            original_address = service_param.get("original_address")
            translated_address = service_param.get("translated_address")
            description = service_param.get("description", '')
            protocol = service_param.get("protocol", 'any')
            original_port = service_param.get("original_port", 'any')
            translated_port = service_param.get("translated_port", 'any')
            icmp_type = service_param.get("icmp_type", 'any')
            enabled = service_param.get("enabled", True)
            logging_enabled = service_param.get("logging_enabled", False)
            vnic = service_param.get("vnic", 0)
            nat_rule_obj = NatRule(client=self.gateway.client,
                                   gateway_name=self.gateway.name,
                                   rule_id=nat_rule_id)
            nat_rule_obj.href = self.get_nat_rule_href(nat_rule_id)
            nat_rule_obj.update_nat_rule(
                original_address,
                translated_address,
                description,
                protocol,
                original_port,
                translated_port,
                icmp_type,
                logging_enabled,
                enabled,
                vnic
            )
            response['msg'].append(nat_rule_id)
        response['msg'] = 'Nat rule(s) {0} are updated'.format(response['msg'])
        response['changed'] = True

        return response

    def delete(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()

        for service_param in self.service_params:
            nat_rule_id = service_param.get("nat_rule_id")
            nat_rule_obj = NatRule(client=self.gateway.client,
                                   gateway_name=self.gateway.name,
                                   rule_id=nat_rule_id)
            nat_rule_obj.href = self.get_nat_rule_href(nat_rule_id)
            nat_rule_obj.delete_nat_rule()
            response['msg'].append(nat_rule_id)
        response['msg'] = 'Nat rule(s) {0} are deleted'.format(response['msg'])
        response['changed'] = True

        return response
