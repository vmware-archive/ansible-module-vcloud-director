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
module: vcd_disk
short_description: Manage disk's states/operations in vCloud Director
version_added: "2.4"
description:
    - Manage disk's states/operations in vCloud Director

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
    disk_name:
        description:
            - Disk Name
        required: true
    size:
        description:
            - Disk Size in Bytes
        required: false
    vdc:
        description:
            - ORG VDC where disk needs to be created
        required: true
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
    bus_type:
        description:
            - bus type for Disk
        required: false
    bus_sub_type:
        description:
            - bus sub type for Disk
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
            - state of disk ('present'/'absent'/'update').
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
msg: success/failure message corresponding to disk state/operation
changed: true if resource has been changed else false
'''

from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException


VCD_DISK_STATES = ['present', 'update', 'absent']


def vcd_disk_argument_spec():
    return dict(
        disk_name=dict(type='str', required=True),
        size=dict(type='int', required=False),
        vdc=dict(type='str', required=True),
        description=dict(type='str', required=False),
        storage_profile=dict(type='str', required=False, default=None),
        iops=dict(type='int', required=False, default=None),
        bus_type=dict(type='str', required=False, default=None),
        bus_sub_type=dict(type='str', required=False, default=None),
        new_disk_name=dict(type='str', required=False, default=None),
        new_size=dict(type='int', required=False, default=None),
        new_description=dict(type='str', required=False, default=None),
        new_storage_profile=dict(type='str', required=False, default=None),
        new_iops=dict(type='int', required=False, default=None),
        disk_id=dict(type='str', required=False),
        org_name=dict(type='str', required=False, default=None),
        state=dict(choices=VCD_DISK_STATES, required=False),
    )


class Disk(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Disk, self).__init__(**kwargs)
        self.org = self.get_org()
        vdc = self.org.get_vdc(self.params.get('vdc'))
        self.vdc = VDC(self.client, href=vdc.get('href'))

    def manage_states(self):
        state = self.params.get('state')
        if state == 'present':
            return self.create()

        if state == 'absent':
            return self.delete()

        if state == 'update':
            return self.update()

    def get_org(self):
        org_name = self.params.get('org_name')
        org_resource = self.client.get_org()
        if org_name:
            org_resource = self.client.get_org_by_name(org_name)

        return Org(self.client, resource=org_resource)

    def create(self):
        disk_name = self.params.get('disk_name')
        disk_id = self.params.get('disk_id')
        size = self.params.get('size')
        description = self.params.get('description')
        storage_profile = self.params.get('storage_profile')
        bus_type = self.params.get('bus_type')
        bus_sub_type = self.params.get('bus_sub_type')
        iops = self.params.get('iops')
        response = dict()
        response['changed'] = False

        try:
            self.vdc.get_disk(name=disk_name, disk_id=disk_id)
        except EntityNotFoundException:
            create_disk_task = self.vdc.create_disk(
                name=disk_name, size=size, bus_type=bus_type,
                bus_sub_type=bus_sub_type, description=description,
                iops=iops, storage_profile_name=storage_profile)
            self.execute_task(create_disk_task.Tasks.Task[0])
            response['msg'] = 'Disk {} has been created.'.format(disk_name)
            response['changed'] = True
        else:
            msg = "Disk {} is already present."
            response['warnings'] = msg.format(disk_name)

        return response

    def update(self):
        disk_name = self.params.get('disk_name')
        disk_id = self.params.get('disk_id')
        new_disk_name = self.params.get('new_disk_name')
        new_size = self.params.get('new_size')
        new_description = self.params.get('new_description')
        new_storage_profile = self.params.get('new_storage_profile')
        new_iops = self.params.get('new_iops')
        response = dict()
        response['changed'] = False

        update_disk_task = self.vdc.update_disk(
            name=disk_name, disk_id=disk_id, new_name=new_disk_name,
            new_size=new_size, new_iops=new_iops,
            new_description=new_description,
            new_storage_profile_name=new_storage_profile)
        self.execute_task(update_disk_task)
        response['msg'] = 'Disk {} has been updated.'.format(disk_name)
        response['changed'] = True

        return response

    def delete(self):
        disk_name = self.params.get('disk_name')
        disk_id = self.params.get('disk_id')
        response = dict()
        response['changed'] = False

        try:
            self.vdc.get_disk(name=disk_name, disk_id=disk_id)
        except EntityNotFoundException:
            response['warnings'] = "Disk {} is not present.".format(disk_name)
        else:
            delete_disk_task = self.vdc.delete_disk(
                name=disk_name, disk_id=disk_id)
            self.execute_task(delete_disk_task)
            response['msg'] = 'Disk {} has been deleted.'.format(disk_name)
            response['changed'] = True

        return response


def main():
    argument_spec = vcd_disk_argument_spec()
    response = dict(msg=dict(type='str'))
    module = Disk(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.check_mode:
            response = dict()
            response['changed'] = False
            response['msg'] = "skipped, running in check mode"
            response['skipped'] = True
        elif module.params.get('state'):
            response = module.manage_states()
        else:
            raise Exception('Please provide the state for the resource')

    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
