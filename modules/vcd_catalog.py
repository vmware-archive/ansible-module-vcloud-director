#!/usr/bin/python3

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: catalog_module

short_description: Perform CRUD operation on Catalog 

version_added: "0.1"

description:
    - This module will actively managed VDC catalog instances.  Catalog
    can be created and deleted as well as updated.

options:
    name:
        description:
            - The name of the Catalog
        required: true
    publish:
        description:
            - If true, catalog will be shared
        required: false

extends_documentation_fragment:
    - VDC

author:
    - Prakash Chandra Pandey (@prakashpandey)
'''

EXAMPLES = '''
# Pass in a message
- name: create catalog
  vcd_catalog:
    name: test_catalog
'''

RETURN = '''
result: success/failure message relates to catalog operation
'''

from pyvcloud.vcd.org import Org
from pyvcloud.vcd.client import Client
from ansible.module_utils.basic import AnsibleModule
from pyvcloud.vcd.client import BasicLoginCredentials
from ansible.module_utils.vcd import VcdAnsibleModule


def create(client, name, description):
    logged_in_org = client.get_org()
    org = Org(client, resource=logged_in_org)
    catalog = org.create_catalog(name=name, description=description)


def vcd_catalog_argument_spec():
    return dict(
        name=dict(type='str', required=True),
        description=dict(type='str', required=False, default=''),
    )


def main():
    argument_spec = vcd_catalog_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = VcdAnsibleModule(argument_spec=argument_spec,
                              supports_check_mode=True)
    try:
        client = module.client
        name = module.params.get('name')
        description = module.params.get('description')
        create(client, name, description)
    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    response['msg'] = 'Catalog {} has been created!'.format(name)
    module.exit_json(**response)


if __name__ == '__main__':
    main()
