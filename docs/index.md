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
   hosts: XXXXXXXXXXXX
   environment:
	env_user: XXXXXXXXXXXX
	env_password: XXXXXXXXXXXX
	env_host: XXXXXXXXXXXX
	env_org: XXXXXXXXXXXX
	env_api_version: XXXXXXXXXXXX
	env_verify_ssl_certs: XXXXXXXXXXXX

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
<li>
<h3>Response</h3>
<p>VCD Ansible Modules provide a unanimous response. The response shall contain following properties,</p>
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
<li>catalog_name - (Required) Name of the catalog</li>
<li>description - (Required) Description Text for the catalog</li>
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
 <li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
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
 <li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
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
 <li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
 <li>catalog_name - (Required) Name of the catalog</li>
 <li>shared - (Optional) True/False to share/unshare the catalog. The default value is True for the argument</li>
 <li>state == "operation" (Required) to share/unshare catalog</li>
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
	file_name: "test_item_media.ova"
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
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
	item_name: "test_item"
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
<li>catalog_name - (Required) Name of the catalog</li>
<li>item_name - (Required) Name of the catalog media/ova</li>
<li>vapp_name - (Required) Name of the vApp to capture</li>
<li>vdc_name - (Required) Name of the vdc</li>
<li>description - (Optional) Description of the catalog item</li>
<li>customize_on_instantiate - (Optional) Flag indicating if the vApp to be instantiated from this vApp template can be customized. The default value is False.</li>
<li>overwrite - (Optional) Flag indicating if the item in the catalog has to be overwritten if it already exists. If it doesn't exist, this flag is not used. The default value is False</li>
<li>operation == "capturevapp" (Required) to capture vApp as a template into a catalog</li> 
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
	password: "test_password"
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
<li>vapp_name - (Required) name of the new vApp</li> 
<li>vdc - (Required) name of the vdc</li> 
<li>catalog_name - (Required) name of the catalog</li> 
<li>template_name - (Required) name of the vApp template</li> 
<li>description - (Optional) description of the new vApp. The default value is None.</li> 
<li>network - (Optional) name of a vdc network. When provided, connects the vm to the network. The default value is None.</li> 
<li>fence_mode - (Optional) fence mode. Possible values are pyvcloud.vcd.client.FenceMode.BRIDGED.value and pyvcloud.vcd.client.FenceMode.NAT_ROUTED.value. The default value is pyvcloud.vcd.client.FenceMode.BRIDGED.value.</li> 
<li>ip_allocation_mode - (Optional) ip allocation mode. Acceptable values are 'pool', 'dhcp' and 'manual'. The default value is 'dhcp'.</li> 
<li>deploy - (Optional) if True deploy the vApp after instantiation. The default value is True.</li> 
<li>power_on - (Optional) if True, power on the vApp after instantiation. The default value is True.</li> 
<li>accept_all_eulas - (Optional) True, confirms acceptance of all EULAs in a vApp template. The default value is False.</li> 
<li>memory - (Optional) max memory that can allocated. The default value is None.</li> 
<li>cpu - (Optional) max cpu that can be allocated. The default value is None.</li> 
<li>disk_size - size of the disk(Optional). The default value is None.</li> 
<li>password - (Optional) the administrator password of vm. The default value is None.</li> 
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
<li>vapp_name - (Required) name of the vApp to be deleted</li> 
<li>vdc - (Required) name of the vdc</li> 
<li>force - (Optional) default False. If True, will instruct vcd to force delete the vapp</li>
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
<li>vapp_name - (Required) name of the vApp to be deploy</li> 
<li>vdc - (Required) name of the vdc</li> 
<li>operation == "deploy" (Required) to deploy vapp</li> 
</ul>
</li>
</ul>
</li>
</ol>
</div>
<!--				  -->
<!-- vApp VM Use Case -->
<div class="vapp-vam-usage col-12" id="vapp-vm-usage">
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
<li>vmpassword_reset - (Optional) True, if the administrator password for this vm must be reset after first use</li> 
<li>ip_allocation_mode - (Optional) Name of the ip ip allocation mode. The default value is 'DHCP'.</li> 
<li>power_on - (Optional) True if the vApp should be powered-on at instantiation. The default value is True.</li> 
<li>all_eulas_accepted - (Optional) True confirms acceptance of all EULAs in the vApp.  The default value is None.</li> 
<li>storage_profile - (Optional) name of the storage profile. The default value is None.</li>
<li>network - (Optional) name of the vApp network to connect. If omitted, the vm won't be connected to any network</li>
<li>cust_script - (Optional) script to run on guest customization</li> 
<li>deploy - (Optional) True, if the vApp should be deployed at instantiation.  The default value is True.</li>
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
<li>target_vm_name - (Optional) target vm name</li> 
<li>target_vapp - (Required) name of the target vapp</li> 
<li>source_vdc - (Required) name of the source vdc</li> 
<li>target_vdc - (Required) name of the target vdc</li> 
<li>source_vapp - (Required) name of the sorce vapp</li> 
<li>source_vm_name - (Required) source vm name</li> 
<li>hostname - (Optional) target guest hostname</li> 
<li>vmpassword - (Optional) the administrator password of the vm</li> 
<li>vmpassword_auto - (Optional) if True, auto generate administrator password</li> 
<li>vmpassword_reset - (Optional) True, if the administrator password for this vm must be reset after first use</li> 
<li>ip_allocation_mode - (Optional) Name of the ip ip allocation mode. The default value is 'DHCP'.</li> 
<li>power_on - (Optional) True if the vApp should be powered-on at instantiation. The default value is True.</li> 
<li>all_eulas_accepted - (Optional) True confirms acceptance of all EULAs in the vApp. The default value is None.</li> 
<li>storage_profile - (Optional) name of the storage profile. The default value is None.</li>
<li>network - (Optional) name of the vApp network to connect. If omitted, the vm won't be connected to any network</li>
<li>cust_script - (Optional) script to run on guest customization</li> 
<li>deploy - (Optional) True, if the vApp should be deployed at instantiation. The default value is True.</li>
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
<li>target_vm_name - (Required) name of the target vm</li> 
<li>target_vapp - (Required) name of the target vapp</li>  
<li>target_vdc - (Required) name of the target vdc</li>
<li>virtual_cpus - (Required) number of virtual CPUs to configure on the vm</li>
<li>cores_per_socket - (Optional) number of cores per socket</li>
<li>state == "update" (Required) to update vapp vm memory</li> 
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
<li>target_vm_name - (Required) name of the target vm</li> 
<li>target_vapp - (Required) name of the target vapp</li> 
<li>target_vdc - (Required) name of the target vdc</li>
<li>memory - (Required) number of MB of memory to configure on the vm</li>
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
<li>target_vm_name - (Required) name of the target vm</li> 
<li>target_vapp - (Required) name of the target vapp</li> 
<li>target_vdc - (Required) name of the target vdc</li>
<li>operation == "deploy" (Required) to deploy vapp vm</li> 
</ul>
</li>
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
<li>disk_name - (Required) name of the new disk</li>
<li>description - (Optional) description of the new disk</li>
<li>size - (Required) size of the disk in bytes</li>
<li>vdc - (Required) name of the virutal data center</li>
<li>bus_type - (Optional) bus type of the disk</li>
<li>bus_sub_type - (Optional) bus subtype of the disk</li>
<li>storage_profile_name - (Optional) name of an existing storage profile to be used by the new disk</li>
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
<li>disk_name - (Required) name of the existing disk</li>
<li>vdc - (Required) name of the virtual data center</li>
<li>disk_id - (Optional) id of the existing disk</li>
<li>new_disk_name - (Optional) new name of the disk</li>
<li>new_size - (Optional) new size of the disk</li>
<li>new_description - (Optional) new description of the disk</li>
<li>new_storage_profile_name - (Optional) new storage profile that the disk will be moved to</li>
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
<li>org_name - (Required) name of the organization</li>
<li>full_name - (Required) full name of the organization</li>
<li>is_enabled - (Optional) enable organization if True. The default value is False</li>
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
<li>org_name - (Required) name of the organization</li>
<li>is_enabled - (Optional) enable organization if True. The default value is False</li>
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
<li>org_name - (Required) name of the organization</li>
<li>force - (Optional) force=True along with recursive=True to remove
an organization and any objects it contains, regardless of their state. The default value is None</li>
<li>recursive - (Optional) recursive=True to remove an organization
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
<li>org_name - (Required) name of the organization</li>
<li>operation == "read" (Required) to read organization</li>
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
	vdc_name: "test_vdc"
	provider_vdc_name: "test_provider_vdc"
	description: "test vdc description"
	allocation_model: "AllocationVApp"
	is_enabled: "false"
	storage_profiles: "{
		\"name\" : \"Performance\",
		\"enabled\"  : true,
		\"units\" : \"MB\",
		\"limit\" : 0,
		\"default\"  : true
	}"
	cpu_units : "MHz"
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
	network_pool_name : "test_network_pool"
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
<li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
<li>vdc_name - (Required) name of the new org vdc</li>
<li>provider_vdc_name - (Required) The name of an existing provider vdc</li>
<li>description - (Optional) description of the new org vdc</li>
<li>allocation_model - (Optional) allocation model used by this vdc. Accepted values are 'AllocationVApp', 'AllocationPool' or 'ReservationPool'</li>
<li>cpu_units - (Optional) unit for compute capacity allocated to this vdc. Accepted values are 'MHz' or 'GHz'</li>
<li>cpu_allocated - (Optional) capacity that is committed to be available</li>
<li>cpu_limit - (Optional) capacity limit relative to the value specified for allocation</li>
<li>mem_units - (Optional) unit for memory capacity allocated to this vdc. Acceptable values are 'MB' or 'GB'</li>
<li>mem_allocated - (Optional) memory capacity that is committed to be available</li>
<li>mem_limit - (Optional) memory capacity limit relative to the value specified for allocation</li>
<li>nic_quota - (Optional) maximum number of virtual NICs allowed in this vdc. Defaults to 0, which specifies an unlimited number</li>
<li>network_quota - (Optional) maximum number of network objects that can be deployed in this vdc. Defaults to 0, which means no networks can be deployed</li>
<li>vm_quota - (Optional) maximum number of VMs that can be created in this vdc. Defaults to 0, which specifies an unlimited number</li>
<li>storage_profiles - (Optional) list of provider vdc storage profiles to add to this vdc. Each item is a dictionary that should include the following elements:</li>
	    <ul>
            <li>name - name of the PVDC storage profile</li>
            <li>enabled - True if the storage profile is enabled for this vdc</li>
            <li>units - Units used to define limit. One of MB or GB</li>
            <li>limit - Max number of units allocated for this storage profile</li>
            <li>default - True if this is default storage profile for this vdc</li>
	    </ul>
<li>resource_guaranteed_memory - (Optional) percentage of allocated CPU
            resources guaranteed to vApps deployed in this vdc. Value defaults
            to 1.0 if the element is empty</li>
<li>resource_guaranteed_cpu - (Optional) percentage of allocated memory
            resources guaranteed to vApps deployed in this vdc. Value defaults
            to 1.0 if the element is empty</li>
<li>vcpu_in_mhz - (Optional) specifies the clock frequency, in MegaHertz,
            for any virtual CPU that is allocated to a VM</li>
<li>is_thin_provision - (Optional) True to request thin provisioning</li>
<li>network_pool_name - (Optional) name to a network pool in the provider
            vdc that this org vdc should use</li>
<li>uses_fast_provisioning - (Optional) True to request fast provisioning</li>
<li>over_commit_allowed - (Optional) False to disallow creation of the VDC
            if the AllocationModel is AllocationPool or ReservationPool and the
            ComputeCapacity specified is greater than what the backing provider
            VDC can supply. Defaults to True, if empty or missing</li>
<li>vm_discovery_enabled - (Optional) True, if discovery of vCenter VMs
            is enabled for resource pools backing this vdc</li>
<li>is_enabled - (Optional) True, if this vdc is enabled for use by the
            organization users. The default value is True</li>
 <li>state == "present" (Required) to create org vdc</li>
 </ul>
 <li>
 <h5>Update Org VDC</h5>
 </li>
 <pre>
 <code>
 - name: update vdc
   vcd_org_vdc:
	vdc_name: "test_vdc"
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
 <li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
 <li>vdc_name - (Required) Name of the vdc</li>
 <li>is_enabled - (Required) To enable/disable the vdc. The default value is True.</li>
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
 <li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
 <li>vdc_name - (Required) Name of the vdc</li>
 <li>state == "absent" (Required) to delete vdc</li>
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
 <li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
 <li>username - (Required) The username of the user</li>
 <li>userpassword - (Required) The password of the user (must be at least 6
 characters long)</li>
 <li>role_name - (Required) User role name</li>
 <li>full_username - (Optional) The full name of the user</li>
 <li>description - (Optional) The description for the User</li>
 <li>email - (Optional) The email of the user</li>
 <li>telephone - (Optional) The telephone of the user</li>
 <li>im - (Optional) The im address of the user</li>
 <li>is_enabled - (Optional) True/False Enable user. The default value is False.</li>
 <li>stored_vm_quota - (Optional) The quota of vApps that this user can store. The default value is 0.</li>
 <li>deployed_vm_quota - (Optional) The quota of vApps that this user can deploy concurrently. The default value is 0.</li>
 <li>is_alert_enabled - (Optional) True/False The alert email address. The default value is False.</li>
 <li>is_external - (Optional) True/False Indicates if user is imported from an external source. The default value is False.</li>
 <li>is_default_cached - (Optional) True/False Indicates if user should be cached. The default value is False.</li>
 <li>is_group_role - (Optional) True/False Indicates if the user has a group role. The default value is False.</li>
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
 <li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
 <li>username - (Required) username of the user</li>
 <li>is_enabled - (Required) True/False enable/disable the user</li>
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
 <li>verify_ssl_certs - (Optional) - True to enforce to verify ssl certificate for each requests else False</li>
 <li>username - (Required) username of the user</li>
 <li>state == "absent" (Required) to update user</li>
</ul>
</ul>
</ol>
</div>
