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
module: vcd_catalog_item
short_description: Manage catalog_item's states/operations in vCloud Director
version_added: "2.4"
description:
    - Manage catalog_item's states/operations in vCloud Director

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
    description:
        description:
            - description of vapp capture
        required: false
    customize_on_instantiate:
        description: true/false if needs to customise vapp on instantiation
        required: false
    overwrite:
        description: true/false if the catalog_item has to be overwritten
        required: false
    state:
        description:
            - state of catalog_item ('present'/'absent').
            - One of operation/state has to be provided.
        required: false
    operation:
        description:
            - operation to perform on catalog_item (capturevapp/list_vms).
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
from pyvcloud.vcd.vapp import VApp
from pyvcloud.vcd.client import Client
from pyvcloud.vcd.client import QueryResultFormat
from ansible.module_utils.vcd import VcdAnsibleModule
from pyvcloud.vcd.exceptions import EntityNotFoundException


VCD_CATALOG_ITEM_STATES = ['present', 'absent']
VCD_CATALOG_ITEM_OPERATIONS = ['capturevapp', 'list_vms']
DEFAULT_CHUNK_SIZE = 1024 * 1024


def vcd_catalog_item_argument_spec():
    return dict(
        catalog_name=dict(type='str', required=True),
        item_name=dict(type='str', required=False, default=None),
        file_name=dict(type='str', required=False),
        chunk_size=dict(
            type='int', required=False, default=DEFAULT_CHUNK_SIZE),
        vapp_name=dict(type='str', required=False),
        vdc_name=dict(type='str', required=False),
        description=dict(type='str', required=False, default=''),
        customize_on_instantiate=dict(
            type='bool', required=False, default=False),
        overwrite=dict(type='bool', required=False, default=False),
        org_name=dict(type='str', required=False, default=None),
        state=dict(choices=VCD_CATALOG_ITEM_STATES, required=False),
        operation=dict(choices=VCD_CATALOG_ITEM_OPERATIONS, required=False)
    )


class CatalogItem(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(CatalogItem, self).__init__(**kwargs)
        self.org = self.get_org()

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

        if operation == "list_vms":
            return self.list_vms()

    def get_org(self):
        org_name = self.params.get('org_name')
        org_resource = self.client.get_org()
        if org_name:
            org_resource = self.client.get_org_by_name(org_name)

        return Org(self.client, resource=org_resource)

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
        catalog_name = self.params.get('catalog_name')
        item_name = self.params.get('item_name')
        file_name = self.params.get('file_name')
        chunk_size = self.params.get('chunk_size')
        response = dict()
        response['changed'] = False
        item_details = {
            "catalog_name": catalog_name,
            "item_name": item_name,
            "file_name": file_name,
            "chunk_size": chunk_size
        }

        if self.is_present():
            msg = "Catalog Item {} is already present."
            response['warnings'] = msg.format(item_name)
            return response

        if file_name.endswith(".ova") or file_name.endswith(".ovf"):
            self.org.upload_ovf(**item_details)
            self.ova_check_resolved()
        else:
            self.org.upload_media(**item_details)

        response['msg'] = "Catalog item {} is uploaded.".format(item_name)
        response['changed'] = True

        return response

    def delete(self):
        catalog_name = self.params.get('catalog_name')
        item_name = self.params.get('item_name')
        response = dict()
        response['changed'] = False

        if not self.is_present():
            msg = "Catalog Item {} is not present."
            response['warnings'] = msg.format(item_name)
            return response

        self.org.delete_catalog_item(name=catalog_name, item_name=item_name)
        response['msg'] = "Catalog Item {} has been deleted.".format(item_name)
        response['changed'] = True

        return response

    def capture_vapp(self):
        vapp_name = self.params.get('vapp_name')
        vdc_name = self.params.get('vdc_name')
        catalog_name = self.params.get('catalog_name')
        item_name = self.params.get('item_name')
        desc = self.params.get('description')
        customize_on_instantiate = self.params.get('customize_on_instantiate')
        overwrite = self.params.get('overwrite')
        response = dict()
        response['changed'] = False

        v = self.org.get_vdc(vdc_name)
        vdc = VDC(self.client, href=v.get('href'))
        vapp = vdc.get_vapp(vapp_name)
        catalog = self.org.get_catalog(catalog_name)
        self.org.capture_vapp(
            catalog_resource=catalog, vapp_href=vapp.get('href'),
            catalog_item_name=item_name, description=desc,
            customize_on_instantiate=customize_on_instantiate,
            overwrite=overwrite)
        self.ova_check_resolved()
        response['msg'] = "Catalog Item {} has been captured".format(item_name)
        response['changed'] = True

        return response

    def ova_check_resolved(self):
        catalog_name = self.params.get('catalog_name')
        item_name = self.params.get('item_name')
        response = False

        source_ova_item = self.org.get_catalog_item(catalog_name, item_name)
        self.check_resolved(source_ova_item, catalog_name, item_name)
        response = True

        return response

    def check_resolved(self, source_ova_item, catalog_name, item_name):
        item_id = source_ova_item.get('id')

        while True:
            q = self.client.get_typed_query(
                'catalogItem',
                query_result_format=QueryResultFormat.ID_RECORDS,
                qfilter='id==%s' % item_id
            )
            records = list(q.execute())
            # TODO might have to check when status goes to other state than resolved
            if records[0].get('status') == 'RESOLVED':
                break
            else:
                time.sleep(5)

    def list_vms(self):
        catalog_name = self.params.get('catalog_name')
        item_name = self.params.get('item_name')
        response = dict()
        response['changed'] = False

        catalog_item = self.org.get_catalog_item(catalog_name, item_name)
        catalog_item_href = catalog_item.Entity.get('href')
        vapp_template_resource = self.client.get_resource(catalog_item_href)
        vapp_template = VApp(
            self.client, name=item_name, resource=vapp_template_resource)

        response['msg'] = [vm.get('name')
                           for vm in vapp_template.get_all_vms()]

        return response


def main():
    argument_spec = vcd_catalog_item_argument_spec()
    response = dict(msg=dict(type='str'))
    module = CatalogItem(argument_spec=argument_spec, supports_check_mode=True)

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
