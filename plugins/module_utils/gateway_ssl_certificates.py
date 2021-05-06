
from pyvcloud.vcd.certificate import Certificate


class SSLCertificates():
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
            return self.get_ssl_certificates()

        raise Exception("Please provide a valid operation for the service")

    def get_service_certificates(self):
        response = list()
        for certs in self.gateway.list_service_certificates():
            response.append({
                'name': str(certs["Name"]),
                'object_id': str(certs["Object_Id"])
            })

        return response

    def get_ca_certificates(self):
        response = list()
        for certs in self.gateway.list_ca_certificates():
            response.append({
                'name': str(certs["Name"]),
                'object_id': str(certs["Object_Id"])
            })

        return response

    def get_crl_certificates(self):
        response = list()
        for certs in self.gateway.list_crl_certificates():
            response.append({
                'name': str(certs["Name"]),
                'object_id': str(certs["Object_Id"])
            })

        return response

    def get_ssl_certificates(self):
        response = dict()
        response['changed'] = False
        response['msg'] = self.get_service_certificates(
        ) + self.get_ca_certificates() + self.get_crl_certificates()

        return response

    def add(self):
        response = dict()
        response['changed'] = False
        response['warnings'] = list()
        response['msg'] = list()
        msg = 'SSL Certificates have been added'

        for service_param in self.service_params:
            cert_type = service_param.get("cert_type") or 'service'
            if cert_type == 'service':
                self.add_service_certificate(service_param)
            if cert_type == 'ca':
                self.add_ca_certificate(service_param)
            if cert_type == 'crl':
                self.add_crl_certificate(service_param)

            response['msg'] = msg
            response['changed'] = True

        return response

    def add_service_certificate(self, service_param):
        cert_file_path = service_param.get('cert_file_path')
        key_file_path = service_param.get('key_file_path')
        key_passphrase = service_param.get('key_passphrase')
        description = service_param.get('description')

        return self.gateway.add_service_certificate(
            cert_file_path, key_file_path, key_passphrase, description)

    def add_ca_certificate(self, service_param):
        cert_file_path = service_param.get('cert_file_path')
        description = service_param.get('description')

        return self.gateway.add_ca_certificate(cert_file_path, description)

    def add_crl_certificate(self, service_param):
        cert_file_path = service_param.get('cert_file_path')
        description = service_param.get('description')

        return self.gateway.add_crl_certificate(cert_file_path, description)

    def delete(self):
        response = dict()
        response['changed'] = False
        response['msg'] = list()
        response['warnings'] = list()
        msg = 'SSL Certificates have been deleted'

        for service_param in self.service_params:
            cert_type = service_param.get("cert_type") or 'service'
            if cert_type == 'service':
                self.delete_service_certificate(service_param)
            if cert_type == 'ca':
                self.delete_ca_certificate(service_param)
            if cert_type == 'crl':
                self.delete_crl_certificate(service_param)

            response['msg'] = msg
            response['changed'] = True

        return response

    def delete_service_certificate(self, service_param):
        service_certs = self.get_service_certificates()
        cert_name = service_param.get("cert_name")
        for service_cert in service_certs:
            if service_cert.get("name") == cert_name:
                cert = Certificate(client=self.gateway.client,
                                   gateway_name=self.gateway.name,
                                   resource_id=service_cert.get("object_id"))
                cert.delete_certificate()

    def delete_ca_certificate(self, service_param):
        ca_certs = self.get_ca_certificates()
        cert_name = service_param.get("cert_name")
        for ca_cert in ca_certs:
            if ca_cert.get("name") == cert_name:
                cert = Certificate(client=self.gateway.client,
                                   gateway_name=self.gateway.name,
                                   resource_id=ca_cert.get("object_id"))
                cert.delete_certificate()

    def delete_crl_certificate(self, service_param):
        crl_certs = self.get_crl_certificates()
        cert_name = service_param.get("cert_name")
        for crl_cert in crl_certs:
            if crl_cert.get("name") == cert_name:
                cert = Certificate(client=self.gateway.client,
                                   gateway_name=self.gateway.name,
                                   resource_id=crl_cert.get("object_id"))
                cert.delete_certificate()
