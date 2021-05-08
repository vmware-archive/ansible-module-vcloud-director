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
module: vcd_vapp
short_description: Manage vApp's states/operations in vCloud Director
version_added: "2.4"
description:
    - Manage vApp's states/operations in vCloud Director

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
    org_name:
        description:
            - target org name
            - required for service providers to create resources in other orgs
            - default value is module level / environment level org
        required: false
    vapp_name:
        description:
            - Vapp name
        required: true
    vdc:
        description:
            - Org Vdc where this VAPP gets created
        required: true
    template_name:
        description:
            - source catalog item name
        required: false
    description:
        description:
            - vApp description
        required: false
    network:
        description:
            - org network for the vapp
        required: false
    fence_mode:
        description:
            - vApp fence mode
        required: false
    deploy:
        description:
            - true if to deploy vApp else false
        required: false
    power_on:
        description:
            - true if to power on vApp else false
        required: false
    accept_all_eulas:
        description:
            - true/false
        required: false
    disk_size:
        description:
            - vApp disk size
        required: false
    memory:
        description:
            - memory size in MB
        required: false
    cpu:
        description:
            - number of CPU
        required: false
    vmpassword:
        description:
            - vm password in vApps
        required: false
    cust_script:
        description:
            - vApp customization script
        required: false
    vm_name:
        description:
            - vm name in vApp
        required: false
    hostname:
        description:
            - vApp hostname
        required: false
    ip_address:
        description:
            - vApp ip address
        required: false
    ip_allocation_mode:
        description:
            - IP Allocation mode static/DHCP
        required: false
    storage_profile:
        description:
            - storage profile to use for the vapp
        required: false
    network_adapter_type:
        description:
            - network adapter type for vApp
        required: false
    force:
        description:
            - true if delete vApp forcefully else false
        required: false
    shared_access:
        description:
            - shared access for a vapp across the org.
            - Possible values could be 'ReadOnly', 'Change', 'FullControl'
        requried: false
    state:
        description:
            - state of new virtual machines (present/absent).
            - One from state or operation has to be provided.
        required: false
    operation:
        description:
            - operation to perform on vApp.
            - One from state or operation has to be provided.
        required: false

author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_vapp:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    org: Terraform
    api_version: 30
    verify_ssl_certs: False
    vapp_name = "vcdvapp"
    template_name = "vcdlab"
    catalog_name = "source1"
    vdc = "vdcname"
    network = "ORGNET1"
    ip_allocation_mode = "static"
    cpu = 4
    memory = 2000
    state="present"
    storage_profile = "SP_PERFORMANCE_SDD"
'''

RETURN = '''
msg: success/failure message corresponding to vapp state/operation
changed: true if resource has been changed else false
'''

from lxml import etree
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.client import NSMAP
from pyvcloud.vcd.client import FenceMode
from pyvcloud.vcd.client import MetadataDomain
from pyvcloud.vcd.client import MetadataValueType
from pyvcloud.vcd.client import MetadataVisibility
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException, OperationNotSupportedException, InvalidStateException


VAPP_VM_STATES = ['present', 'absent']
VM_STATUSES = {'3': 'SUSPENDED', '4': 'POWERED_ON', '8': 'POWERED_OFF'}
VAPP_SHARED_ACCESS = ['ReadOnly', 'Change', 'FullControl']
VAPP_METADATA_DOMAINS = ['GENERAL', 'SYSTEM']
VAPP_METADATA_VISIBILITY = ['PRIVATE', 'READONLY', 'READWRITE']
VAPP_SET_METADATA_VALUE_TYPE = ['String', 'Number', 'Boolean', 'DateTime']
VAPP_OPERATIONS = ['poweron', 'poweroff', 'list_vms', 'list_networks',
                   'share', 'unshare', 'set_meta', 'get_meta', 'remove_meta',
                   'add_org_network', 'delete_org_network']


def vapp_argument_spec():
    return dict(
        vapp_name=dict(type='str', required=True),
        template_name=dict(type='str', required=False),
        catalog_name=dict(type='str', required=False),
        vdc=dict(type='str', required=True),
        description=dict(type='str', required=False, default=None),
        network=dict(type='str', required=False, default=None),
        ip_allocation_mode=dict(type='str', required=False, default="dhcp"),
        deploy=dict(type='bool', required=False, default=True),
        power_on=dict(type='bool', required=False, default=True),
        accept_all_eulas=dict(type='bool', required=False, default=False),
        memory=dict(type='int', required=False, default=None),
        cpu=dict(type='int', required=False, default=None),
        disk_size=dict(type='int', required=False, default=None),
        vmpassword=dict(type='str', required=False, default=None),
        cust_script=dict(type='str', required=False, default=None),
        vm_name=dict(type='str', required=False, default=None),
        hostname=dict(type='str', required=False, default=None),
        ip_address=dict(type='str', required=False, default=None),
        storage_profile=dict(type='str', required=False, default=None),
        network_adapter_type=dict(type='str', required=False, default=None),
        force=dict(type='bool', required=False, default=False),
        metadata=dict(type='dict', required=False, default=None),
        metadata_type=dict(type='str', required=False, default='String', choices=VAPP_SET_METADATA_VALUE_TYPE),
        metadata_visibility=dict(type='str', required=False, default='READWRITE', choices=VAPP_METADATA_VISIBILITY),
        metadata_domain=dict(type='str', required=False, default='GENERAL', choices=VAPP_METADATA_DOMAINS),
        fence_mode=dict(type='str', required=False, default=FenceMode.BRIDGED.value),
        shared_access=dict(type='str', required=False, choices=VAPP_SHARED_ACCESS, default="ReadOnly"),
        org_name=dict(type='str', required=False, default=None),
        state=dict(choices=VAPP_VM_STATES, required=False),
        operation=dict(choices=VAPP_OPERATIONS, required=False),
    )


class Vapp(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Vapp, self).__init__(**kwargs)
        self.org = self.get_org()
        vdc_resource = self.org.get_vdc(self.params.get('vdc'))
        self.vdc = VDC(self.client, href=vdc_resource.get('href'))

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.create()

        if state == "absent":
            return self.delete()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "poweron":
            return self.power_on()

        if operation == "poweroff":
            return self.power_off()

        if operation == "list_vms":
            return self.list_vms()

        if operation == "list_networks":
            return self.list_networks()

        if operation == "share":
            return self.share()

        if operation == "unshare":
            return self.unshare()

        if operation == "set_meta":
            return self.set_meta()

        if operation == "get_meta":
            return self.get_meta()

        if operation == "remove_meta":
            return self.remove_meta()

        if operation == "add_org_network":
            return self.add_org_network()

        if operation == "delete_org_network":
            return self.delete_org_network()

    def get_org(self):
        org_name = self.params.get('org_name')
        org_resource = self.client.get_org()
        if org_name:
            org_resource = self.client.get_org_by_name(org_name)

        return Org(self.client, resource=org_resource)

    def get_vapp(self):
        vapp_name = self.params.get('vapp_name')
        vapp_resource = self.vdc.get_vapp(vapp_name)

        return VApp(self.client, name=vapp_name, resource=vapp_resource)

    def instantiate(self):
        params = self.params
        vapp_name = params.get('vapp_name')
        catalog_name = params.get('catalog_name')
        template_name = params.get('template_name')
        description = params.get('description')
        network = params.get('network')
        fence_mode = params.get('fence_mode')
        ip_allocation_mode = params.get('ip_allocation_mode')
        deploy = params.get('deploy')
        power_on = params.get('power_on')
        accept_all_eulas = params.get('accept_all_eulas')
        memory = params.get('memory')
        cpu = params.get('cpu')
        disk_size = params.get('disk_size')
        vmpassword = params.get('vmpassword')
        cust_script = params.get('cust_script')
        vm_name = params.get('vm_name')
        hostname = params.get('hostname')
        ip_address = params.get('ip_address')
        storage_profile = params.get('storage_profile')
        network_adapter_type = params.get('network_adapter_type')
        response = dict()
        response['changed'] = False

        try:
            self.vdc.get_vapp(vapp_name)
        except EntityNotFoundException:
            create_vapp_task = self.vdc.instantiate_vapp(
                name=vapp_name,
                catalog=catalog_name,
                template=template_name,
                description=description,
                network=network,
                fence_mode=fence_mode,
                ip_allocation_mode=ip_allocation_mode,
                deploy=deploy,
                power_on=power_on,
                accept_all_eulas=accept_all_eulas,
                memory=memory,
                cpu=cpu,
                disk_size=disk_size,
                password=vmpassword,
                cust_script=cust_script,
                vm_name=vm_name,
                hostname=hostname,
                ip_address=ip_address,
                storage_profile=storage_profile,
                network_adapter_type=network_adapter_type)
            self.execute_task(create_vapp_task.Tasks.Task[0])
            msg = 'Vapp {} has been created'
            response['msg'] = msg.format(vapp_name)
            response['changed'] = True
        else:
            msg = "Vapp {} is already present"
            response['warnings'] = msg.format(vapp_name)

        return response

    def create(self):
        params = self.params
        catalog_name = params.get('catalog_name')

        # vapp initialization if catalog has been provided
        if catalog_name:
            return self.instantiate()

        vapp_name = params.get('vapp_name')
        description = params.get('description')
        network = params.get('network')
        fence_mode = params.get('fence_mode')
        accept_all_eulas = params.get('accept_all_eulas')
        response = dict()
        response['changed'] = False

        try:
            self.vdc.get_vapp(vapp_name)
        except EntityNotFoundException:
            create_vapp_task = self.vdc.create_vapp(
                name=vapp_name,
                description=description,
                network=network,
                fence_mode=fence_mode,
                accept_all_eulas=accept_all_eulas)
            self.execute_task(create_vapp_task.Tasks.Task[0])
            msg = 'Vapp {} has been created'
            response['msg'] = msg.format(vapp_name)
            response['changed'] = True
        else:
            msg = "Vapp {} is already present"
            response['warnings'] = msg.format(vapp_name)

        return response

    def delete(self):
        vapp_name = self.params.get('vapp_name')
        force = self.params.get('force')
        response = dict()
        response['changed'] = False

        try:
            self.vdc.get_vapp(vapp_name)
        except EntityNotFoundException:
            response['warnings'] = "Vapp {} is not present.".format(vapp_name)
        else:
            delete_vapp_task = self.vdc.delete_vapp(
                name=vapp_name, force=force)
            self.execute_task(delete_vapp_task)
            response['msg'] = 'Vapp {} has been deleted.'.format(vapp_name)
            response['changed'] = True

        return response

    def power_on(self):
        response = dict()
        response['changed'] = False
        vapp_name = self.params.get('vapp_name')

        try:
            vapp = self.get_vapp()
            deploy_vapp_task = vapp.deploy()
            self.execute_task(deploy_vapp_task)
            msg = 'Vapp {} has been powered on'
            response['msg'] = msg.format(vapp_name)
            response['changed'] = True
        except OperationNotSupportedException as ex:
            response['warnings'] = str(ex)
        except EntityNotFoundException as ex:
            response['warnings'] = str(ex)

        return response

    def power_off(self):
        response = dict()
        response['changed'] = False
        vapp_name = self.params.get('vapp_name')

        try:
            vapp = self.get_vapp()
            undeploy_vapp_task = vapp.undeploy(action="powerOff")
            self.execute_task(undeploy_vapp_task)
            response['msg'] = 'Vapp {} has been powered off'.format(vapp_name)
            response['changed'] = True
        except OperationNotSupportedException as ex:
            response['warnings'] = str(ex)
        except EntityNotFoundException as ex:
            response['warnings'] = str(ex)

        return response

    def list_vms(self):
        response = dict()
        response['msg'] = list()
        response['changed'] = False

        try:
            vapp = self.get_vapp()
            for vm in vapp.get_all_vms():
                try:
                    ip = vapp.get_primary_ip(vm.get('name'))
                except Exception:
                    ip = None
                finally:
                    response['msg'].append({
                        "name": vm.get('name'),
                        "status": VM_STATUSES[vm.get('status')],
                        "deployed": vm.get('deployed') == 'true',
                        "ip_address": ip
                    })
        except EntityNotFoundException as ex:
            response['warnings'] = str(ex)

        return response

    def list_networks(self):
        response = dict()
        response['changed'] = False

        try:
            vapp = self.get_vapp()
            networks = vapp.get_all_networks()
            response['msg'] = [
                network.get('{' + NSMAP['ovf'] + '}name') for network in networks
            ]
        except EntityNotFoundException as ex:
            response['warnings'] = str(ex)

        return response

    def share(self):
        response = dict()
        response['changed'] = False
        access = self.params.get("shared_access")

        try:
            vapp = self.get_vapp()
            vapp.share_with_org_members(everyone_access_level=access)
            msg = "Vapp is shared across org with {0} access"
            response['msg'] = msg.format(access)
            response['changed'] = True
        except EntityNotFoundException as ex:
            response['warnings'] = str(ex)

        return response

    def unshare(self):
        response = dict()
        response['changed'] = False

        try:
            vapp = self.get_vapp()
            vapp.unshare_from_org_members()
            response['msg'] = "Sharing has been stopped for Vapp"
            response['changed'] = True
        except EntityNotFoundException as ex:
            response['warnings'] = str(ex)

        return response

    def set_meta(self):
        response = dict()
        response['changed'] = False
        vapp_name = self.params.get('vapp_name')
        metadata = self.params.get('metadata')
        domain = self.params.get("metadata_domain")
        visibility = self.params.get("metadata_visibility")
        metadata_type = self.params.get("metadata_type")
        metadata_type = "Metadata{0}Value".format(metadata_type)

        try:
            vapp = self.get_vapp()
            domain = MetadataDomain(domain)
            visibility = MetadataVisibility(visibility)
            metadata_type = MetadataValueType(metadata_type)
            set_meta_task = vapp.set_multiple_metadata(metadata,
                                                       domain=domain,
                                                       visibility=visibility,
                                                       metadata_value_type=metadata_type)
            self.execute_task(set_meta_task)
            msg = "Metadata {0} have been set to vApp {1}"
            response["msg"] = msg.format(list(metadata.keys()), vapp_name)
        except EntityNotFoundException as ex:
            response['warnings'] = str(ex)

        return response

    def get_meta(self):
        response = dict()
        response['changed'] = False
        response['msg'] = dict()

        try:
            vapp = self.get_vapp()
            metadata = vapp.get_metadata()
            response['msg'] = {
                 metadata.MetadataEntry.Key.text: metadata.MetadataEntry.TypedValue.Value.text
            }
        except EntityNotFoundException as ex:
            response['warnings'] = str(ex)

        return response

    def remove_meta(self):
        response = dict()
        response['changed'] = False
        vapp_name = self.params.get('vapp_name')
        domain = self.params.get("metadata_domain")
        metadata = self.params.get('metadata')
        domain = MetadataDomain(domain)
        response['msg'] = list()

        try:
            vapp = self.get_vapp()
            for key in metadata:
                remove_meta_task = vapp.remove_metadata(key, domain=domain)
                self.execute_task(remove_meta_task)
            msg = "Metadata {0} have been removed from vApp {1}"
            response["msg"] = msg.format(list(metadata.keys()), vapp_name)
        except EntityNotFoundException as ex:
            response['warnings'] = str(ex)

        return response

    def add_org_network(self):
        response = dict()
        response['changed'] = False
        vapp_name = self.params.get('vapp_name')
        network = self.params.get("network")

        try:
            vapp = self.get_vapp()
            vapp.connect_org_vdc_network(network)
            response['changed'] = True
            msg = "Org Network {0} has been added to vApp {1}"
            response['msg'] = msg.format(network, vapp_name)
        except EntityNotFoundException as ex:
            response['warnings'] = str(ex)
        except InvalidStateException as ex:
            response['warnings'] = str(ex)

        return response

    def delete_org_network(self):
        response = dict()
        response['changed'] = False
        vapp_name = self.params.get('vapp_name')
        network = self.params.get("network")

        try:
            vapp = self.get_vapp()
            vapp.disconnect_org_vdc_network(network)
            response['changed'] = True
            msg = "Org Network {0} has been added to vApp {1}"
            response['msg'] = msg.format(network, vapp_name)
        except EntityNotFoundException as ex:
            response['warnings'] = str(ex)
        except InvalidStateException as ex:
            response['warnings'] = str(ex)

        return response


def main():
    argument_spec = vapp_argument_spec()
    response = dict(msg=dict(type='str'))
    module = Vapp(argument_spec=argument_spec, supports_check_mode=True)

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
            raise Exception('Please provide state/operation for resource')

    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
