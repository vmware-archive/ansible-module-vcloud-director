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
module: vcd_fetch_vapp
short_description: This module is to fetch available vapps on vCloud Director
version_added: "2.4"
description:
    - "This module is to fetch available vapps on vCloud Director"
options:
    vdc:
        description:
            - virtual datacenter assigned to org
        required: true

author:
    - mtaneja@vmware.com
'''

EXAMPLES = '''
- name: Test with a message
  vcd_fetch_vapp:
    vdc: Terraform_VDC
'''

RETURN = '''
result: list of all available vapp names on vCloud Director
'''

from pyvcloud.vcd.org import Org
from pyvcloud.vcd.vdc import VDC
from pyvcloud.vcd.client import EntityType
from ansible.module_utils.vcd import VcdAnsibleModule


def vcd_fetch_vapps_argument_spec():
    return dict(
        vdc=dict(type='str', required=True),
    )


def main():
    argument_spec = vcd_fetch_vapps_argument_spec()
    response = dict(
        msg=dict(type='str'),
        vapps=[]
    )
    module = VcdAnsibleModule(argument_spec=argument_spec,
                              supports_check_mode=True)

    try:
        vdc = module.params['vdc']
        client = module.client
        org_resource = client.get_org()
        org = Org(client, resource=org_resource)
        vdc_resource = org.get_vdc(vdc)
        vdc = VDC(client, resource=vdc_resource)
        vapps = vdc.list_resources(EntityType.VAPP)

        for vapp in vapps:
            response['vapps'].append(vapp.get('name'))

    except Exception as error:
        response['msg'] = error.__str__()
        module.fail_json(**response)

    module.exit_json(**response)


if __name__ == '__main__':
    main()
