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

short_description: Catalog module for performing CRUD operation in vCloud Director

version_added: "2.4"

description:
    - This module is to create, read, update, delete catalog in vCloud Director.
    - Task performed:
        - Create catalog 
        - Read Catalog
        - Update name, description and shared state of catalog
        - Delete catalog

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
    name:
        description:
            - catalog name
        required: true
    new_name:
        description:
            - new catalog name. Used while updating catalog name.
        required: false
    description:
        description:
            - description of the catalog
        required: false
    vdc:
        description:
            - Org Vdc where this VAPP gets created
        required: true
    shared:
        description:
            - shared state of catalog(true/false)
        required: false  
    state:
        description:
            - state of catalog ('present'/'absent').
            - One from state or operation has to be provided. 
        required: false
    operation:
        description:
            - operation which should be performed over catalog.
            - various operations are: 
                - updatenameanddescription : update catalog_name and catalog_description
                - sharecatalogstate : share or unshare catalog
                - readcatalog : read catalog metadata e.g catalog name, description, shared state of catalog
            - One from state or operation has to be provided.
        required: false

author:
    - pcpandey@mail.com
'''

EXAMPLES = '''
- name: create catalog
  vcd_catalog:
    name: "{{ catalog_name }}"
    description: "{{ description }}"
    state: "present"
  register: output  
'''

RETURN = '''
result: success/failure message relates to catalog operation/operations
'''

from pyvcloud.vcd.org import Org
from pyvcloud.vcd.client import Client
from ansible.module_utils.basic import AnsibleModule
from pyvcloud.vcd.client import BasicLoginCredentials
from ansible.module_utils.vcd import VcdAnsibleModule


VCD_CATALOG_STATES = ['present', 'absent']
VCD_CATALOG_OPERATIONS = ['updatenameanddescription', 'sharecatalogstate', 'readcatalog']


def vcd_catalog_argument_spec():
    return dict(
        name=dict(type='str', required=True),
        new_name=dict(type='str', required=False, default=''),
        description=dict(type='str', required=False, default=''),
        shared=dict(type='bool', required=False, default=False),
        state=dict(choices=VCD_CATALOG_STATES, required=False),
        operation=dict(choices=VCD_CATALOG_OPERATIONS, required=False)
    )


class Catalog(object):
    def __init__(self, module):
        self.module = module

    def get_org_object(self):
        client = self.module.client
        logged_in_org = client.get_org()
        org = Org(client, resource=logged_in_org)
        return org        

    def create(self):
        name = self.module.params.get('name')
        description = self. module.params.get('description')

        response = dict()

        org = self.get_org_object()
        catalog = org.create_catalog(name=name, description=description)
        response['msg'] = 'Catalog {} has been created.'.format(name)
        response['changed'] = True

        return response

    def delete(self):
        name = self.module.params.get('name')

        response = dict()

        org = self.get_org_object()
        result = org.delete_catalog(name)
        response['msg'] = 'Catalog {} has been deleted.'.format(name)
        response['changed'] = True

        return response

        
    def update_name_and_description(self):
        name = self.module.params.get('name')
        new_name = self.module.params.get('new_name')
        description = self.module.params.get('description')

        response = dict()

        org = self.get_org_object()
        
        if not new_name:
            #if new_name is None or empty, set new name as old name i.e name
            new_name = name

        result = org.update_catalog(
                    old_catalog_name=name,
                    new_catalog_name=new_name,
                    description=description)
        response['msg'] = 'Catalog {} name or description has been updated.'.format(name)
        response['changed'] = True

        return response                    


    def share(self):
        name = self.module.params.get('name')
        shared = self.module.params.get('shared')

        response = dict()

        org = self.get_org_object()
        result = org.share_catalog(name=name, share=shared)

        response['msg'] = 'Catalog {} shared state has been updated to [shared={}].'.format(name, shared)
        response['changed'] = True

        return response


    def read(self):
        name = self.module.params.get('name')
        response = dict()
        
        org = self.get_org_object()
        catalog = org.get_catalog(name)

        result = dict()
        result['name'] = str(catalog.get("name"))
        result['description'] = str(catalog.Description)
        result['shared'] = str(catalog.IsPublished)
        response['msg'] = result
        response['changed'] = False

        return response


def manage_states(catalog):
    state = catalog.module.params.get('state')
    
    if state == "present":
        return catalog.create()
    elif state == "absent":
        return catalog.delete()

def manage_operations(catalog):
    operation = catalog.module.params.get('operation')

    if (operation == "updatenameanddescription"):
        return catalog.update_name_and_description()
   
    if operation == "sharecatalogstate":
        return catalog.share()
        
    if operation == "readcatalog":   
        return catalog.read()     


def main():
    argument_spec = vcd_catalog_argument_spec()
    
    response = dict(
        msg=dict(type='str'),
        changed=False,
    )

    module = VcdAnsibleModule(argument_spec=argument_spec,
                              supports_check_mode=True)
    try:
        catalog = Catalog(module)
        if module.params.get('state'):
            response = manage_states(catalog)
        elif module.params.get('operation'):
            response = manage_operations(catalog)
        else:
            raise Exception('One of from state/operation should be provided.')
    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
