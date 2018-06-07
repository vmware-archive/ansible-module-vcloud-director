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
short_description: Catalog_Item Module to manage catalog_item operations through vCloud Director
version_added: "2.4"
description:
    - This module is to [upload, read, delete] ova/media, capture vapp in vCloud Director.
    - Task performed:
        - Upload media 
        - Upload ova
        - Delete media
        - Delete ova
        - Capture vapp
        - Check media item resolved
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
    catalog_name:
        description:
            - name of the catalog
        required: true
    item_name:
        description:
            - name of the item
        required: false
    file_name:
        description:
            - name of the file 
        required: false
    vapp_name:
        description:
            - name of the vapp
        required: false
    vdc_name:
        description:
            - name of the vdc
        required: false  
    vdc_name:
        description:
            - name of the vdc
        required: false
    description:
        description:
            - description of vapp capture
        required: false
    customize_on_instantiate:
        description:
            - if you want to customise vapp on instantiation
        required: false
    state:
        description:
            - state of catalog_item ('present'/'absent').
            - used for
                - 'uploadova'           : upload ova file
                - 'deleteova'           : delete ova file
                - 'uploadmedia'         : upload media file
                - 'deletemedia'         : delete media file
            - One of operation/state has to be provided.
        required: false
    operation:
        description:
            - operation which should be performed over catalog.
            - various operations
                - 'capturevapp'         : capture vapp
                - 'ovacheckresolved'    : check if catalog item is resolved
            - One of operation/state has to be provided.
        required: false
author:
    - pcpandey@mail.com
'''

EXAMPLES = '''
- name: upload media
  vcd_catalog_item:
    catalog_name: "{{ catalog_name }}"
    item_name: "{{ item_name }}"
    file_name : "{{ file_name }}"
    operation: "uploadmedia"
  register: output   
'''

RETURN = '''
result: success/failure message relates to catalog operation/operations
'''

from pyvcloud.vcd.org import Org
from pyvcloud.vcd.client import Client
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.client import QueryResultFormat
import time

VCD_CATALOG_ITEM_STATES = ['present', 'absent']
VCD_CATALOG_ITEM_OPERATIONS = ['capturevapp', 'ovacheckresolved']

def vcd_catalog_item_argument_spec():
    return dict(
        catalog_name=dict(type='str', required=True),
        item_name=dict(type='str', required=False, default=''),
        file_name=dict(type='str', required=False, default=''),
        vapp_name=dict(type='str', required=False, default=''),
        vdc_name=dict(type='str', required=False, default=''),
        description=dict(type='str', required=False, default=''),
        customize_on_instantiate=dict(type='str', required=False, default=''),
        state=dict(choices=VCD_CATALOG_ITEM_STATES, required=False),
        operation=dict(choices=VCD_CATALOG_ITEM_OPERATIONS, required=False)
    )

class CatalogItem(object):
    
    def __init__(self, module):
        self.module = module

    def get_org_object(self):
        client = self.module.client
        logged_in_org = client.get_org()
        org = Org(client, resource=logged_in_org)

        return org

    def is_present(self):
        catalog_name = self.module.params.get('catalog_name')
        item_name = self. module.params.get('item_name')
        present = False

        org = self.get_org_object()
        try:
            catalog = org.get_catalog_item(catalog_name, item_name)
            present = True
        except Exception as e:
            pass

        return present

    def upload(self):
        catalog_name = self.module.params.get('catalog_name')
        item_name = self.module.params.get('item_name')
        file_name = self.module.params.get('file_name')
        item_details = {
            "catalog_name" : catalog_name,
            "item_name" : item_name,
            "file_name" : file_name
        }
        response = dict()

        if self.is_present():
            raise Exception("The catalog item you are trying to upload is already present.")
        org = self.get_org_object()
        if file_name.endswith(".ova"):
            org.upload_ovf(**item_details) 
        else:
            org.upload_media(**item_details) 
        response['msg'] = 'Catalog item {} is uploaded in catalog {}.'.format(item_name, catalog_name)
        response['changed'] = True

        return response

    def delete(self):
        catalog_name = self.module.params.get('catalog_name')
        item_name = self. module.params.get('item_name')
        response = dict()

        org = self.get_org_object()
        org.delete_catalog_item(name=catalog_name, item_name=item_name)
        response['msg'] = 'Catalog item {} is deleted from catalog {}.'.format(item_name, catalog_name)
        response['changed'] = True

        return response

    def capture_vapp(self):
        vapp_name = self.module.params.get('vapp_name')
        vdc_name = self.module.params.get('vdc_name')
        catalog_name = self.module.params.get('catalog_name')
        item_name = self.module.params.get('item_name')
        desc = self.module.params.get('description')
        customize_on_instantiate = self.module.params.get('customize_on_instantiate')
        client = self.module.client
        response = dict()

        org = self.get_org_object()
        v = org.get_vdc(vdc_name)
        vdc = VDC(client, href=v.get('href'))
        vapp = vdc.get_vapp(vapp_name)   
        catalog = org.get_catalog(catalog_name)
        org.capture_vapp(
            catalog_resource = catalog,
            vapp_href = vapp.get('href'),
            catalog_item_name = item_name,
            description = desc,
            customize_on_instantiate=customize_on_instantiate)
        response['msg'] = 'Vapp {} captured successfully for catalog_name {}, item_name {}.'.format(vapp_name, catalog_name, item_name)
        response['changed'] = True    

        return response

    def check_resolved(self, source_ova_item, catalog_name, item_name):
        client = self.module.client
        item_id = source_ova_item.get('id')
        # max_try = 20
        # attempt = 0
       
        while True:
            q = client.get_typed_query(
                'catalogItem',
                query_result_format = QueryResultFormat.ID_RECORDS,
                qfilter = 'id==%s' % item_id
                )
            records = list(q.execute())
            if records[0].get('status') == 'RESOLVED':
                break
            # elif attempt >= max_try:
            #     err_msg = "catalog_item {} not resolved for catalog {}, exceeded max_try limit={}.".format(item_name, catalog_name, max_try)
            #     raise Exception(err_msg)
            else:
                time.sleep(5)
                #attempt = attempt + 1
                #TODO might have to check when status goes to other state than resolved

    def ova_check_resolved(self):
        catalog_name = self.module.params.get('catalog_name')
        item_name = self.module.params.get('item_name')
        response = dict()

        org = self.get_org_object()
        source_ova_item = org.get_catalog_item(catalog_name, item_name)
        self.check_resolved(source_ova_item, catalog_name, item_name)
        response['msg'] = 'successfully uploaded/captured ova/media for catalog_name {}, item_name {}.'.format(catalog_name, item_name)
        response['changed'] = True 

        return response

def manage_states(catalog_item):
    params = catalog_item.module.params
    file_name = params.get('file_name')
    state = params.get('state')
    
    if state == "present":
        return catalog_item.upload()

    if state == "absent":
        return catalog_item.delete()

def manage_operations(catalog_item):
    operation = catalog_item.module.params.get('operation')
    
    if operation == "capturevapp":   
        return catalog_item.capture_vapp()

    if operation == "ovacheckresolved":   
        return catalog_item.ova_check_resolved()

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
            raise Exception('One of state/operation should be provided.')
    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)

if __name__ == '__main__':
    main()
