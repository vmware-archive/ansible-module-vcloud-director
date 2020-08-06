

# ansible-module-vcloud-director

## Overview
**ansible-module-vcloud-director** is a set of ansible modules that manage a VMware vCloud Director instance.

## Try it out

### Prerequisites

* The [pyvcloud](https://github.com/vmware/pyvcloud) module is required. 
* vCD Ansible modules require Python 3.6 or above.

### Build & Run

1. pip install --user pyvcloud
2. git clone https://github.com/vmware/ansible-module-vcloud-director
3. cd ansible-module-vcloud-director

## Documentation

Refer [docs](https://github.com/vmware/ansible-module-vcloud-director/wiki/vCD-Ansible-Modules) to know more about available modules's usage.

1. vcd_catalog
2. vcd_catalog_item
3. vcd_disk
4. vcd_external_network
5. vcd_org
6. vcd_org_vdc
7. vcd_roles
8. vcd_user
9. vcd_vapp
10. vcd_vapp_network
11. vcd_vapp_vm
12. vcd_vapp_vm_disk
13. vcd_vapp_vm_nic
14. vcd_vapp_vm_snapshot
15. vcd_vdc_gateway
16. vcd_vdc_network
17. vcd_gateway_services

We have also written sample ansible playbooks to show usage of these ansible modules and their interaction with vCD instance. We are using [ansible role](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html)
concept to define playbooks in modular fashion for these modules. Please refer [roles](https://github.com/vmware/ansible-module-vcloud-director/tree/master/roles) and [main.yml](https://github.com/vmware/ansible-module-vcloud-director/blob/master/main.yml) to see usage.

## Releases & Major Branches

Following is the approx version matrix which are tested and supported through vCD ansible modules,

| vCD Version    | Pyvcloud Version    | API Versions       |
| -------------  | :-------------:     | -----:             |
| vCD 9.1        | 20.1                | 28.0 / 29.0 / 30.0 |
| vCD 9.5        | 22.0.1              | 29.0 / 30.0 / 31.0 / 32.0 / 33.0 |
| vCD 10.0       | 22.0.1              | 30.0 / 31.0 / 32.0 / 33.0 / 34.0 |
| vCD 10.1       | 22.0.1              | 30.0 / 31.0 / 32.0 / 33.0 / 34.0 |

Note - Testing is still in progress for new releases of vCD and Pyvcloud.

## Contributing

The **ansible-module-vcloud-director** project team welcomes contributions from the community. Before you start working with ansible-module-vcloud-director, please read our [Developer Certificate of Origin](https://cla.vmware.com/dco).
All contributions to this repository must be signed as described on that page. Your signature certifies that you wrote the patch or have the right to pass it on as an open-source patch. For more detailed information, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## License
[BSD-2 License or GPLv3](LICENSE.txt)
