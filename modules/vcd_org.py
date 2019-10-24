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
module: vcd_org
short_description: Ansible module to manage (create/update/delete) orgs in vCloud Director
version_added: "2.4"
description:
    - Ansible module to manage (create/update/delete) orgs in vCloud Director

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
            - name of the org
        required: true
    full_name:
        description:
            - full name of the org
        required: false
    is_enabled:
        description:
            - enable organization if True. The default value is False
        required: false
    force:
        description:
            - force delete org
        required: false
    recursive:
        description:
            - recursive delete org
        required: false
    metadata:
        description:
            - dict to set, delete or update metadata
            - Example:
              metadata:
                - state: 'present'                                             # optional, present (will also update value), absent, default: present
                  name: 'keyX'                                                 # mandatory, unique name of metadata-entry
                  value: 'valueY'                                              # mandatory, if state present, else optional as it will be ignored
                  type: 'STRING'                                               # optional, STRING, NUMBER, BOOLEAN, DATA_TIME, default: STRING
                  visibility: 'READONLY'                                       # optional, PRIVATE, READONLY, READ_WRITE, default: READONLY
        required: false
    state:
        description:
            - state of org
                - present
                - absent
                - update
            - One from state or operation has to be provided.
        required: false
    operation:
        description:
            - operation which should be performed over org
                - read : read org metadata
            - One from state or operation has to be provided.
        required: false
author:
    - pcpandey@mail.com
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_org:
    user: terraform
    password: abcd
    host: csa.sandbox.org
    api_version: 30
    verify_ssl_certs: False
    org_name = "vcdvapp"
    full_name = "vcdlab"
    is_enabled = True
    state="present"
'''

RETURN = '''
msg: success/failure message corresponding to org state/operation
changed: true if resource has been changed else false
'''


from lxml import etree
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.system import System
from pyvcloud.vcd.client import E, EntityType, RelationType, ResourceType, MetadataDomain, MetadataVisibility, MetadataValueType
from pyvcloud.vcd.utils import to_dict
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException, BadRequestException

VCD_ORG_STATES = ['present', 'absent', 'update']
VCD_ORG_OPERATIONS = ['read','list_users','list_vdcs','set_metadata']


def org_argument_spec():
    return dict(
        org_name=dict(type='str', required=True),
        full_name=dict(type='str', required=False),
        is_enabled=dict(type='bool', required=False, default=False),
        force=dict(type='bool', required=False, default=None),
        recursive=dict(type='bool', required=False, default=None),
        metadata=dict(type='list', required=False, default='[]'),
        state=dict(choices=VCD_ORG_STATES, required=False),
        operation=dict(choices=VCD_ORG_OPERATIONS, required=False),
    )


class VCDOrg(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(VCDOrg, self).__init__(**kwargs)
        sys_admin = self.client.get_admin()
        self.system = System(self.client, admin_resource=sys_admin)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.create()

        if state == "absent":
            return self.delete()

        if state == "update":
            return self.update()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "read":
            return self.read()
        if operation == "list_users":
            return self.list_users()
        if operation == "list_vdcs":
            return self.list_vdcs()
        if operation == "set_metadata":
            return self.set_metadata()

    def create(self):
        org_name = self.params.get('org_name')
        full_name = self.params.get('full_name')
        is_enabled = self.params.get('is_enabled')
        metadata = self.params.get('metadata')
        response = dict()
        response['changed'] = False

        try:
            self.system.create_org(org_name, full_name, is_enabled)
            response['msg'] = 'Org {} has been created.'.format(org_name)
            response['changed'] = True
        except BadRequestException:
            response['warnings'] = 'Org {} is already present.'.format(org_name)

        return response

    def read(self):
        org_name = self.params.get('org_name')
        response = dict()
        org_details = dict()
        response['changed'] = False

        resource = self.client.get_org_by_name(org_name)
        org = Org(self.client, resource=resource)
        org_admin_resource = org.client.get_resource(org.href_admin)
        org_details['org_name'] = org_name
        org_details['full_name'] = str(org_admin_resource['FullName'])
        org_details['is_enabled'] = str(org_admin_resource['IsEnabled'])
        response['msg'] = org_details

        return response

    def update(self):
        org_name = self.params.get('org_name')
        is_enabled = self.params.get('is_enabled')
        response = dict()
        response['changed'] = False

        resource = self.client.get_org_by_name(org_name)
        org = Org(self.client, resource=resource)
        org.update_org(is_enabled)
        response['msg'] = "Org {} has been updated.".format(org_name)
        response['changed'] = True

        return response

    def delete(self):
        org_name = self.params.get('org_name')
        force = self.params.get('force')
        recursive = self.params.get('recursive')
        response = dict()
        response['changed'] = False

        try:
            delete_org_task = self.system.delete_org(org_name, force, recursive)
            self.execute_task(delete_org_task)
            response['msg'] = "Org {} has been deleted.".format(org_name)
            response['changed'] = True
        except EntityNotFoundException:
            response['warnings'] = "Org {} is not present.".format(org_name)

        return response

    def list_users(self):
        org_name = self.params.get('org_name')
        response = dict()
        org_details = dict()
        response['users'] = list()
        response['changed'] = False

        resource = self.client.get_org_by_name(org_name)
        org = Org(self.client, resource=resource)
        org_user_list = org.list_users()
        resource_type = ResourceType.USER.value
        if self.client.is_sysadmin():
            resource_type = ResourceType.ADMIN_USER.value
        for org_user in org_user_list:
            response['users'].append(
                to_dict(org_user, resource_type=resource_type, exclude=[]))

        return response
    
    def list_vdcs(self):
        org_name = self.params.get('org_name')
        response = dict()
        org_details = dict()
        response['vdcs'] = list()
        response['changed'] = False

        resource = self.client.get_org_by_name(org_name)
        org = Org(self.client, resource=resource)
        response['vdcs'] = org.list_vdcs()

        return response
    
    def set_metadata(self):
        '''
        Expects metadata as following:
        metadata:
          - state: 'present'                                             # optional, present (will also update value), absent, default: present
            name: 'keyX'                                                 # mandatory, unique name of metadata-entry
            value: 'valueY'                                              # mandatory, if state present, else optional as it will be ignored
            type: 'STRING'                                               # optional, STRING, NUMBER, BOOLEAN, DATA_TIME, default: STRING
            visibility: 'READONLY'                                       # optional, PRIVATE, READONLY, READ_WRITE, default: READONLY
        '''
        org_name = self.params.get('org_name')
        metadata = self.params.get('metadata')
        response = dict()
        response['msg'] = ''
        
        if len(metadata) != 0:
            # workaround to set metadata for org as it is as of now not implemented in pyvcloud for org, vdc, e.g. - we will open a pull request to fix this in the future
            resource = self.client.get_linked_resource(self.client.get_org_by_name(org_name), RelationType.DOWN, EntityType.METADATA.value)
            self.metadata = Metadata(self.client, resource=resource)
            for md in metadata:
                domain = MetadataDomain.SYSTEM
                visibility = MetadataVisibility.READONLY
                if type(md) is dict and md.get('state', 'present') == 'absent':
                    if md.get('visibility', 'READONLY').upper() == 'READWRITE':
                        domain = MetadataDomain.GENERAL
                    self.metadata.remove_metadata()
                else:
                    if md.get('visibility', 'READONLY').upper() == 'PRIVATE':
                        visibility = MetadataVisibility.PRIVATE
                    elif md.get('visibility', 'READONLY').upper() == 'READWRITE':
                        domain = MetadataDomain.GENERAL
                        visibility = MetadataVisibility.READWRITE
                    value_type = MetadataValueType.STRING
                    if md.get('type', 'STRING').upper() == 'NUMBER':
                        value_type = MetadataValueType.NUMBER
                    elif md.get('type', 'STRING').upper() == 'BOOLEAN':
                        value_type = MetadataValueType.BOOLEAN
                    elif md.get('type', 'STRING').upper() == 'DATA_TIME':
                        value_type = MetadataValueType.DATA_TIME
                    self.metadata.set_metadata(md['name'], md['value'], domain, visibility, value_type, True)
        
        return response

def main():
    argument_spec = org_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = VCDOrg(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.params.get('state'):
            response = module.manage_states()
        elif module.params.get('operation'):
            response = module.manage_operations()
        else:
            raise Exception('One of from state/operation should be provided.')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
