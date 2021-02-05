
import traceback
from pyvcloud.vcd.firewall_rule import FirewallRule
from pyvcloud.vcd.exceptions import BadRequestException
from pyvcloud.vcd.exceptions import EntityNotFoundException


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
                    if value[0].lower() == 'any':
                        return ['any']
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
                if 'any' in destination_values or 'any' in source_values:
                    continue
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
