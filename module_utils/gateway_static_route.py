
from pyvcloud.vcd.static_route import StaticRoute
from pyvcloud.vcd.exceptions import BadRequestException
from pyvcloud.vcd.exceptions import EntityNotFoundException


class StaticRoutes():
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
            return self.get_static_routes()

        raise Exception("Please provide a valid operation for the service")

    def _update_response(self, response, msg, warnings):
        if response['msg']:
            response['msg'] = msg.format(response['msg'])
        if response['warnings']:
            response['warnings'] = warnings.format(response['warnings'])

        return response

    def get_static_routes(self):
        response = dict()
        response['changed'] = False

        response['msg'] = self.gateway.list_static_routes()
        return response

    def is_route_present(self, network):
        for route in self.gateway.list_static_routes():
            if route['Network'] == network:
                return True
        raise EntityNotFoundException()

    def add(self):
        response = dict()
        response['changed'] = False
        response['warnings'] = list()
        response['msg'] = list()
        msg = 'Static Route(s) {0} have been created'
        warnings = 'Static Route(s) {0} may already present'

        for service_param in self.service_params:
            try:
                network = service_param.get("network")
                next_hop = service_param.get("next_hop")
                mtu = service_param.get("mtu") or 1500
                description = service_param.get("description")
                route_type = service_param.get("route_type") or 'User'
                vnic = service_param.get("vnic") or 0

                self.gateway.add_static_route(network=network,
                                              next_hop=next_hop,
                                              mtu=mtu,
                                              description=description,
                                              type=route_type,
                                              vnic=vnic)
            except BadRequestException:
                response['warnings'].append(network)
            else:
                response['msg'].append(network)
                response['changed'] = True

        return self._update_response(response, msg, warnings)

    def update(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()
        response['warnings'] = list()
        msg = 'Static Route(s) {0} have been updated'
        warnings = 'Static Route(s) {0} are not present'

        for service_param in self.service_params:
            try:
                network = service_param.get("network")
                new_network = service_param.get("new_network") or network
                next_hop = service_param.get("next_hop")
                mtu = service_param.get("mtu") or 1500
                description = service_param.get("description")
                vnic = service_param.get("vnic") or 0

                if self.is_route_present(network):
                    static_route = StaticRoute(client=self.gateway.client,
                                               gateway_name=self.gateway.name,
                                               route_network_id=network)
                    static_route.update_static_route(network=new_network,
                                                     next_hop=next_hop,
                                                     mtu=mtu,
                                                     description=description,
                                                     vnic=vnic)
                    response['msg'].append(network)
                    response['changed'] = True
            except EntityNotFoundException:
                response['warnings'].append(network)

        return self._update_response(response, msg, warnings)

    def delete(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()
        response['warnings'] = list()
        msg = 'Static Route(s) {0} have been deleted'
        warnings = 'Static Route(s) {0} are not present'

        for service_param in self.service_params:
            try:
                network = service_param.get("network")
                if self.is_route_present(network):
                    static_route = StaticRoute(client=self.gateway.client,
                                               gateway_name=self.gateway.name,
                                               route_network_id=network)
                    static_route.delete_static_route()
                    response['msg'].append(network)
                    response['changed'] = True
            except EntityNotFoundException:
                response['warnings'].append(network)

        return self._update_response(response, msg, warnings)
