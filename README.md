

# ansible-module-vcloud-director

## Overview
**ansible-module-vcloud-director** is a set of ansible modules to manage various operations on VMware vCloud Director.

## Try it out

## Prerequisites

1. [Python 3.6 or above](https://www.python.org/downloads/)
2. [pyvcloud](https://github.com/vmware/pyvcloud)

## Build & Run

1. pip install --user pyvcloud
2. git clone https://github.com/vmware/ansible-module-vcloud-director
3. cd ansible-module-vcloud-director
4. ansible-playbook -i main.yml

## Usage

This repository packaged below two components to manage VCD,

1. Ansible Modules
2. Ansbile Playbooks

Ansible playbooks are the client which use modules as a gateway to interact with VCD. We have written various ansible playbooks to show how to interact with VCD. We are using [ansible roles](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html) to define playbooks in modular fashion for each module. Please refer [roles](https://github.com/vmware/ansible-module-vcloud-director/tree/master/roles) and [main.yml](https://github.com/vmware/ansible-module-vcloud-director/blob/master/main.yml) to see usage.

## Deployment

These modules may be deployed in two ways,

##### Local Deployment

We may define `modules` and `module_utils` settings in `ansible.cfg` to deploy ansible modules local to a directory. We have packaged `ansible.cfg` with this repository. You may refer [this](https://github.com/vmware/ansible-module-vcloud-director/blob/master/ansible.cfg)

##### Global Deployment

We may copy `modules` and `module_utils` to below paths to deploy ansible modules globally.

- `/usr/share/ansible/plugins/modules/`
- `/usr/share/ansible/plugins/module_utils`

## Documentation

Refer [docs](https://github.com/vmware/ansible-module-vcloud-director/wiki/vCD-Ansible-Modules) to know more about available modules and their usage.

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

## Releases & Major Branches

Following is the approx version matrix which are tested and supported through vCD ansible modules,

| vCD Version    |  API Versions       |
| -------------  | -------------       |
| vCD 9.0        | 29.0 			   |
| vCD 9.1        | 30.0				   |
| vCD 9.5        | 31.0                |
| vCD 9.7        | 32.0 		       |
| vCD 10.0       | 33.0                |
| vCD 10.1       | 34.0                |

Note - Testing is still in progress for new releases of vCD and Pyvcloud.

## Contributing

The **ansible-module-vcloud-director** project team welcomes contributions from the community. Before you start working with ansible-module-vcloud-director, please read our [Developer Certificate of Origin](https://cla.vmware.com/dco).
All contributions to this repository must be signed as described on that page. Your signature certifies that you wrote the patch or have the right to pass it on as an open-source patch. For more detailed information, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## License
[BSD-2 License or GPLv3](LICENSE.txt)
