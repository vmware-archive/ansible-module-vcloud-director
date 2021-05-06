# Ansible Collection: vmware.vcloud_director

This repo hosts the `vmware.vcloud_director` Ansible Collection.

The collection includes the VMware modules and plugins to help the management of VMware Cloud Director infrastructure.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.9.10**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

## Installation and Usage

### Installing the Collection from Ansible Galaxy

Before using the VMware Cloud Director collection, you need to install the collection with the `ansible-galaxy` CLI:

    ansible-galaxy collection install vmware.vcloud_director

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
- name: vmware.vcloud_director
```

### Required Python libraries

VMware Cloud Director collection depends upon following third party libraries:

1. The [pyvcloud](https://github.com/vmware/pyvcloud) module is required.
2. VCD Ansible modules require Python 3.6 or above.

### Installing required libraries and SDK

Installing collection does not install any required third party Python libraries or SDKs. You need to install the required Python libraries using following command:

    pip install -r ~/.ansible/collections/ansible_collections/vmware/cloud_director/requirements.txt

If you are working on developing and/or testing VMware community collection, you may want to install additional requirements using following command:

    pip install -r ~/.ansible/collections/ansible_collections/vmware/cloud_director/test-requirements.txt

## Included content

<!--start collection content-->
### Modules
Name | Description
--- | ---
vmware.vcloud_director.vcd_catalog|Manage catalog's states/operations in vCloud Director
vmware.vcloud_director.vcd_catalog_item|Manage catalog_item's states/operations in vCloud Director
vmware.vcloud_director.vcd_disk|Manage disk's states/operations in vCloud Director
vmware.vcloud_director.vcd_external_network|Manage external_network's states/operations in vCloud Director
vmware.vcloud_director.vcd_gateway_services|Manage edge gateway service in vCloud Director
vmware.vcloud_director.vcd_org|Manage org's states/operations in vCloud Director
vmware.vcloud_director.vcd_org_vdc|Manage ORG VDC's states/operations in vCloud Director
vmware.vcloud_director.vcd_resources|Add/Delete/Update VCD Infrastructure resources
vmware.vcloud_director.vcd_roles|Manage role's states/operations in vCloud Director
vmware.vcloud_director.vcd_user|Manage user's states/operations in vCloud Director
vmware.vcloud_director.vcd_vapp|Manage vApp's states/operations in vCloud Director
vmware.vcloud_director.vcd_vapp_network|Manage vApp Network's states/operation in vCloud Director
vmware.vcloud_director.vcd_vapp_vm|Manage VM snapshots states/operations in vCloud Director
vmware.vcloud_director.vcd_vapp_vm_disk|Ansible Module to manage disks in vApp VMs in vCloud Director.
vmware.vcloud_director.vcd_vapp_vm_nic|Manage VM NIC's states/operations in vCloud Director
vmware.vcloud_director.vcd_vdc_gateway|Manage edge gateway's states/operations in vCloud Director
vmware.vcloud_director.vcd_vdc_network|Manage VDC Network's states/operations in vCloud Director

<!--end collection content-->

## Testing and Development

If you want to develop new content for this collection or improve what is already here, the easiest way to work on the collection is to clone it into one of the configured [`COLLECTIONS_PATHS`](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths), and work on it there.


## Publishing New Version

Prepare the release:
- Refresh the changelog: `tox -e antsibull-changelog -- release --verbose --version 1.2.0`
- Clean up the changelog fragments.
- Commit everything and push a PR for review

Push the release:
- Tag the release: `git tag -s 1.0.0`
- Push the tag: `git push origin 1.0.`

## Communication

TBD

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

See [BSD-2 License or GPLv3](LICENSE.txt) to see the full text.
