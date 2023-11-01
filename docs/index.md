---

layout: default
---
<!-- Setting Use Case -->
<div class="environment-settings col-12" id="environment-settings">
<h2>Environment Settings</h2>
<hr />
<ol>
<li>
<h3>Login</h3>
</li>
<pre>
<code>
 - name: vCloudDirectorAnsible
   hosts: localhost
   environment:
	env_user: VCD_USER_NAME
	env_password: VCD_USER_PASSWORD
	env_host: VCD_URL            ## VCD Instance URL
	env_org: VCD_ORG             ## VCD ORG to login
	env_api_version: PYVCLOUD_API_VERSION
	env_verify_ssl_certs: false

</code>
</pre>
<p>
VCD Ansible Modules prefer following two ways to set login variables for vCloud Director instance.
</p>
<ol>
<li>
<b>Environment Variables - </b>
The end user can set login variables in the environment as shown above. Once they are set, modules will use these variables for all the subsequent resource operations automatically.
</li>
<li>
<b>Local Variables - </b>
The end user can set login variables for specific module(s) as local variables. This approach gives more freedom to the end user to execute specific module(s) on specific vCloud Director instance(s).
</li>
</ol>
<br />
<p>
By default, the priority will be given to <b>Local Variables</b> than <b>Environment Variables.</b>
</p>
<p>
If "API_TOKEN" is passed in the <code>user</code> variable the <code>password</code> variable will be interpreted as <a href=https://docs.vmware.com/en/VMware-Cloud-Director/10.4/VMware-Cloud-Director-Tenant-Portal-Guide/GUID-A1B3B2FA-7B2C-4EE1-9D1B-188BE703EEDE.html>API Access Token</a> and OAuth 2.0 based authentication is used instead of user credentials. This is useful if an <a href=https://docs.vmware.com/en/VMware-Cloud-Director/10.4/VMware-Cloud-Director-Service-Provider-Admin-Portal-Guide/GUID-3326986B-931C-4FDE-AF47-D5A863191072.html>external identity provider</a> is configured for the authentication with vCloud Director.
</p>
<li>
<h3>Response</h3>
<p>VCD Ansible Modules provide sort of a unanimous response across all operations. The response shall contain atleast following properties,</p>
<ul>
<li>msg - the success/failure string corresponding to the resource</li>
<li>changed - "true" if resource has been modified at the infrastrucutre else "false"
</li>
</ul>
</li>
</ol>
</div>
<!--				  -->
<!-- Catalogs Use Case -->
<div class="catalog-usage col-12" id="catalog-usage">
<h2>Catalog Example Usage</h2>
<hr />
<ol>
<li>
<h3>Catalog States</h3>
<ul>
<li>
<h5>Create Catalog</h5>
</li>
<pre>
<code>
 - name: create catalog
   vcd_catalog:
	catalog_name: "test_catalog"
	description: "test_description"
	state: "present"

</code>
</pre>
 <h5>Argument Reference</h5>
 <ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>catalog_name - (Required) Name of the catalog</li>
<li>description - (Required) Description text for the catalog</li>
<li>state == "present" (Required) to create catalog</li>
</ul>
<li>
<h5>Update Catalog</h5>
</li>
<pre>
<code>
 - name: update catalog name and description
   vcd_catalog:
	catalog_name: "test_catalog"
	new_catalog_name: "new_test_catalog"
	description: "test_description"
	state: "update"
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>catalog_name - (Required) Old name of the catalog</li>
 <li>new_catalog_name - (Required) New name of the catalog</li>
 <li>description - (Required) New description text for the catalog</li>
 <li>state == "update" (Required) to update catalog</li>
 </ul>
 <li>
 <h5>Delete Catalog</h5>
 </li>
 <pre>
 <code>
 - name: delete catalog
   vcd_catalog:
	catalog_name: "test_catalog"
	state: "absent"
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>catalog_name - (Required) Name of the catalog</li>
 <li>state == "absent" (Required) to delete catalog</li>
 </ul>
 </ul>
</li>
 <li>
 <h3>Catalog Operations</h3>
 <ul>
 <li>
 <h5>Share/Unshare Catalog</h5>
 <pre>
 <code>
 - name: share/unshare catalog
   vcd_catalog:
	catalog_name: "test_catalog"
	shared: "true"
	operation: "shared"
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>catalog_name - (Required) Name of the catalog</li>
 <li>shared - (Optional) true/false to share/unshare the catalog. The default value is true for the argument</li>
 <li>operation == "shared" (Required) to share/unshare catalog</li>
</ul>
</li>
<li>
 <h5>List Catalog Items</h5>
 <pre>
 <code>
 - name: list catalog items
   vcd_catalog:
        catalog_name: "test_catalog"
        operation: "list_items"
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>catalog_name - (Required) Name of the catalog</li>
 <li>operation == "list_items" (Required) to list catalog items</li>
</ul>
</li>
</ul>
</li>
</ol>
</div>
<!--				  -->
<!-- Catalog Item Use Case -->
<div class="catalog-item-usage col-12" id="catalog-item-usage">
<h2>Catalog Item Example Usage</h2>
<hr />
<ol>
<li>
<h3>Catalog Item States</h3>
<ul>

<li>
<h5>Upload Catalog Media/Ova</h5>
</li>
<pre>
<code>
 - name: upload media
   vcd_catalog_item:
	catalog_name: "test_catalog"
	item_name: "test_item_media"
	file_name: "test_item_media.iso"
	chunk_size: 1048576
	description: "test_description"
	state: "present"

</code>
</pre>
<pre>
<code>
 - name: upload ova
   vcd_catalog_item:
    catalog_name: "test_catalog"
    item_name: "test_item_ova"
    file_name: "test_item_ova.ova"
    chunk_size: 1048576
    description: "test_description"
    state: "present"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>catalog_name - (Required) Name of the catalog</li>
<li>item_name - (Required) Name for the catalog media/ova</li>
<li>file_name - (Required) Path of the catalog media/ova file</li>
<li>chunk_size - (Optional) Size of chunks in which the file will be uploaded to the catalog</li>
<li>description - (Optional) catalog item description</li>
<li>state == "present" (Required) to upload catalog media/ova</li>
</ul>
<li>
<h5>Delete Catalog Media/Ova</h5>
</li>
<pre>
<code>
 - name: delete media
   vcd_catalog_item:
	catalog_name: "test_catalog"
	item_name: "test_media_item"
	state: "absent"

</code>
</pre>
<pre>
<code>
 - name: delete ova
   vcd_catalog_item:
    catalog_name: "test_catalog"
    item_name: "test_ova_item"
    state: "absent"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>catalog_name - (Required) Name of the catalog</li>
<li>item_name - (Required) Name for the catalog media/ova</li>
<li>state == "absent" (Required) to delete catalog media/ova</li>
</ul>
</ul>
</li>
<li>
<h3>Catalog Item Operations</h3>
<ul>
<li>
<h5>Capture Vapp</h5>
<pre>
<code>
  - name: capture vapp
    vcd_catalog_item:
	catalog_name: "test_catalog"
	item_name: "test_item"
	vapp_name: "test_vapp"
	vdc_name: "test_vdc"
	description: "test_description"
	customize_on_instantiate: false
	overwrite: false
	operation: "capturevapp"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>catalog_name - (Required) Name of the catalog</li>
<li>item_name - (Required) Name of the catalog media/ova inside a catalog</li>
<li>vapp_name - (Required) Name of the vApp to capture</li>
<li>vdc_name - (Required) Name of the vdc</li>
<li>description - (Optional) Description of the catalog item</li>
<li>customize_on_instantiate - (Optional) true/false, Flag indicating if the vApp to be instantiated from this vApp template can be customized. The default value is false.</li>
<li>overwrite - (Optional) true/false, Flag indicating if the item in the catalog has to be overwritten if it already exists. If it doesn't exist, this flag is not used. The default value is false</li>
<li>operation == "capturevapp" (Required) to capture vApp as a template into a catalog</li>
</ul>
</li>
<li>
<h5>List Catalog Item vms</h5>
<pre>
<code>
  - name: capture vapp
    vcd_catalog_item:
        catalog_name: "test_catalog"
        item_name: "test_item"
        description: "test_description"
        operation: "list_vms"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>catalog_name - (Required) Name of the catalog</li>
<li>item_name - (Required) Name of the catalog media/ova</li>
<li>description - (Optional) Description of the catalog item</li>
<li>operation == "list_vms" (Required) to list catalog item vms</li>
</ul>
</li>
</ul>
</li>
</ol>
</div>
<!--				  -->
<!-- vApp Use Case -->
<div class="vapp-usage col-12" id="vapp-usage">
<h2>Vapp Example Usage</h2>
<hr />
<ol>
<li>
<h3>Vapp States</h3>
<ul>
<li>
<h5>Create Vapp</h5>
</li>
<pre>
<code>
 - name: create vapp
   vcd_vapp:
	vapp_name: "test_vapp"
	template_name: "test_template"
	catalog_name: "test_catalog"
	vdc: "test_vdc"
	description: "test_description"
	network: "test_network"
	fence_mode: "bridged"
	ip_allocation_mode: 'dhcp'
	deploy: true
	power_on: true
	accept_all_eulas: false
	memory: 1024000
	cpu: 1000
	disk_size: 10240000
	vmpassword: "test_password"
	cust_script: "test_script"
	vm_name: "test_vm"
	hostname: "test_host"
	ip_address: "1.1.1.1"
	storage_profile: "Standard"
	network_adapter_type: "VMXNET"
	state: "present"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vapp_name - (Required) name of the new vApp</li>
<li>vdc - (Required) name of the vdc</li>
<li>catalog_name - (Optional) name of the catalog</li>
<li>template_name - (Optional) name of the vApp template</li>
<li>description - (Optional) description of the new vApp. The default value is None.</li>
<li>network - (Optional) name of a vdc network. When provided, connects the vm to the network. The default value is None.</li>
<li>fence_mode - (Optional) fence mode. Possible values are pyvcloud.vcd.client.FenceMode.BRIDGED.value and pyvcloud.vcd.client.FenceMode.NAT_ROUTED.value. The default value is pyvcloud.vcd.client.FenceMode.BRIDGED.value.</li>
<li>ip_allocation_mode - (Optional) ip allocation mode. Acceptable values are 'pool', 'dhcp' and 'manual'. The default value is 'dhcp'.</li>
<li>deploy - (Optional) if true deploy the vApp after instantiation. The default value is true.</li>
<li>power_on - (Optional) if true, power on the vApp after instantiation. The default value is true.</li>
<li>accept_all_eulas - (Optional) true, confirms acceptance of all EULAs in a vApp template. The default value is false.</li>
<li>memory - (Optional) max memory that can allocated. The default value is None.</li>
<li>cpu - (Optional) max cpu that can be allocated. The default value is None.</li>
<li>disk_size - size of the disk(Optional). The default value is None.</li>
<li>vmpassword - (Optional) the administrator password of vm. The default value is None.</li>
<li>cust_script - (Optional) script to run on guest customization. The default value is None.</li>
<li>vm_name - (Optional) when provided, sets the name of the vm. The default value is None.</li>
<li>ip_address - (Optional) when provided, sets the ip_address of the vm. The default value is None.</li>
<li>hostname - (Optional) when provided, sets the hostname of the guest OS. The default value is None.</li>
<li>storage_profile - (Optional) name of the storage profile. The default value is None.</li>
<li>network_adapter_type - (Optional) One of the values in pyvcloud.vcd.client.NetworkAdapterType. The default value is None.</li>
<li>state == "present" (Required) to create vapp</li>
</ul>
<li>
<h5>Delete Vapp</h5>
</li>
<pre>
<code>
  - name: delete vapp
    vcd_vapp:
	vapp_name: "test_vapp"
	vdc: "test_vdc"
	force: true
	state: "absent"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vapp_name - (Required) name of the vApp to be deleted</li>
<li>vdc - (Required) name of the vdc</li>
<li>force - (Optional) default false. If true, will instruct vcd to force delete the vapp</li>
<li>state == "absent" (Required) to delete vapp</li>
</ul>
</ul>
</li>
<li>
<h3>Vapp Operations</h3>
<ul>
<li>
<h5>Power on vapp</h5>
<pre>
<code>
 - name: power on vapp
   vcd_vapp:
	vapp_name: "test_vapp"
	vdc: "test_vdc"
	operation: "poweron"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vapp_name - (Required) name of the vApp to be powered on</li>
<li>vdc - (Required) name of the vdc</li>
<li>operation == "poweron" (Required) to power on vapp</li>
</ul>
</li>
<li>
<h5>Power off vapp</h5>
<pre>
<code>
 - name: power off vapp
   vcd_vapp:
	vapp_name: "test_vapp"
	vdc: "test_vdc"
	operation: "poweroff"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vapp_name - (Required) name of the vApp to be powered off</li>
<li>vdc - (Required) name of the vdc</li>
<li>operation == "poweroff" (Required) to power off vapp</li>
</ul>
</li>
<li>
<h5>Undeploy vapp</h5>
<pre>
<code>
 - name: undeploy vapp
   vcd_vapp:
	vapp_name: "test_vapp"
	vdc: "test_vdc"
	operation: "undeploy"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vapp_name - (Required) name of the vApp to be undeploy</li>
<li>vdc - (Required) name of the vdc</li>
<li>operation == "undeploy" (Required) to undeploy vapp</li>
</ul>
</li>
<li>
<h5>Deploy vapp</h5>
<pre>
<code>
 - name: deploy vapp
   vcd_vapp:
	vapp_name: "test_vapp"
	vdc: "test_vdc"
	operation: "deploy"

</code>
</pre>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vapp_name - (Required) name of the vApp to be deploy</li>
<li>vdc - (Required) name of the vdc</li>
<li>operation == "deploy" (Required) to deploy vapp</li>
</ul>
</li>
<li>
<h5>Get list of vms</h5>
<pre>
<code>
 - name: get list of vms
   vcd_vapp:
        vapp_name: "test_vapp"
        vdc: "test_vdc"
        operation: "list_vms"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vapp_name - (Required) name of the vApp to get a list of vms from</li>
<li>vdc - (Required) name of the vdc</li>
<li>operation == "list_vms" (Required) get list of vms</li>
</ul>
</li>
<li>
<h5>Get list of vapp networks</h5>
<pre>
<code>
 - name: get list of networks
   vcd_vapp:
        vapp_name: "test_vapp"
        vdc: "test_vdc"
        operation: "list_networks"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vapp_name - (Required) name of the vApp to get a list of networks from</li>
<li>vdc - (Required) name of the vdc</li>
<li>operation == "list_networks" (Required) get list of networks</li>
</ul>
</li>
</ul>
</li>
</ol>
</div>
<!--				  -->
<!-- vApp VM Use Case -->
<div class="vapp-vm-usage col-12" id="vapp-vm-usage">
<h2>Vapp VM Example Usage</h2>
<hr />
<ol>
<li>
<h3>Vapp VM States</h3>
<ul>
<li>
<h5>Create Vapp VM</h5>
<ul>
<li>
<h5>Create Vapp VM from Catalog</h5>
</li>
<pre>
<code>
 - name: create vapp vm from catalog
   vcd_vapp_vm:
	target_vm_name: "test_vapp_vm"
	target_vapp: "web2"
	source_vdc: "test_vdc"
	target_vdc: "test_vdc"
	source_catalog_name: "test_catalog"
	source_template_name: "centos7"
	source_vm_name: "CentOS7"
	hostname: "vcdcell"
	vmpassword: "rootpass"
	vmpassword_auto: "false"
	vmpassword_reset: "false"
	ip_allocation_mode: "DHCP"
	power_on: "false"
	all_eulas_accepted: "true"
	storage_profile: "Standard"
	network: "web2Network"
	cust_script: "test_script"
	deploy: false
	state: "present"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Optional) target vm name</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>source_vdc - (Required) name of the source vdc</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>source_catalog_name - (Required) name of the sorce catalog</li>
<li>source_template_name - (Required) name of the source template</li>
<li>source_vm_name - (Required) source vm name</li>
<li>hostname - (Optional) target guest hostname</li>
<li>vmpassword - (Optional) the administrator password of the vm</li>
<li>vmpassword_auto - (Optional) if true, auto generate administrator password</li>
<li>vmpassword_reset - (Optional) true, if the administrator password for this vm must be reset after first use</li>
<li>ip_allocation_mode - (Optional) Name of the ip ip allocation mode. The default value is 'DHCP'.</li>
<li>power_on - (Optional) true if the vApp should be powered-on at instantiation. The default value is true.</li>
<li>all_eulas_accepted - (Optional) true confirms acceptance of all EULAs in the vApp.  The default value is None.</li>
<li>storage_profile - (Optional) name of the storage profile. The default value is None.</li>
<li>network - (Optional) name of the vApp network to connect. If omitted, the vm won't be connected to any network</li>
<li>cust_script - (Optional) script to run on guest customization</li>
<li>deploy - (Optional) true, if the vApp should be deployed at instantiation.  The default value is true.</li>
<li>state == "present" (Required) to create vapp vm</li>
</ul>
<li>
<h5>Create Vapp VM from Vapp</h5>
</li>
<pre>
<code>
 - name: create vapp vm from vapp
   vcd_vapp_vm:
	target_vm_name: "test_vapp_vm"
	target_vapp: "web2"
	source_vdc: "test_vdc"
	target_vdc: "test_vdc"
	source_vapp: "web"
	source_vm_name: "CentOS7"
	hostname: "vcdcell"
	vmpassword: "rootpass"
	vmpassword_auto: "false"
	vmpassword_reset: "false"
	ip_allocation_mode: "DHCP"
	power_on: "false"
	all_eulas_accepted: "true"
	storage_profile: "Standard"
	network: "web2Network"
	cust_script: "test_script"
	deploy: false
	state: "present"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Optional) target vm name</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>source_vdc - (Required) name of the source vdc</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>source_vapp - (Required) name of the sorce vapp</li>
<li>source_vm_name - (Required) source vm name</li>
<li>hostname - (Optional) target guest hostname</li>
<li>vmpassword - (Optional) the administrator password of the vm</li>
<li>vmpassword_auto - (Optional) if true, auto generate administrator password</li>
<li>vmpassword_reset - (Optional) true, if the administrator password for this vm must be reset after first use</li>
<li>ip_allocation_mode - (Optional) Name of the ip ip allocation mode. The default value is 'DHCP'.</li>
<li>power_on - (Optional) true if the vApp should be powered-on at instantiation. The default value is true.</li>
<li>all_eulas_accepted - (Optional) true confirms acceptance of all EULAs in the vApp. The default value is None.</li>
<li>storage_profile - (Optional) name of the storage profile. The default value is None.</li>
<li>network - (Optional) name of the vApp network to connect. If omitted, the vm won't be connected to any network</li>
<li>cust_script - (Optional) script to run on guest customization</li>
<li>deploy - (Optional) true, if the vApp should be deployed at instantiation. The default value is true.</li>
<li>state == "present" (Required) to create vapp vm</li>
</ul>
</ul>
<li>
<h5>Update Vapp VM</h5>
<ul>
<li>
<h5>Update cpu</h5>
</li>
<pre>
<code>
 - name: modify cpu vapp vm
   vcd_vapp_vm:
	target_vm_name: "test_vm"
	target_vapp: "web2"
	target_vdc: "Terraform_VDC"
	virtual_cpus: 2
	cores_per_socket: 2
	state: "update"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Required) name of the target vm</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>virtual_cpus - (Required) number of virtual CPUs to configure on the vm</li>
<li>cores_per_socket - (Optional) number of cores per socket</li>
<li>state == "update" (Required) to update vapp vm cpu & cpu cores</li>
</ul>
<li>
<h5>Update memory</h5>
</li>
<pre>
<code>
 - name: modify memory vapp vm
   vcd_vapp_vm:
	target_vm_name: "test_vm"
	target_vapp: "web2"
	target_vdc: "test_vdc"
	memory: 4096
	state: "update"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Required) name of the target vm</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>memory - (Required) number of MB of memory to configure on the vm</li>
<li>state == "update" (Required) to update vapp vm memory</li>
</ul>
</ul>
<li>
<h5>Update compute policy</h5>
</li>
<pre>
<code>
- name: modify compute policy vapp vm
  vcd_vapp_vm:
    target_vm_name: "test_vm"
    target_vapp: "web2"
    target_vdc: "test_vdc"
    compute_policy_href: "https://vcloud.example.com/cloudapi/1.0.0/vdcComputePolicies/51"
    state: "update"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Required) name of the target vm</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>compute_policy_href - (Required) the href of the compute policy to apply</li>
<li>state == "update" (Required) to update vapp vm memory</li>
</ul>
</ul>
<li>
<h5>Delete Vapp VM</h5>
</li>
<pre>
<code>
 - name: delete vapp vm
   vcd_vapp_vm:
	 target_vm_name: "test_vm"
	 target_vapp: "web2"
	 target_vdc: "test_vdc"
	 state: "absent"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Required) name of the target vm</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>state == "absent" (Required) to delete vapp vm</li>
</ul>
</li>
</li>
</ul>
</li>
<li>
<h3>Vapp VM Operations</h3>
<ul>
<li>
<h5>Power on vapp vm</h5>
<pre>
<code>
 - name: power on vapp vm
   vcd_vapp_vm:
	target_vm_name: "test_vapp"
	target_vapp: "web2"
	target_vdc: "test_vdc"
	operation: "poweron"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Required) name of the target vm</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>operation == "poweron" (Required) to power on vapp vm</li>
</ul>
</li>
<li>
<h5>Power off vapp vm</h5>
<pre>
<code>
 - name: power off vapp vm
   vcd_vapp_vm:
	target_vm_name: "test_vapp"
	target_vapp: "web2"
	target_vdc: "test_vdc"
	operation: "poweroff"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Required) name of the target vm</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>operation == "poweroff" (Required) to power off vapp vm</li>
</ul>
</li>
<li>
<h5>Reload vapp vm</h5>
<pre>
<code>
 - name: reload vapp vm
   vcd_vapp_vm:
	target_vm_name: "test_vapp_vm"
	target_vapp: "web2"
	target_vdc: "test_vdc"
	operation: "reloadvm"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Required) name of the target vm</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>operation == "reloadvm" (Required) to reload vapp vm</li>
</ul>
</li>
<li>
<h5>Undeploy Vapp VM</h5>
<pre>
<code>
 - name: undeploy vapp vm
   vcd_vapp_vm:
	target_vm_name: "test_vm"
	target_vapp: "web2"
	target_vdc: "test_vdc"
	operation: "undeploy"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Required) name of the target vm</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>operation == "undeploy" (Required) to undeploy vapp vm</li>
</ul>
</li>
<li>
<h5>Deploy Vapp VM</h5>
<pre>
<code>
 - name: deploy vapp vm
   vcd_vapp_vm:
	target_vm_name: "test_vm"
	target_vapp: "web2"
	target_vdc: "test_vdc"
	operation: "deploy"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Required) name of the target vm</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>operation == "deploy" (Required) to deploy vapp vm</li>
</ul>
</li>
<li>
<h5>List Vapp VM Disks</h5>
<pre>
<code>
 - name: list vapp vm disks
   vcd_vapp_vm:
    target_vm_name: "test_vm"
    target_vapp: "web2"
    target_vdc: "test_vdc"
    operation: "list_disks"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Required) name of the target vm</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>operation == "list_disks" (Required) to list vapp vm disks</li>
</ul>
</li>
<li>
<h5>List Vapp VM NICs</h5>
<pre>
<code>
 - name: list vapp vm nics
   vcd_vapp_vm:
    target_vm_name: "test_vm"
    target_vapp: "web2"
    target_vdc: "test_vdc"
    operation: "list_nics"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>target_vm_name - (Required) name of the target vm</li>
<li>target_vapp - (Required) name of the target vapp</li>
<li>target_vdc - (Required) name of the target vdc</li>
<li>operation == "list_nics" (Required) to list vapp vm nics</li>
</ul>
</li>
</ul>
</li>
</ol>
</div>
<!--                  -->
<!-- vApp VM Disk Use Case -->
<div class="vapp-vm-disk-usage col-12" id="vapp-vm-disk-usage">
<h2>Vapp VM Disk Example Usage</h2>
<hr />
<ol>
<li>
<h3>Vapp VM Disk States</h3>
<ul>
<li>
<h5>Create Vapp VM Disk</h5>
</li>
<pre>
<code>
  - name: create vapp vm disk
    vcd_vapp_vm_disk:
     vm_name: "test_vm"
     vapp: "test_vapp"
     vdc: "test_vdc"
     size: "10240"
     state: "present"

</code>
</pre>
<h4>
	Note: Name of the new disk and instance id are not in user control. They are going to be managed by Pyvcloud internally. But our module manages to return metadata such as new disk name/size/instance id which can be further
	used.
</h4>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vm_name - (Required) name of the VM</li>
<li>vapp - (Required) name of the vApp</li>
<li>vdc - (Required) name of the vdc</li>
<li>size - (Required) size in MB of the new disk</li>
<li>state == "present" (Required) to create disk</li>
</ul>
<li>
<h5>Update vapp vm disk</h5>
</li>
<pre>
<code>
 - name: update disk
   vcd_vapp_vm_disk:
      vm_name: "test_vm"
      vapp: "test_vapp"
      vdc: "test_vdc"
      disk_name: "Hard disk 3"
      size: "10240"
      state: "update"

</code>
</pre>
<h4>
    Note: There are few things to take care before trying to update existing hard disks such as,<br />
    a) Fast-provisioned hard drives can not be resized. <br />
    b) Hard drives part of the VM snapshot may not be able to resize.
</h4>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vm_name - (Required) name of the VM</li>
<li>vapp - (Required) name of the vApp</li>
<li>vdc - (Required) name of the vdc</li>
<li>disk_name - (Required) name of the disk to be updated</li>
<li>size - new size of the disk</li>
<li>state == "update" (Required) to update disk</li>
</ul>
<li>
<h5>Delete Vapp VM Disk</h5>
</li>
<pre>
<code>
  - name: delete disk
    vcd_vapp_vm_disk:
      vm_name: "test_vm"
      vapp: "test_vapp"
      vdc: "test_vdc"
      disks:
        - 'Hard disk 3'
        - 'Hard disk 4'
      state: "absent"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vm_name - (Required) name of the VM</li>
<li>vapp - (Required) name of the vApp</li>
<li>vdc - (Required) name of the vdc</li>
<li>disks - (Required) list of the disk names to be deleted</li>
<li>state == "absent" (Required) to delete disk</li>
</ul>
</ul>
</li>
<li>
<h3>Vapp VM Disk Operations</h3>
<ul>
<li>
<h5>Read vapp vm disk</h5>
<pre>
<code>
 - name: read disks
   vcd_vapp_vm_disk:
      vm_name: "test_vm"
      vapp: "test_vapp"
      vdc: "test_vdc"
      operation: "read"

</code>
</pre>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vm_name - (Required) name of the VM</li>
<li>vapp - (Required) name of the vApp</li>
<li>vdc - (Required) name of the vdc</li>
<li>operation == "read" (Required) to read disks</li>
</ul>
</li>
</ul>
</li>
</ol>
</div>
<!--                  -->
<!-- vApp VM NIC Use Case -->
<div class="vapp-vm-nic-usage col-12" id="vapp-vm-nic-usage">
<h2>Vapp VM NIC Example Usage</h2>
<hr />
<ol>
<li>
<h3>Vapp VM NIC States</h3>
<ul>
<li>
<h5>Create Vapp VM NIC</h5>
</li>
<pre>
<code>
  - name: create vapp vm nic
    vcd_vapp_vm_nic:
     vm_name: "test_vm"
     vapp: "test_vapp"
     vdc: "test_vdc"
     network: "web2Network"
     state: "present"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vm_name - (Required) name of the VM</li>
<li>vapp - (Required) name of the vApp</li>
<li>vdc - (Required) name of the vdc</li>
<li>network - (Required) name of the vApp network to connect</li>
<li>ip_allocation_mode - (Optional) Set Ip Allocation Mode (DHCP/MANUAL/POOL) for newly added Nic</li>
<li>ip_address - (Optional) Set Ip Address of newly added Nic</li>
<li>state == "present" (Required) to create nic</li>
</ul>
<li>
<h5>Update vapp vm nic</h5>
<pre>
<code>
 - name: update nic
   vcd_vapp_vm_nic:
      vm_name: "test_vm"
      vapp: "test_vapp"
      vdc: "test_vdc"
      nic_id: 1
      network: "web2Network"
      ip_allocation_mode: "MANUAL"
      ip_address: "172.16.1.122"
      state: "update"

</code>
</pre>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vm_name - (Required) name of the VM</li>
<li>vapp - (Required) name of the vApp</li>
<li>vdc - (Required) name of the vdc</li>
<li>nic_id - (Required) connection index of the nic</li>
<li>network - (Optional) name of the vApp network to connect</li>
<li>ip_allocation_mode - (Optional) Set Ip Allocation Mode (DHCP/MANUAL/POOL) for newly added Nic</li>
<li>ip_address - (Optional) Set Ip Address of newly added Nic</li>
<li>state == "update" (Required) to update nic</li>
</ul>
<li>
<h5>Delete Vapp VM NIC</h5>
</li>
<pre>
<code>
  - name: delete nic
    vcd_vapp_vm_nic:
      vm_name: "test_vm"
      vapp: "test_vapp"
      vdc: "test_vdc"
      nic_id:
        - 1
      state: "absent"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vm_name - (Required) name of the VM</li>
<li>vapp - (Required) name of the vApp</li>
<li>vdc - (Required) name of the vdc</li>
<li>nic_id - (Required) list of nic ids to be deleted</li>
<li>state == "absent" (Required) to delete nic</li>
</ul>
</li>
<li>
<h3>Vapp VM NIC Operations</h3>
<ul>
<h5>Read vapp vm nics</h5>
<pre>
<code>
 - name: read nics
   vcd_vapp_vm_nic:
      vm_name: "test_vm"
      vapp: "test_vapp"
      vdc: "test_vdc"
      operation: "read"

</code>
</pre>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vm_name - (Required) name of the VM</li>
<li>vapp - (Required) name of the vApp</li>
<li>vdc - (Required) name of the vdc</li>
<li>operation == "read" (Required) to read available Nics</li>
</ul>
</ul>
</li>
</ul>
</li>
</ol>
</div>
<!--                  -->
<!-- vApp Network Use Case -->
<div class="vapp-network-usage col-12" id="vapp-network-usage">
<h2>Vapp Network Example Usage</h2>
<hr />
<ol>
<li>
<h3>Vapp Network States</h3>
<ul>
<li>
<h5>Create Vapp Network</h5>
</li>
<pre>
<code>
 - name: create vapp network connected to vdc network
   vcd_vapp_network:
     network: "web2Network"
	 vapp: "web2"
	 vdc: "test_vdc"
	 parent_network: "webs"
	 state: "present"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>network - (Required) name of the network</li>
<li>vapp - (Required) name of the vapp</li>
<li>vdc - (Required) name of the vdc</li>
<li>parent_network - (Optional) name of the parent vdc network to connect.</li>
<li>ip_scope - (Optional) IP scope (gateway-address/bits) in case to create internal network.</li>
<li>state == "present" (Required) to create vapp network</li>
</ul>
</ul>
<ul>
<li>
<h5>Delete Vapp Network</h5>
</li>
<pre>
<code>
 - name: delete vapp network
   vcd_vapp_network:
     network: "web2Network"
     vapp: "web2"
     vdc: "test_vdc"
     state: "absent"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>network - (Required) name of the network</li>
<li>vapp - (Required) name of the vapp</li>
<li>vdc - (Required) name of the vdc</li>
<li>state == "absent" (Required) to delete vapp network</li>
</ul>
</ul>
</li>
</ol>
</div>
<!--				  -->
<!-- Independent Disk Use Case -->
<div class="disk-usage col-12" id="disk-usage">
<h2>Disk Example Usage</h2>
<hr />
<ol>
<li>
<h3>Disk States</h3>
</li>
<ul>
<li>
<h5>Create Disk</h5>
</li>
<pre>
<code>
 - name: create disk
   vcd_disk:
	disk_name: "test_disk"
	description: "Test Disk"
	size: "100"
	vdc: "Test_VDC"
	state: "present"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>disk_name - (Required) name of the new disk</li>
<li>description - (Optional) description of the new disk</li>
<li>size - (Required) size of the disk in bytes</li>
<li>vdc - (Required) name of the virutal data center</li>
<li>bus_type - (Optional) bus type of the disk</li>
<li>bus_sub_type - (Optional) bus subtype of the disk</li>
<li>storage_profile - (Optional) name of an existing storage profile to be used by the new disk</li>
<li>iops - (Optional) iops requirement of the disk</li>
<li>state == "present" (Required) to create org</li>
</ul>
<li>
<h5>Update Disk</h5>
</li>
<pre>
<code>
 - name: update disk
   vcd_disk:
	disk_name: "test_disk"
	new_disk_name: "test_disk_1"
	new_size: "200"
	vdc: "Test_VDC"
	state: "update"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>disk_name - (Required) name of the existing disk</li>
<li>vdc - (Required) name of the virtual data center</li>
<li>disk_id - (Optional) id of the existing disk</li>
<li>new_disk_name - (Optional) new name of the disk</li>
<li>new_size - (Optional) new size of the disk</li>
<li>new_description - (Optional) new description of the disk</li>
<li>new_storage_profile - (Optional) new storage profile that the disk will be moved to</li>
<li>new_iops - (Optional) new iops requirement of the disk</li>
<li>state == "update" (Required) to update org</li>
</ul>
<li>
<h5>Delete Disk</h5>
</li>
<pre>
<code>
 - name: delete disk
   vcd_disk:
	disk_name: "test_disk"
	vdc: "Test_VDC"
	state: "absent"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>disk_name - (Required) name of the disk to delete</li>
<li>disk_id - (Optional) id of the disk to delete</li>
<li>vdc - (Required) name of the virtual datacenter</li>
<li>state == "absent" (Required) to create org</li>
</ul>
</ul>
</ol>
</div>
<!--				  -->
<!-- Org Use Case -->
<div class="org-usage col-12" id="org-usage">
<h2>Org Example Usage</h2>
<hr />
<ol>
 <li>
 <h3>Org States</h3>
 </li>
 <ul>
 <li>
 <h5>Create Org</h5>
 </li>
 <pre>
 <code>
 - name: create org
   vcd_org:
	org_name: "test_org"
	full_name: "test_org"
	is_enabled : "false"
	state: "present"
 </code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>org_name - (Required) name of the organization</li>
<li>full_name - (Required) full name of the organization</li>
<li>is_enabled - (Optional) enable organization if true. The default value is false</li>
<li>state == "present" (Required) to create org</li>
</ul>
<li>
<h5>Update Org</h5>
</li>
<pre>
<code>
 - name: update org
   vcd_org:
	org_name: "test_org"
	is_enabled: "true"
	state: "update"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>org_name - (Required) name of the organization</li>
<li>is_enabled - (Required) enable organization if true. The default value is false</li>
<li>state == "update" (Required) to update org</li>
</ul>
<li>
<h5>Delete Org</h5>
</li>
<pre>
<code>
 - name: delete org
   vcd_org:
	org_name: "test_org"
	force: "true"
	recursive: "true"
	state: "absent"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>org_name - (Required) name of the organization</li>
<li>force - (Optional) force=true along with recursive=true to remove
an organization and any objects it contains, regardless of their state. The default value is None</li>
<li>recursive - (Optional) recursive=true to remove an organization
and any objects it contains that are in a state that normally allows removal. The default value is None</li>
<li>state == "absent" (Required) to delete org</li>
</ul>
</ul>
<li>
<h3>Org Operations</h3>
</li>
<ul>
<li>
<h5>Read Org</h5>
</li>
<pre>
<code>
 - name: read org
   vcd_org:
	org_name: "test_org"
	operation: "read"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>org_name - (Required) name of the organization</li>
<li>operation == "read" (Required) to read organization</li>
</ul>
<li>
<h5>Add Rights</h5>
</li>
<pre>
<code>
 - name: add rights to org
   vcd_org:
	org_name: "test_org"
	org_rights:
	  - test_right_1
	  - test_right_2
	operation: "add_rights"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>org_name - (Required) name of the organization</li>
<li>org_rights - (Required) list of rights to be added to an organization</li>
<li>operation == "add_rights" (Required) to add rights to the organization</li>
</ul>
<li>
<h5>Remove Rights</h5>
</li>
<pre>
<code>
 - name: remove rights from org
   vcd_org:
	org_name: "test_org"
	org_rights:
	  - test_right_1
	  - test_right_2
	operation: "remove_rights"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>org_name - (Required) name of the organization</li>
<li>org_rights - (Required) list of rights to be remove to an organization</li>
<li>operation == "remove_rights" (Required) to remove rights from the organization</li>
</ul>
<li>
<h5>List Rights</h5>
</li>
<pre>
<code>
 - name: list org rights
   vcd_org:
	org_name: "test_org"
	operation: "list_rights"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>org_name - (Required) name of the organization</li>
<li>operation == "list_rights" (Required) to list available rights of the organization</li>
</ul>
<li>
<h5>List Roles</h5>
</li>
<pre>
<code>
 - name: list org roles
   vcd_org:
	org_name: "test_org"
	operation: "list_roles"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>org_name - (Required) name of the organization</li>
<li>operation == "list_roles" (Required) to list available roles of the organization</li>
</ul>
</ul>
</ol>
</div>
<!--				  -->
<!-- Org VDC Use Case -->
<div class="org-vdc-usage col-12" id="org-vdc-usage">
<h2>Org VDC Example Usage</h2>
<hr />
<ol>
<li>
<h3>Org VDC States</h3>
<ul>
<li>
<h5>Create Org VDC</h5>
</li>
<pre>
<code>
 - name: create vdc
   vcd_org_vdc:
	vdc_name: test_vdc
	vdc_org_name: test_org
	provider_vdc_name: test_provider_vdc
	description: test vdc description
	allocation_model: AllocationVApp
	is_enabled: false
	storage_profiles:
	- name: Performance
          enabled: true
          units: "MB"
          limit: 50000
          default: true
	cpu_units : MHz
	cpu_allocated : 0
	cpu_limit : 0
	mem_units : 'MB'
	mem_allocated : 0
	mem_limit : 0
	nic_quota : 0
	network_quota : 0
	vm_quota : 0
	resource_guaranteed_memory : 1.0
	resource_guaranteed_cpu : 1.0
	vcpu_in_mhz : 1024
	is_thin_provision : true
	network_pool_name : test_network_pool
	uses_fast_provisioning : false
	over_commit_allowed : false
	vm_discovery_enabled : true
	state: "present"

</code>
</pre>
<h5>Argument Reference</h5>
<ul>
<li>user - (Optional) - vCloud Director user name</li>
<li>password - (Optional) - vCloud Director password</li>
<li>org - (Optional) - vCloud Director org name to log into</li>
<li>host - (Optional) - vCloud Director host name</li>
<li>api_version - (Optional) - Pyvcloud API version</li>
<li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vdc_name - name of the new org vdc</li>
<li>vdc_org_name - associated organization name with the new vdc</li> 
<li>provider_vdc_name - The name of an existing provider vdc</li>
<li>description - description of the new org vdc</li>
<li>allocation_model - allocation model used by this vdc. Accepted values are 'AllocationVApp', 'AllocationPool' or 'ReservationPool'</li>
<li>cpu_units - unit for compute capacity allocated to this vdc. Accepted values are 'MHz' or 'GHz'. Default value is 'MHz'</li>
<li>cpu_allocated - capacity that is committed to be available. Default value is 1</li>
<li>cpu_limit - capacity limit relative to the value specified for allocation. Default value is 1</li>
<li>mem_units - unit for memory capacity allocated to this vdc. Acceptable values are 'MB' or 'GB'. Default value is 'MB'</li>
<li>mem_allocated - memory capacity that is committed to be available.. Default value is 1</li>
<li>mem_limit - memory capacity limit relative to the value specified for allocation. Default value is 1</li>
<li>nic_quota - maximum number of virtual NICs allowed in this vdc. Defaults to 0, which specifies an unlimited number</li>
<li>network_quota - maximum number of network objects that can be deployed in this vdc. Defaults to 0, which means no networks can be deployed</li>
<li>vm_quota - maximum number of VMs that can be created in this vdc. Defaults to 0, which specifies an unlimited number</li>
<li>storage_profiles - list of provider vdc storage profiles to add to this vdc. Each item is a dictionary that should include the following elements:</li>
	    <ul>
            <li>name - name of the PVDC storage profile</li>
            <li>enabled - true/false, true if the storage profile is enabled for this vdc else false</li>
            <li>units - Units used to define limit. One of MB or GB</li>
            <li>limit - Max number of units allocated for this storage profile</li>
            <li>default - true/false, true if this is default storage profile for this vdc else false</li>
	    </ul>
<li>resource_guaranteed_memory - percentage of allocated CPU
            resources guaranteed to vApps deployed in this vdc. Value defaults
            to 1.0 if the element is empty</li>
<li>resource_guaranteed_cpu - percentage of allocated memory
            resources guaranteed to vApps deployed in this vdc. Value defaults
            to 1.0 if the element is empty</li>
<li>vcpu_in_mhz - specifies the clock frequency, in MegaHertz,
            for any virtual CPU that is allocated to a VM</li>
<li>is_thin_provision - true/false, true to request thin provisioning else false</li>
<li>network_pool_name - name to a network pool in the provider
            vdc that this org vdc should use</li>
<li>uses_fast_provisioning - true/false, true to request fast provisioning else false</li>
<li>over_commit_allowed - true/false, false to disallow creation of the VDC
            if the AllocationModel is AllocationPool or ReservationPool and the
            ComputeCapacity specified is greater than what the backing provider
            VDC can supply. Defaults to true, if empty or missing</li>
<li>vm_discovery_enabled - true/false, true if discovery of vCenter VMs
            is enabled for resource pools backing this vdc else false</li>
<li>is_enabled - true/false, true if this vdc is enabled for use by the
            organization users else false. The default value is true</li>
 <li>state == "present" to create org vdc</li>
 </ul>
 <li>
 <h5>Update Org VDC</h5>
 </li>
 <pre>
 <code>
 - name: update vdc
   vcd_org_vdc:
	vdc_name: "test_vdc"
	vdc_org_name: test_org
	is_enabled: "true"
	state: "update"
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>vdc_name - Name of the vdc</li>
 <li>vdc_org_name - associated organization with vdc</li> 
 <li>is_enabled - To enable/disable the vdc. The default value is true.</li>
 <li>state == "update" (Required) to update vdc</li>
 </ul>
 <li>
 <h5>Delete Org VDC</h5>
 </li>
 <pre>
 <code>
 - name: delete Vdc
   vcd_org_vdc:
	vdc_name: "test_vdc"
	vdc_org_name: test_org
	state: "absent"
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>vdc_name - Name of the vdc</li>
 <li>vdc_org_name - associated organization with vdc</li> 
 <li>state == "absent" (Required) to delete vdc</li>
 </ul>
 </ul>
 </li>
 <li>
 <h3>Org VDC Operations</h3>
 <ul>
 <li>
 <h5>List Org VDC(s)</h5>
 </li>
 <pre>
 <code>
 - name: list_vdcs
   vcd_org_vdc:
   	operation: list_vdcs
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>operation == "list_vdcs" (Required) to list org vdc(s)</li>
</ul>
</ul>
</li>
</ol>
</div>
<!--				  -->
<!-- User Use Case -->
<div class="user-usage col-12" id="user-usage">
<h2>User Example Usage</h2>
 <hr />
 <ol>
 <li>
 <h3>User States</h3>
 </li>
 <ul>
 <li>
 <h5>Create User</h5>
 </li>
 <pre>
 <code>
 - name: create user
   vcd_user:
	username: "test_user"
	userpassword: test_password
	role_name: "Organization Administrator"
	full_username: "test_admin_user"
	description: "admin test user"
	email: "testuser@test.com"
	telephone: "12345678"
	im: "i_m_val"
	is_enabled: "false"
	stored_vm_quota: 5
	deployed_vm_quota: 5
	is_alert_enabled: "true"
	is_external: "false"
	is_default_cached: "false"
	is_group_role: "false"
	alert_email_prefix: "test"
	alert_email: "test@test.com"
	state: "present"
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>username - (Required) The username of the user</li>
 <li>userpassword - (Required) The password of the user (must be at least 6
 characters long)</li>
 <li>role_name - (Required) User role name</li>
 <li>full_username - (Optional) The full name of the user</li>
 <li>description - (Optional) The description for the User</li>
 <li>email - (Optional) The email of the user</li>
 <li>telephone - (Optional) The telephone of the user</li>
 <li>im - (Optional) The im address of the user</li>
 <li>is_enabled - (Optional) true/false Enable user. The default value is false.</li>
 <li>stored_vm_quota - (Optional) The quota of vApps that this user can store. The default value is 0.</li>
 <li>deployed_vm_quota - (Optional) The quota of vApps that this user can deploy concurrently. The default value is 0.</li>
 <li>is_alert_enabled - (Optional) true/false The alert email address. The default value is false.</li>
 <li>is_external - (Optional) true/false Indicates if user is imported from an external source. The default value is false.</li>
 <li>is_default_cached - (Optional) true/false Indicates if user should be cached. The default value is false.</li>
 <li>is_group_role - (Optional) true/false Indicates if the user has a group role. The default value is false.</li>
 <li>alert_email_prefix - (Optional) The string to prepend to the alert message subject line</li>
 <li>alert_email - (Optional) The alert email address</li>
 <li>state == "present" (Required) to create user</li>
</ul>
<li>
<h5>Update User</h5>
</li>
<pre>
 <code>
 - name: update user
   vcd_user:
	username: "test_user"
	is_enabled: "true"
	state: "update"
 </code>
</pre>
<h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>username - (Required) username of the user</li>
 <li>is_enabled - (Required) true/false enable/disable the user</li>
 <li>state == "update" (Required) to update user</li>
</ul>
<li>
<h5>Delete User</h5>
</li>
<pre>
 <code>
 - name: delete user
   vcd_user:
	username: "test_user"
	state: "absent"
 </code>
</pre>
<h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>username - (Required) username of the user</li>
 <li>state == "absent" (Required) to delete user</li>
</ul>
</ul>
</ol>
</div>
<!--				  -->
<!-- Role Use Case -->
<div class="role-usage col-12" id="role-usage">
<h2>Role Example Usage</h2>
 <hr />
 <ol>
 <li>
 <h3>Role States</h3>
 </li>
 <ul>
 <li>
 <h5>Create Role</h5>
 </li>
 <pre>
 <code>
 - name: create role
   vcd_roles:
   	role_name: test_role
   	role_description: test role description
   	role_rights:
   	 - test_right_01
   	 - test_right_02
   	state: present
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>role_name - Name of the new role</li>
 <li>role_description - Description of new role</li>
 <li>role_rights - list of rights attached with role</li>
 <li>state - (Required) "present" to create role</li>
</ul>
<li>
 <h5>Update Role</h5>
 </li>
 <pre>
 <code>
 - name: update role
   vcd_roles:
   	role_name: test_role
   	role_description: test role description
   	role_rights:
   	 - test_right_01
   	 - test_right_02
   	state: update
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>role_name - Name of the role needs to be updated</li>
 <li>role_description - Updated description of role</li>
 <li>role_rights - Updated list of rights attached with role</li>
 <li>state - (Required) "update" to update role</li>
</ul>
<li>
 <h5>Delete Role</h5>
 </li>
 <pre>
 <code>
 - name: delete role
   vcd_roles:
   	role_name: test_role
   	state: absent
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>role_name - Name of role needs to be deleted</li>
 <li>state - (Required) "absent" to delete role</li>
</ul>
</ul>
<li>
<h3>Role Operations</h3>
</li>
<ul>
 <li>
 <h5>List Roles</h5>
 </li>
 <pre>
 <code>
 - name: list roles
   vcd_roles:
   	operation: list_roles
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>operation - (Required) "list_roles" to list all available roles inside logged in organization</li>
</ul>
 <li>
 <h5>List Rights</h5>
 </li>
 <pre>
 <code>
 - name: list rights
   vcd_roles:
   	operation: list_rights
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>operation - (Required) "list_rights" to list all available rights of the logged in organization</li>
</ul>
</ul>
</ol>
</div>
<!--                  -->
<!-- vCD External Network Use Case -->
<div class="external-network-usage col-12" id="external-network-usage">
<h2>vCD External Network Example Usage</h2>
 <hr />
 <ol>
 <li>
 <h3>vCD External Network States</h3>
 </li>
 <ul>
 <li>
 <h5>Create vCD External Network</h5>
 </li>
 <pre>
 <code>
 - name: create vCD external network
   vcd_external_network:
    vc_name: vc.0
    port_group_names:
        - VM Network
    network_name: external-network
    gateway_ip: 10.176.3.253
    netmask: 255.255.0.0
    ip_ranges:
        - 10.176.7.68-10.176.7.69
    state: "present"
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>vc_name - Name of the underlying vCenter</li>
 <li>port_group_names - list of vCenter port groups external network needs to be attached with</li>
 <li>network_name - Name of the new vCD External Network</li>
 <li>gateway_ip - IP address of the gateway</li>
 <li>netmask - Netmask of the gateway</li>
 <li>ip_ranges - list of IP ranges used for static pool allocation in the network</li>
 <li>description - (Optional) Description for vCD External Network</li>
 <li>primary_dns_ip - (Optional) IP address of primary DNS server</li>
 <li>secondary_dns_ip - (Optional) IP address of secondary DNS Server</li>
 <li>dns_suffix - (Optional) DNS suffix</li>
 <li>state - (Required) "present" to create vCD External Network</li>
</ul>
<li>
 <h5>Update vCD external network</h5>
 </li>
 <pre>
 <code>
 - name: update vCD external network
   vcd_external_network:
    network_name: external-network
    description: new-network-description
    new_network_name: new-network
    state: update
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>network_name - Name of the exisiting External Network</li>
 <li>new_network_name - New name of the network</li>
 <li>description - Updated description of network</li>
 <li>state - (Required) "update" to update vCD External Network</li>
</ul>
<li>
 <h5>Delete vCD external network</h5>
 </li>
 <pre>
 <code>
 - name: delete vCD external network
   vcd_external_network:
    network_name: test_role
    state: absent
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>network_name - Name of network to be deleted</li>
 <li>force_delete - (Optional) boolean flag to delete network forcefully</li>
 <li>state - (Required) "absent" to delete role</li>
</ul>
</ul>
<li>
<h3>vCD External Network Operations</h3>
</li>
<ul>
 <li>
 <h5>List External Networks</h5>
 </li>
 <pre>
 <code>
 - name: list vCD External Networks
   vcd_external_network:
    operation: list_networks
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>operation - (Required) "list_networks" to list all available External Networks</li>
</ul>
 <li>
 <h5>Add new Subnet</h5>
 </li>
 <pre>
 <code>
 - name: add subnet to vCD External Network
   vcd_external_network:
    network_name: new-name
    gateway_ip: 10.196.10.253
    netmask: 255.255.0.0
    ip_ranges:
        - 10.196.7.68-10.196.7.69
    operation: add_subnet
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>network_name - Name of the external network</li>
 <li>gateway_ip - IP address of the gateway</li>
 <li>netmask - Netmask of the gateway</li>
 <li>ip_ranges - list of IP ranges used for static pool allocation in the network</li>
 <li>operation - (Required) "add_subnet" to add new subnet to the network</li>
</ul>
 <li>
 <h5>Add new IP Ranges</h5>
 </li>
 <pre>
 <code>
 - name: add new ip ranges to vCD External Network subnet
   vcd_external_network:
    network_name: new-name
    gateway_ip: 10.196.10.253
    ip_ranges:
        - 10.196.7.68-10.196.7.69
    operation: add_ip_ranges
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>network_name - Name of the external network</li>
 <li>gateway_ip - IP address of the gateway</li>
 <li>ip_ranges - list of IP ranges used for static pool allocation in the network</li>
 <li>operation - (Required) "add_ip_ranges" to add new ip ranges to the subnet</li>
</ul>
<li>
 <h5>Modify IP Ranges</h5>
 </li>
 <pre>
 <code>
 - name: modify existing ip ranges inside vCD External Network subnet
   vcd_external_network:
    network_name: new-name
    gateway_ip: 10.196.10.253
    ip_ranges:
        - 10.196.7.68-10.196.7.69
    new_ip_ranges:
        - 10.196.8.68-10.196.8.69
    operation: modify_ip_ranges
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>network_name - Name of the external network</li>
 <li>gateway_ip - IP address of the gateway</li>
 <li>ip_ranges - list of old IP ranges needs to be removed</li>
 <li>new_ip_ranges - list of new IP ranges needs to be added</li>
 <li>operation - (Required) "modify_ip_ranges" to modify ip ranges inside subnet</li>
</ul>
<li>
 <h5>Delete IP Ranges</h5>
 </li>
 <pre>
 <code>
 - name: delete existing ip ranges inside vCD External Network subnet
   vcd_external_network:
    network_name: new-name
    gateway_ip: 10.196.10.253
    ip_ranges:
        - 10.196.8.68-10.196.8.69
    operation: delete_ip_ranges
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>network_name - Name of the external network</li>
 <li>gateway_ip - IP address of the gateway</li>
 <li>ip_ranges - list of IP ranges needs to be removed</li>
 <li>operation - (Required) "delete_ip_ranges" to delete ip ranges inside subnet</li>
</ul>   
 <li>
 <h5>Enable/Disable vCD External Network Subnet</h5>
 </li>
 <pre>
 <code>
 - name: enable vCD External Network subnet
   vcd_external_network:
    network_name: new-name
    gateway_ip: 10.196.10.253
    enable_subnet: True
    operation: enable_subnet
 </code>
 </pre>
 <pre>
 <code>
 - name: disable vCD External Network subnet
   vcd_external_network:
    network_name: new-name
    gateway_ip: 10.196.10.253
    enable_subnet: False
    operation: enable_subnet
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>network_name - Name of the external network</li>
 <li>gateway_ip - IP address of the gateway</li>
 <li>enable_subnet - boolean flag to enable/disable external network subnet</li>
 <li>operation - (Required) "enable_subnet" to enable/disable external network subnet</li>
</ul>    
 <li>
 <h5>Attach vCenter Port Group to vCD External Network</h5>
 </li>
 <pre>
 <code>
 - name: attach port group to vCD External Network
   vcd_external_network:
    vc_name: vc.0
    port_group_names:
        - VM Network
    network_name: new-name
    operation: attach_port_group
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>vc_name - Name of the underlying vCenter</li>
 <li>port_group_names - list of vCenter port groups external network needs to be attached with</li>
 <li>network_name - Name of the external network</li>
 <li>operation - (Required) "attach_port_group" to attach a port group to the external network</li>
</ul>
<li>
<h5>Detach vCenter Port Group to vCD External Network</h5>
</li>
 <pre>
 <code>
 - name: detach port group to vCD External Network
   vcd_external_network:
    vc_name: vc.0
    port_group_names:
        - VM Network
    network_name: new-name
    operation: detach_port_group
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>vc_name - Name of the underlying vCenter</li>
 <li>port_group_names - list of vCenter port groups external network needs to be detached with</li>
 <li>network_name - Name of the external network</li>
 <li>operation - (Required) "detach_port_group" to detach a port group to the external network</li>
</ul>
</ul>
</ol>
</div>

<!--                  -->
<!-- vCD vAPP VM snapshot Use Case -->
<div class="vapp-vm-snapshot-usage col-12" id="vapp-vm-snapshot-usage">
<h2>vApp VM Snapshot Example Usage</h2>
 <hr />
 <ol>
 <li>
 <h3>vApp VM Snapshot States</h3>
 </li>
 <ul>
 <li>
 <h5>Create vApp VM Snapshot</h5>
 </li>
 <pre>
 <code>
 - name: create vApp VM Snapshot
   vcd_vapp_vm_snapshot:
    vdc_name: test_vdc
    vapp_name: test_vapp
    vm_name: test_vm
    state: "present"
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>vdc_name - (Required) - vCloud Director ORG VDC Name</li>
 <li>vapp_name - (Required) - vApp Name which VM is part of</li>
 <li>vm_name - (Required) - Name of Virtual Machine</li>
 <li>snapshot_name - (Optional) - Name of Virtual Machine's snapshot</li>
 <li>mem_snapshot - (Optional) - boolean flag true if snapshot should include Virtual Machine's memory else false</li>
 <li>vm_quiesce - (Optional) - boolean flag true if the file system of the Virtual Machine should be quiesced before the snapshot is created. Requires VMware tools to be installed on the vm else false</li>
 <li>state - (Required) "present" to vCD vApp VM snapshot</li>
</ul>
<li>
 <h5>Delete vApp VM Snapshot</h5>
 </li>
 <pre>
 <code>
 - name: delete vApp VM Snapshot
   vcd_vapp_vm_snapshot:
    vm_name: test_vm
    state: absent
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
<li>vm_name - (Required) - Name of Virtual Machine to delete snapshots of</li>
<li>state - (Required) "absent" to delete vApp VM snapshot</li>
</ul>
<li>
<h3>vApp VM Snapshot Operations</h3>
</li>
<ul>
 <li>
 <h5>Revert vApp VM snapshot</h5>
 </li>
 <pre>
 <code>
 - name: revert vApp VM snapshot
   vcd_vapp_vm_snapshot:
    vm_name: test_vm
    operation: revert
 </code>
 </pre>
 <h5>Argument Reference</h5>
 <ul>
 <li>user - (Optional) - vCloud Director user name</li>
 <li>password - (Optional) - vCloud Director password</li>
 <li>org - (Optional) - vCloud Director org name to log into</li>
 <li>host - (Optional) - vCloud Director host name</li>
 <li>api_version - (Optional) - Pyvcloud API version</li>
 <li>verify_ssl_certs - (Optional) - true to enforce to verify ssl certificate for each requests else false</li>
 <li>vm_name - (Required) - Name of Virtual Machine to revert to the current snapshot</li>
<li>operation - (Required) "revert" to revert vApp VM snapshot</li>
</ul>
</ul>
</ul>
</ol>
</div>

<br />
<hr />
<h5 class="text-center">Hope Docs helped!</h5>

