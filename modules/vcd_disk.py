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
client: catalog

short_description: Disk Module to manage disk operations through vCloud Director

version_added: "2.4"

description:
    - Disk Module to manage disk operations through vCloud Director

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
    disk_name:
        description:
            - Disk Name
        required: false
    size:
        description:
            - Disk Size in Bytes
        required: false
    vdc:
        description:
            - ORG VDC where disk needs to be created
        required: false
    description:
        description:
            - Disk Description
        required: false
    storage_profile:
        description:
            - Storage Profile for Disk
        required: false
    iops:
        description:
            - Iops for Disk
        required: false
    new_disk_name:
        description:
            - New Disk Name
        required: false
    new_size:
        description:
            - New Disk Size in MB
        required: false
    new_description:
        description:
            - New Disk Description
        required: false
    new_storage_profile:
        description:
            - New Storage Profile for Disk
        required: false
    new_iops:
        description:
            - New Iops for Disk
        required: false
    disk_id:
        description:
            - Disk ID
        required: false
    state:
        description:
            - state of disk ('present'/'absent').
            - One from state or operation has to be provided.
        required: false
    operation:
        description:
            - operation ('update') which should be performed over disk.
            - One from state or operation has to be provided.
        required: false

author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: create disk
  vcd_disk:
    disk_name: "DISK_NAME"
    size: "100"
    vdc: "OVD4"
    state: "present"
  register: output
'''

RETURN = '''
result: success/failure message relates to disk operation/operations
'''

from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from ansible.module_utils.vcd import VcdAnsibleModule


VCD_DISK_STATES = ['present', 'absent']
VCD_DISK_OPERATIONS = ['update']


def vcd_disk_argument_spec():
    return dict(
        disk_name=dict(type='str', required=False),
        size=dict(type='str', required=False),
        vdc=dict(type='str', required=False),
        description=dict(type='str', required=False),
        storage_profile=dict(type='str', required=False),
        iops=dict(type='str', required=False),
        new_disk_name=dict(type='str', required=False),
        new_size=dict(type='str', required=False),
        new_description=dict(type='str', required=False),
        new_storage_profile=dict(type='str', required=False),
        new_iops=dict(type='str', required=False),
        disk_id=dict(type='str', required=False),
        state=dict(choices=VCD_DISK_STATES, required=False),
        operation=dict(choices=VCD_DISK_OPERATIONS, required=False)
    )


class Disk(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Disk, self).__init__(**kwargs)

    def get_vdc_object(self, vdc):
        logged_in_org = self.client.get_org()
        org = Org(self.client, resource=logged_in_org)
        vdc = org.get_vdc(vdc)

        return VDC(self.client, href=vdc.get('href'))

    def create(self):
        disk_name = self.params.get('disk_name')
        vdc = self.params.get('vdc')
        size = self.params.get('size')
        description = self.params.get('description')
        storage_profile = self.params.get('storage_profile')
        disk_id = self.params.get('disk_id')
        response = dict()

        vdc_object = self.get_vdc_object(vdc)
        create_disk_task = vdc_object.create_disk(name=disk_name,
                                            size=size,
                                            storage_profile_name=storage_profile,
                                            description=description)
        self.execute_task(create_disk_task.Tasks.Task[0])
        response['msg'] = 'Disk {} has been created.'.format(disk_name)
        response['changed'] = True

        return response

    def update(self):
        disk_name = self.params.get('disk_name')
        vdc = self.params.get('vdc')
        disk_id = self.params.get('disk_id')
        new_disk_name = self.params.get('new_disk_name')
        new_size = self.params.get('new_size')
        new_description = self.params.get('new_description')
        new_storage_profile = self.params.get('new_storage_profile')
        new_iops = self.params.get('new_iops')
        response = dict()

        vdc_object = self.get_vdc_object(vdc)
        update_disk_task = vdc_object.update_disk(name=disk_name,
                                            disk_id=disk_id,
                                            new_name=new_disk_name,
                                            new_size=new_size,
                                            new_storage_profile_name=new_storage_profile,
                                            new_description=new_description,
                                            new_iops=new_iops)
        self.execute_task(update_disk_task)
        response['msg'] = 'Disk {} has been updated.'.format(disk_name)
        response['changed'] = True

        return response

    def delete(self):
        disk_name = self.params.get('disk_name')
        disk_id = self.params.get('disk_id')
        vdc = self.params.get('vdc')
        response = dict()

        vdc_object = self.get_vdc_object(vdc)
        delete_disk_task = vdc_object.delete_disk(disk_name, disk_id=disk_id)
        self.execute_task(delete_disk_task)
        response['msg'] = 'Disk {} has been deleted.'.format(disk_name)
        response['changed'] = True

        return response
        

    def manage_states(self):
        state = self.params.get('state')
        if state == 'present':
            return self.create()

        if state == 'absent':
            return self.delete()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == 'update':
            return self.update()


def main():
    argument_spec = vcd_disk_argument_spec()

    response = dict(
        msg=dict(type='str'),
    )

    module = Disk(argument_spec=argument_spec, supports_check_mode=True)
    try:
        if module.params.get('state'):
            response = module.manage_states()
        elif module.params.get('operation'):
            response = module.manage_operations()
        else:
            raise Exception('One of from state/operation should be provided.')
    except Exception as error:
        response['msg'] = error.__str__()
        response['changed'] = False
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
