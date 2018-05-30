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
client: catalog_item
short_description: catalog_item module for performing CRUD operation in vCloud Director
version_added: "2.4"
description:
    - This module is to create, read, update, delete catalog_items in vCloud Director.
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


def vcd_catalog_item_argument_spec():
    return dict(
        name=dict(type='str', required=True),
        new_name=dict(type='str', required=False, default=''),
        description=dict(type='str', required=False, default=''),
        shared=dict(type='bool', required=False, default=False),
        state=dict(choices=VCD_CATALOG_STATES, required=False),
        operation=dict(choices=VCD_CATALOG_OPERATIONS, required=False)
    )

class CatalogItem(object):
    
    def __init__(self, module):
        self.module = module

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass         

def manage_states(catalog_item):
    state = catalog_item.module.params.get('state')
    
    if state == "present":
        return catalog_item.create()
    elif state == "absent":
        return catalog_item.delete()

def manage_operations(catalog_item):
    operation = catalog_item.module.params.get('operation')

    if (operation == "updatenameanddescription"):
        return catalog_item.update_name_and_description()
   
    if operation == "sharecatalogstate":
        return catalog_item.share()
        
    if operation == "readcatalog":   
        return catalog_item.read()  

def main():
    argument_spec = vcd_catalog_item_argument_spec()
    
    response = dict(
        msg=dict(type='str'),
        changed=False,
    )

    module = VcdAnsibleModule(argument_spec=argument_spec,
                              supports_check_mode=True)
    
    try:
        catalog_item = CatalogItem(module)
        if module.params.get('state'):
            response = manage_states(catalog_item)
        elif module.params.get('operation'):
            response = manage_operations(catalog_item)
        else:
            raise Exception('One of from state/operation should be provided.')
    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)

if __name__ == '__main__':
    main()
