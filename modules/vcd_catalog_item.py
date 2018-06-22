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
module: vcd_catalog_item
short_description: Ansible Module to manage (create/update/delete) catalog items in vCloud Director.
version_added: "2.4"
description:
    - Ansible Module to manage (create/update/delete) catalog items in vCloud Director.
    - Task performed:
        - Upload media
        - Upload ova
        - Delete media
        - Delete ova
        - Capture vapp
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
    chunk_size:
        description:
            - Size of chunks in which the file will be uploaded to the catalog
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
            - "true"/"false" if you want to customise vapp on instantiation
        required: false
    overwrite:
        description:
            - "true"/"false"
            - Flag indicates if the item in the catalog has to be overwritten if it already exists.
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
            - One of operation/state has to be provided.
        required: false
author:
    - pcpandey@mail.com
'''

EXAMPLES = '''
- name: upload media
  vcd_catalog_item:
    catalog_name: "test_catalog"
    item_name: "test_item"
    file_name : "test_item.ova"
    state: "present"
  register: output
'''

RETURN = '''
msg: success/failure message corresponding to catalog item state/operation
changed: true if resource has been changed else false
'''

import time
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.org import Org
from pyvcloud.vcd.client import Client
from pyvcloud.vcd.client import QueryResultFormat
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException


VCD_CATALOG_ITEM_STATES = ['present', 'absent']
VCD_CATALOG_ITEM_OPERATIONS = ['capturevapp']
DEFAULT_CHUNK_SIZE = 1024 * 1024


def vcd_catalog_item_argument_spec():
    return dict(
        catalog_name=dict(type='str', required=True),
        item_name=dict(type='str', required=False, default=None),
        file_name=dict(type='str', required=False),
        chunk_size=dict(type='int', required=False, default=DEFAULT_CHUNK_SIZE),
        vapp_name=dict(type='str', required=False),
        vdc_name=dict(type='str', required=False),
        description=dict(type='str', required=False, default=''),
        customize_on_instantiate=dict(type='bool', required=False, default=False),
        overwrite=dict(type='bool', required=False, default=False),
        state=dict(choices=VCD_CATALOG_ITEM_STATES, required=False),
        operation=dict(choices=VCD_CATALOG_ITEM_OPERATIONS, required=False)
    )


class CatalogItem(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(CatalogItem, self).__init__(**kwargs)
        logged_in_org = self.client.get_org()
        self.org = Org(self.client, resource=logged_in_org)

    def manage_states(self):
        state = self.params.get('state')
        if state == "present":
            return self.upload()

        if state == "absent":
            return self.delete()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == "capturevapp":
            return self.capture_vapp()

    def is_present(self):
        params = self.params
        catalog_name = params.get('catalog_name')
        item_name = params.get('item_name')

        try:
            self.org.get_catalog_item(catalog_name, item_name)
        except EntityNotFoundException:
            return False

        return True

    def upload(self):
        params = self.params
        catalog_name = params.get('catalog_name')
        item_name = params.get('item_name')
        file_name = params.get('file_name')
        chunk_size = params.get('chunk_size')
        response = dict()
        response['changed'] = False
        item_details = {
            "catalog_name": catalog_name,
            "item_name": item_name,
            "file_name": file_name,
            "chunk_size": chunk_size
        }

        if self.is_present():
            response['warnings'] = "Catalog Item {} is already present.".format(item_name)
            return response

        if file_name.endswith(".ova") or file_name.endswith(".ovf"):
            self.org.upload_ovf(**item_details)
            self.ova_check_resolved()

        if not file_name.endswith(".ova"):
            self.org.upload_media(**item_details)

        response['msg'] = "Catalog item {} is uploaded.".format(item_name)
        response['changed'] = True

        return response

    def delete(self):
        params = self.params
        catalog_name = params.get('catalog_name')
        item_name = params.get('item_name')
        response = dict()
        response['changed'] = False

        if not self.is_present():
            response['warnings'] = "Catalog Item {} is not present.".format(item_name)
            return response

        self.org.delete_catalog_item(name=catalog_name, item_name=item_name)
        response['msg'] = "Catalog Item {} has been deleted.".format(item_name)
        response['changed'] = True

        return response

    def capture_vapp(self):
        params = self.params
        vapp_name = params.get('vapp_name')
        vdc_name = params.get('vdc_name')
        catalog_name = params.get('catalog_name')
        item_name = params.get('item_name')
        desc = params.get('description')
        customize_on_instantiate = params.get('customize_on_instantiate')
        overwrite = params.get('overwrite')
        client = self.client
        response = dict()
        response['changed'] = False

        v = self.org.get_vdc(vdc_name)
        vdc = VDC(client, href=v.get('href'))
        vapp = vdc.get_vapp(vapp_name)
        catalog = self.org.get_catalog(catalog_name)
        self.org.capture_vapp(
            catalog_resource=catalog,
            vapp_href=vapp.get('href'),
            catalog_item_name=item_name,
            description=desc,
            customize_on_instantiate=customize_on_instantiate,
            overwrite=overwrite)
        self.ova_check_resolved()
        response['msg'] = "Catalog Item {} has been captured".format(item_name)
        response['changed'] = True

        return response

    def ova_check_resolved(self):
        params = self.params
        catalog_name = params.get('catalog_name')
        item_name = params.get('item_name')
        response = False

        source_ova_item = self.org.get_catalog_item(catalog_name, item_name)
        self.check_resolved(source_ova_item, catalog_name, item_name)
        response = True

        return response

    def check_resolved(self, source_ova_item, catalog_name, item_name):
        client = self.client
        item_id = source_ova_item.get('id')

        while True:
            q = client.get_typed_query(
                'catalogItem',
                query_result_format=QueryResultFormat.ID_RECORDS,
                qfilter='id==%s' % item_id
            )
            records = list(q.execute())
            if records[0].get('status') == 'RESOLVED':
                break
            else:
                time.sleep(5)
                # TODO might have to check when status goes to other state than resolved


def main():
    argument_spec = vcd_catalog_item_argument_spec()
    response = dict(
        msg=dict(type='str'),
    )
    module = CatalogItem(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.params.get('state'):
            response = module.manage_states()
        elif module.params.get('operation'):
            response = module.manage_operations()
        else:
            raise Exception('One of the state/operation should be provided.')

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
