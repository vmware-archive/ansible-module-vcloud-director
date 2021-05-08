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
module: vcd_org_vdc
short_description: Manage ORG VDC's states/operations in vCloud Director
version_added: "2.4"
description:
    - Manage ORG VDC's states/operations in vCloud Director

options:
    user:
        description:
            - vCloud Director user name
        type: str
    password:
        description:
            - vCloud Director user password
        type: str
    host:
        description:
            - vCloud Director host address
        type: str
    org:
        description:
            - Organization name on vCloud Director to access
        type: str
    api_version:
        description:
            - Pyvcloud API version, required as float i.e 31 => 31.0
        type: float
    verify_ssl_certs:
        description:
            - whether to use secure connection to vCloud Director host
        type: bool
    vdc_name:
        description:
            - The name of the vdc
        type: str
    vdc_org_name:
        description:
            - name of the vdc organization
        type: str
    provider_vdc_name:
        description:
            - The name of an existing provider vdc
        type: str
    description:
        description:
            - The description of the org vdc
        type: str
    allocation_model:
        description:
            - The allocation model used by this vDC.
        type: str
        choices: ['AllocationVApp', 'AllocationPool', 'ReservationPool']
    cpu_units:
        description:
            - The cpu units compute capacity allocated to this vDC.
        type: str
    cpu_allocated:
        description:
            - Capacity that is committed to be available
        type: int
    cpu_limit:
        description:
            - Capacity limit relative to the value specified for Allocation
        type: int
    mem_units:
        description:
            - The memory units compute capacity allocated to this vDC.
        type: str
    mem_allocated:
        description:
            - Memory capacity that is committed to be available
        type: int
    mem_limit:
        description:
            - Memory capacity limit relative to the value specified for
              Allocation
        type: int
    nic_quota:
        description:
            - Maximum number of virtual NICs allowed in this vDC.
              Defaults to 0, which specifies an unlimited number
        type: int
        default: 0
    network_quota:
        description:
            - Maximum number of network objects that can be deployed in this
              vDC. Defaults to 0, which means no networks can be deployed
        type: int
        default: 0
    vm_quota:
        description:
            - The maximum number of VMs that can be created in this vDC.
              Defaults to 0, which specifies an unlimited number
        type: int
        default: 0
    storage_profiles:
        description:
            - List of provider VDC storage profiles to add to this VDC.
              Each item is a dictionary that requires the following elements.
        suboptions:
                name:
                    description:
                        - Name of the PVDC storage profile.
                    type: str
                    required: true
                enabled:
                    description:
                        - True if the storage profile is enabled for
                          this vDC else False.
                    type: bool
                    required: true
                units:
                    description:
                        - Units(MB) used to define limit.
                    type: str
                    required: true
                limit:
                    description:
                        - Max number of units allocated for this storage
                          profile.
                    type: int
                    required: true
                default:
                    description:
                        - True if this is default storage profile for this vDC.
                    type: bool
                    required: true
        type: list
    resource_guaranteed_memory:
        description:
            - Percentage of allocated memory resources guaranteed to vApps
              deployed in this VDC. Value defaults to 1.0 if the element is
              empty
        type: float
        default: 1.0
    resource_guaranteed_cpu:
        description:
            - Percentage of allocated CPU resources guaranteed to vApps
              deployed in this VDC. Value defaults to 1.0 if the element is
              empty
        type: float
        default: 1.0
    vcpu_in_mhz:
        description:
            - Specifies the clock frequency, in Megahertz, for any virtual CPU
              that is allocated to a VM
        type: int
    is_thin_provision:
        description:
            - request thin provisioning
        type: bool
    network_pool_name:
        description:
            - Reference to a network pool in the Provider VDC
        type: str
    uses_fast_provisioning:
        description:
            - request fast provisioning
        type: bool
    over_commit_allowed:
        description:
            - Set to "false" to disallow creation of the VDC if the
              AllocationModel is AllocationPool or ReservationPool and the
              ComputeCapacity you specified is greater than what the backing
              Provider VDC can supply. Defaults to "true" if empty or missing
        type: bool
        default: true
    vm_discovery_enabled:
        description:
            - True if discovery of vCenter VMs is enabled for resource pools
              backing this VDC else False
        type: bool
    is_enabled:
        description:
            - True if this VDC is enabled for use by the organization users
              else False
        type: bool
        default: true
    state:
        description:
            - state of new virtual datacenter ('present'/'absent'/'update').
            - One from state or operation has to be provided.
        type: str
        choices: ['present', 'absent', 'update']
    operation:
        description:
            - operation to be performed on org vdc
        type: str
        choices: ['add_storage_profile',
                  'update_storage_profile',
                  'delete_storage_profile',
                  'list_storage_profiles']

author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_org_vdc:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    org: Terraform
    api_version: 30.0
    verify_ssl_certs: False
    vdc_name: "VDC_NAME"
    provider_vdc_name: "PVDC_NAME"
    description: "DESCRIPTION"
    allocation_model: "AllocationVApp"
    storage_profiles:
      - name: "Profile 1"
        enabled: True
        units: "MB"
        limit: 50000
        default: True
      - name: "Profile 2"
        enabled: True
        units: "MB"
        limit: 50000
        default: False
    is_enabled: True
    state: "present"
'''

RETURN = '''
msg: success/failure message corresponding to vdc state/operation
changed: true if resource has been changed else false
'''


from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.system import System
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException
from pyvcloud.vcd.exceptions import OperationNotSupportedException


ORG_VDC_STATES = ['present', 'absent', 'update']
ORG_VDC_OPERATIONS = ['add_storage_profile',
                      'update_storage_profile',
                      'delete_storage_profile',
                      'list_storage_profiles']
ORG_VDC_ALLOCATION_MODELS = ['AllocationVApp',
                             'AllocationPool',
                             'ReservationPool']


def org_vdc_argument_spec():
    return dict(
        vdc_name=dict(type='str', required=False),
        vdc_org_name=dict(type='str', required=False),
        provider_vdc_name=dict(type='str', required=False),
        description=dict(type='str', required=False),
        allocation_model=dict(type='str', required=False,
                              choices=ORG_VDC_ALLOCATION_MODELS),
        cpu_units=dict(type='str', required=False),
        cpu_allocated=dict(type='int', required=False),
        cpu_limit=dict(type='int', required=False),
        mem_units=dict(type='str', required=False),
        mem_allocated=dict(type='int', required=False),
        mem_limit=dict(type='int', required=False),
        nic_quota=dict(type='int', required=False),
        network_quota=dict(type='int', required=False),
        vm_quota=dict(type='int', required=False),
        storage_profiles=dict(type='list', required=False, default=[]),
        resource_guaranteed_memory=dict(type='float', required=False),
        resource_guaranteed_cpu=dict(type='float', required=False),
        vcpu_in_mhz=dict(type='int', required=False),
        is_thin_provision=dict(type='bool', required=False),
        network_pool_name=dict(type='str', required=False),
        uses_fast_provisioning=dict(type='bool', required=False),
        over_commit_allowed=dict(type='bool', required=False),
        vm_discovery_enabled=dict(type='bool', required=False),
        is_enabled=dict(type='bool', required=False),
        state=dict(choices=ORG_VDC_STATES, required=False),
        operation=dict(choices=ORG_VDC_OPERATIONS, required=False),
    )


class Vdc(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Vdc, self).__init__(**kwargs)
        self.org = Org(self.client, resource=self.get_vdc_org_resource())

    def manage_states(self):
        state = self.params.get('state')
        if state == 'present':
            return self.create()

        if state == 'absent':
            return self.delete()

        if state == 'update':
            return self.update()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == 'add_storage_profile':
            return self.add_storage_profile()

        if operation == 'update_storage_profile':
            return self.update_storage_profile()

        if operation == 'delete_storage_profile':
            return self.delete_storage_profile()

        if operation == 'list_storage_profiles':
            return self.get_storage_profiles()

    def get_vdc_org_resource(self):
        if self.params.get('vdc_org_name'):
            return self.client.get_org_by_name(self.params.get('vdc_org_name'))

        return self.client.get_org()

    def get_vdc(self):
        try:
            vdc_name = self.params['vdc_name']
            vdc_resource = self.org.get_vdc(vdc_name)
            assert vdc_resource is not None
        except AssertionError:
            msg = "{0} is not found"
            raise EntityNotFoundException(msg.format(vdc_name))

        return VDC(self.client, name=vdc_name, resource=vdc_resource)

    def create(self):
        vdc_name = self.params['vdc_name']
        is_enabled = self.params['is_enabled']
        provider_vdc_name = self.params['provider_vdc_name']
        description = self.params['description'] or ''
        allocation_model = self.params['allocation_model'] or 'AllocationVApp'
        storage_profiles = self.params['storage_profiles']
        cpu_units = self.params['cpu_units'] or "MHz"
        cpu_allocated = self.params['cpu_allocated'] or 0
        cpu_limit = self.params['cpu_limit'] or 0
        mem_units = self.params['mem_units'] or 'MB'
        mem_allocated = self.params['mem_allocated'] or 0
        mem_limit = self.params['mem_limit'] or 0
        nic_quota = self.params['nic_quota'] or 0
        network_quota = self.params['network_quota'] or 0
        vm_quota = self.params['vm_quota'] or 0
        resource_guaranteed_memory = self.params['resource_guaranteed_memory'] or 1.0
        resource_guaranteed_cpu = self.params['resource_guaranteed_cpu'] or 1.0
        vcpu_in_mhz = self.params['vcpu_in_mhz']
        is_thin_provision = self.params['is_thin_provision']
        network_pool_name = self.params['network_pool_name']
        uses_fast_provisioning = self.params['uses_fast_provisioning']
        over_commit_allowed = self.params['over_commit_allowed']
        vm_discovery_enabled = self.params['vm_discovery_enabled']
        response = dict()
        response['changed'] = False
        response['msg'] = self.params["description"] or "None"

        try:
            self.get_vdc()
        except EntityNotFoundException:
            create_vdc_task = self.org.create_org_vdc(
                vdc_name=vdc_name,
                provider_vdc_name=provider_vdc_name,
                description=description,
                allocation_model=allocation_model,
                storage_profiles=storage_profiles,
                cpu_units=cpu_units,
                cpu_allocated=cpu_allocated,
                cpu_limit=cpu_limit,
                mem_units=mem_units,
                mem_allocated=mem_allocated,
                mem_limit=mem_limit,
                nic_quota=nic_quota,
                network_quota=network_quota,
                vm_quota=vm_quota,
                resource_guaranteed_memory=resource_guaranteed_memory,
                resource_guaranteed_cpu=resource_guaranteed_cpu,
                vcpu_in_mhz=vcpu_in_mhz,
                is_thin_provision=is_thin_provision,
                network_pool_name=network_pool_name,
                uses_fast_provisioning=uses_fast_provisioning,
                over_commit_allowed=over_commit_allowed,
                vm_discovery_enabled=vm_discovery_enabled,
                is_enabled=is_enabled)
            self.execute_task(create_vdc_task.Tasks.Task[0])
            response['msg'] = 'VDC {} has been created'.format(vdc_name)
            response['changed'] = True
        else:
            response['warnings'] = 'VDC {} is already present'.format(vdc_name)

        return response

    def update(self):
        vdc_name = self.params['vdc_name']
        description = self.params['description']
        allocation_model = self.params['allocation_model']
        cpu_units = self.params['cpu_units']
        cpu_allocated = self.params['cpu_allocated']
        cpu_limit = self.params['cpu_limit']
        mem_units = self.params['mem_units']
        mem_allocated = self.params['mem_allocated']
        mem_limit = self.params['mem_limit']
        nic_quota = self.params['nic_quota']
        network_quota = self.params['network_quota']
        vm_quota = self.params['vm_quota']
        resource_guaranteed_memory = self.params['resource_guaranteed_memory']
        resource_guaranteed_cpu = self.params['resource_guaranteed_cpu']
        vcpu_in_mhz = self.params['vcpu_in_mhz']
        is_thin_provision = self.params['is_thin_provision']
        is_enabled = self.params['is_enabled']
        response = dict()
        response['changed'] = False

        try:
            self.get_vdc()
            update_org_vdc_task = self.org.update_org_vdc(
                vdc_name,
                description,
                allocation_model,
                cpu_units,
                cpu_allocated,
                cpu_limit,
                mem_units,
                mem_allocated,
                mem_limit,
                nic_quota,
                network_quota,
                vm_quota,
                resource_guaranteed_memory,
                resource_guaranteed_cpu,
                vcpu_in_mhz,
                is_thin_provision,
                is_enabled)
            self.execute_task(update_org_vdc_task)
            response['msg'] = 'VDC {} has been updated'.format(vdc_name)
            response['changed'] = True
        except OperationNotSupportedException:
            msg = "VDC {} may already in desired state"
            response['warnings'] = msg.format(vdc_name)
        except EntityNotFoundException:
            response['warnings'] = 'VDC {} is not present.'.format(vdc_name)

        return response

    def delete(self):
        vdc_name = self.params['vdc_name']
        response = dict()
        response['changed'] = False

        try:
            vdc = self.get_vdc()
            vdc.enable_vdc(enable=False)
            delete_vdc_task = vdc.delete_vdc()
            self.execute_task(delete_vdc_task)
            response['msg'] = 'VDC {} has been deleted.'.format(vdc_name)
            response['changed'] = True
        except EntityNotFoundException:
            response['warnings'] = 'VDC {} is not present.'.format(vdc_name)
        except OperationNotSupportedException:
            pass

        return response

    def get_storage_profiles(self):
        vdc_name = self.params['vdc_name']
        response = dict()
        response['changed'] = False

        try:
            vdc = self.get_vdc()
            response['msg'] = [
                storage_profile.get("name")
                for storage_profile in vdc.get_storage_profiles()
            ]
        except EntityNotFoundException:
            msg = 'VDC {} is not present'
            response['warnings'] = msg.format(vdc_name)

        return response

    def _update_response(self, response, msg, warning):
        vdc_name = self.params['vdc_name']
        if response['msg']:
            response['msg'] = msg.format(response['msg'], vdc_name)

        if response['warnings']:
            response['warnings'] = warning.format(response['warnings'])

        return response

    def add_storage_profile(self):
        vdc_name = self.params['vdc_name']
        profiles = self.params['storage_profiles']
        response = dict()
        response['changed'] = False
        response['msg'] = list()
        response['warnings'] = list()
        storage_profiles = self.get_storage_profiles()['msg']
        msg = 'VDC Storage profile(s) {0} are added'
        warning = 'VDC Storage profile(s) {0} are already present'

        try:
            vdc = self.get_vdc()
            for profile in profiles:
                name = profile['name']
                if name not in storage_profiles:
                    enabled = profile['enabled']
                    default = profile['default']
                    kwargs = {
                        'enabled': True if enabled == 'true' else False,
                        'default': True if default == 'true' else False,
                        'limit_in_mb': profile['limit']
                    }
                    task = vdc.add_storage_profile(name, **kwargs)
                    self.execute_task(task)
                    response['msg'].append(profile['name'])
                    continue
                response['warnings'].append(name)
            response = self._update_response(response, msg, warning)
        except EntityNotFoundException:
            msg = 'VDC {} is not present'
            response['warnings'] = msg.format(vdc_name)

        return response

    def update_storage_profile(self):
        vdc_name = self.params['vdc_name']
        profiles = self.params['storage_profiles']
        response = dict()
        response['changed'] = False
        response['msg'] = list()
        response['warnings'] = list()
        storage_profiles = self.get_storage_profiles()['msg']
        msg = 'Storage profile(s) {0} are updated'
        warning = 'VDC Storage profile(s) {0} are not found'

        try:
            vdc = self.get_vdc()
            for profile in profiles:
                name = profile['name']
                if name in storage_profiles:
                    enabled = True if profile['enabled'] == 'true' else False
                    kwargs = {
                        'default': profile.get('default', None),
                        'limit_in_mb': profile.get('limit', None)
                    }
                    vdc.update_storage_profile(name, enabled, **kwargs)
                    response['msg'].append(name)
                    continue
                response['warnings'].append(name)
            response = self._update_response(response, msg, warning)
        except EntityNotFoundException:
            msg = 'VDC {} is not present'
            response['warnings'] = msg.format(vdc_name)

        return response

    def delete_storage_profile(self):
        vdc_name = self.params['vdc_name']
        profiles = self.params['storage_profiles']
        response = dict()
        response['msg'] = list()
        response['warnings'] = list()
        response['changed'] = False
        storage_profiles = self.get_storage_profiles()['msg']
        msg = 'Storage profile(s) {0} are deleted'
        warning = 'VDC Storage profile(s) {0} are not found'

        try:
            vdc = self.get_vdc()
            for profile in profiles:
                name = profile.get("name")
                if name in storage_profiles:
                    remove_vdc_task = vdc.remove_storage_profile(name)
                    self.execute_task(remove_vdc_task)
                    response['msg'].append(name)
                    continue
                response['warnings'].append(name)
            response = self._update_response(response, msg, warning)
        except EntityNotFoundException:
            msg = 'VDC {} is not present'
            response['warnings'] = msg.format(vdc_name)

        return response


def main():
    argument_spec = org_vdc_argument_spec()
    response = dict(msg=dict(type='str'))
    module = Vdc(argument_spec=argument_spec, supports_check_mode=True)

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
        response['msg'] = error.__str__()
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
