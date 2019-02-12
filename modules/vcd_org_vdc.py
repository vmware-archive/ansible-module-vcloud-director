# Copyright © 2018 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause

# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: vcd_org_vdc
short_description: Ansible module to manage (create/update/delete) virtual
                   datacenters in vCloud Director.
version_added: "2.4"
description:
    - "Ansible module to manage (create/update/delete) virtual datacenters in
       vCloud Director."

options:
    user:
        description:
            - vCloud Director user name
        required: false
        type: str
    password:
        description:
            - vCloud Director user password
        required: false
        type: str
    host:
        description:
            - vCloud Director host address
        required: false
        type: str
    org:
        description:
            - Organization name on vCloud Director to access
        required: false
        type: str
    api_version:
        description:
            - Pyvcloud API version, required as float i.e 31 => 31.0
        required: false
        type: float
    verify_ssl_certs:
        description:
            - whether to use secure connection to vCloud Director host
        type: bool
    vdc_name:
        description:
            - The name of the new vdc
        required: true
        type: str
    provider_vdc_name:
        description:
            - The name of an existing provider vdc
        required: false
        type: str
    description:
        description:
            - The description of the new org vdc
        required: false
        type: str
    allocation_model:
        description:
            - The allocation model used by this vDC.
        required: false
        type: str
        choices: ['AllocationVApp', 'AllocationPool', 'ReservationPool']
    cpu_units:
        description:
            - The cpu units compute capacity allocated to this vDC.
        required: false
        default: "MHz"
        type: str
    cpu_allocated:
        description:
            - Capacity that is committed to be available
        required: false
        type: int
        default: 0
    cpu_limit:
        description:
            - Capacity limit relative to the value specified for Allocation
        required: false
        type: int
        default: 0
    mem_units:
        description:
            - The memory units compute capacity allocated to this vDC.
        required: false
        default: "MB"
        type: str
    mem_allocated:
        description:
            - Memory capacity that is committed to be available
        required: false
        type: int
        default: 0
    mem_limit:
        description:
            - Memory capacity limit relative to the value specified for
              Allocation
        required: false
        type: int
        default: 0
    nic_quota:
        description:
            - Maximum number of virtual NICs allowed in this vDC.
              Defaults to 0, which specifies an unlimited number
        required: false
        type: int
        default: 0
    network_quota:
        description:
            - Maximum number of network objects that can be deployed in this
              vDC. Defaults to 0, which means no networks can be deployed
        required: false
        type: int
        default: 0
    vm_quota:
        description:
            - The maximum number of VMs that can be created in this vDC.
              Defaults to 0, which specifies an unlimited number
        required: false
        type: int
        default: 0
    storage_profiles:
        description:
            - List of provider vDC storage profiles to add to this vDC.
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
        required: false
        type: list
    resource_guaranteed_memory:
        description:
            - Percentage of allocated memory resources guaranteed to vApps
              deployed in this vDC. Value defaults to 1.0 if the element is
              empty
        required: false
        type: float
        default: 1.0
    resource_guaranteed_cpu:
        description:
            - Percentage of allocated CPU resources guaranteed to vApps
              deployed in this vDC. Value defaults to 1.0 if the element is
              empty
        required: false
        type: float
        default: 1.0
    vcpu_in_mhz:
        description:
            - Specifies the clock frequency, in Megahertz, for any virtual CPU
              that is allocated to a VM
        required: false
        type: int
    is_thin_provision:
        description:
            - request thin provisioning
        required: false
        type: bool
    network_pool_name:
        description:
            - Reference to a network pool in the Provider vDC
        required: false
        type: str
    uses_fast_provisioning:
        description:
            - request fast provisioning
        required: false
        type: bool
    over_commit_allowed:
        description:
            - Set to "false" to disallow creation of the VDC if the
              AllocationModel is AllocationPool or ReservationPool and the
              ComputeCapacity you specified is greater than what the backing
              Provider VDC can supply. Defaults to "true" if empty or missing
        required: false
        type: bool
        default: true
    vm_discovery_enabled:
        description:
            - True if discovery of vCenter VMs is enabled for resource pools
              backing this vDC else False
        required: false
        type: bool
    is_enabled:
        description:
            - True if this vDC is enabled for use by the organization users
              else False
        required: false
        type: bool
        default: true
    state:
        description:
            - state of new virtual datacenter ('present'/'absent').
            - One from state or operation has to be provided.
        required: false
        type: str
        choices: ['present', 'absent', 'update']
        default: 'present'
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
from pyvcloud.vcd.exceptions import EntityNotFoundException
from ansible.module_utils.vcd import VcdAnsibleModule


ORG_VDC_STATES = ['present', 'absent', 'update']


def org_vdc_argument_spec():
    return dict(
        vdc_name=dict(type='str', required=True),
        provider_vdc_name=dict(type='str', required=False),
        description=dict(type='str', required=False, default=''),
        allocation_model=dict(type='str', required=False,
                              default='AllocationVApp',
                              choices=['AllocationVApp', 'AllocationPool',
                                       'ReservationPool']),
        cpu_units=dict(type='str', required=False, default='MHz'),
        cpu_allocated=dict(type='int', required=False, default=0),
        cpu_limit=dict(type='int', required=False, default=0),
        mem_units=dict(type='str', required=False, default='MB'),
        mem_allocated=dict(type='int', required=False, default=0),
        mem_limit=dict(type='int', required=False, default=0),
        nic_quota=dict(type='int', required=False, default=0),
        network_quota=dict(type='int', required=False, default=0),
        vm_quota=dict(type='int', required=False, default=0),
        storage_profiles=dict(type='list', required=False, default='[]'),
        resource_guaranteed_memory=dict(type='float', required=False,
                                        default=1.0),
        resource_guaranteed_cpu=dict(type='float', required=False,
                                     default=1.0),
        vcpu_in_mhz=dict(type='int', required=False, default=None),
        is_thin_provision=dict(type='bool', required=False, default=None),
        network_pool_name=dict(type='str', required=False, default=None),
        uses_fast_provisioning=dict(type='bool', required=False, default=None),
        over_commit_allowed=dict(type='bool', required=False, default=True),
        vm_discovery_enabled=dict(type='bool', required=False, default=None),
        is_enabled=dict(type='bool', required=False, default=True),
        state=dict(choices=ORG_VDC_STATES, required=False, default='present'),
    )


class Vdc(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Vdc, self).__init__(**kwargs)
        logged_in_org = self.client.get_org()
        self.org = Org(self.client, resource=logged_in_org)

    def manage_states(self):
        state = self.params.get('state')
        if state == 'present':
            return self.create()

        if state == 'absent':
            return self.delete()

        if state == 'update':
            return self.update()

    def create(self):
        vdc_name = self.params.get('vdc_name')
        is_enabled = self.params.get('is_enabled')
        provider_vdc_name = self.params.get('provider_vdc_name')
        description = self.params.get('description')
        allocation_model = self.params.get('allocation_model')
        storage_profiles = self.params.get('storage_profiles')
        cpu_units = self.params.get('cpu_units')
        cpu_allocated = self.params.get('cpu_allocated')
        cpu_limit = self.params.get('cpu_limit')
        mem_units = self.params.get('mem_units')
        mem_allocated = self.params.get('mem_allocated')
        mem_limit = self.params.get('mem_limit')
        nic_quota = self.params.get('nic_quota')
        network_quota = self.params.get('network_quota')
        vm_quota = self.params.get('vm_quota')
        resource_guaranteed_memory = self.params.get('resource_guaranteed_memory')
        resource_guaranteed_cpu = self.params.get('resource_guaranteed_cpu')
        vcpu_in_mhz = self.params.get('vcpu_in_mhz')
        is_thin_provision = self.params.get('is_thin_provision')
        network_pool_name = self.params.get('network_pool_name')
        uses_fast_provisioning = self.params.get('uses_fast_provisioning')
        over_commit_allowed = self.params.get('over_commit_allowed')
        vm_discovery_enabled = self.params.get('vm_discovery_enabled')
        response = dict()
        response['changed'] = False

        try:
            self.org.get_vdc(vdc_name)
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
            response['msg'] = 'VDC {} has been created.'.format(vdc_name)
            response['changed'] = True
        else:
            response['warnings'] = 'VDC {} is already present.'.format(vdc_name)

        return response

    def update(self):
        vdc_name = self.params.get('vdc_name')
        is_enabled = self.params.get('is_enabled')
        response = dict()
        response['changed'] = False

        vdc_resource = self.org.get_vdc(vdc_name)
        vdc = VDC(self.client, name=vdc_name, resource=vdc_resource)
        vdc.enable_vdc(enable=is_enabled)
        response['msg'] = 'VDC {} has been updated.'.format(vdc_name)
        response['changed'] = True

        return response

    def delete(self):
        vdc_name = self.params.get('vdc_name')
        response = dict()
        response['changed'] = False

        try:
            vdc_resource = self.org.get_vdc(vdc_name)
        except EntityNotFoundException:
            response['warnings'] = 'VDC {} is not present.'.format(vdc_name)
        else:
            vdc = VDC(self.client, name=vdc_name, resource=vdc_resource)
            vdc.enable_vdc(enable=False)
            delete_vdc_task = vdc.delete_vdc()
            self.execute_task(delete_vdc_task)
            response['msg'] = 'VDC {} has been deleted.'.format(vdc_name)
            response['changed'] = True

        return response


def main():
    argument_spec = org_vdc_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = Vdc(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if not module.params.get('state'):
            raise Exception('Please provide state for the resource.')

        response = module.manage_states()
        module.exit_json(**response)

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)


if __name__ == '__main__':
    main()
