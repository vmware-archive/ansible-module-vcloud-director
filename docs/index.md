---

layout: default
---
<!-- Setting Use Case -->
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
 <h5>Arguments Reference</h5>
 <p>The following arguments are supported,</p>
 <ul>
 <li>catalog_name - (Required) Name of the catalog</li>
 <li>description - (Required) Description Text for the catalog</li>
 <li>state == "present" (Required) to create catalog</li>
 </ul>
 <h5>Response data</h5>
 <p>The response should contain following properties,</p>
 <ul>
 <li>msg - the success/failure string respective to the resource</li>
 <li>changed - "true" if resource has been modified at the infrastrucutre else "false"
 </li>
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
 <h5>Arguments Reference</h5>
 <p>The following arguments are supported,</p>
 <ul>
 <li>catalog_name - (Required) Old name of the catalog</li>
 <li>new_catalog_name - (Required) New name of the catalog</li>
 <li>description - (Required) New description text for the catalog</li>
 <li>state == "update" (Required) to update catalog</li>
 </ul>
 <h5>Response data</h5>
 <p>The response should contain following properties,</p>
 <ul>
 <li>msg - the success/failure string respective to the resource</li>
 <li>changed - "true" if resource has been modified at the infrastrucutre else "false"
 </li>
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
 <h5>Arguments Reference</h5>
 <p>The following arguments are supported,</p>
 <ul>
 <li>catalog_name - (Required) Name of the catalog</li>
 <li>state == "absent" (Required) to delete catalog</li>
 </ul>
 <h5>Response data</h5>
 <p>The response should contain following properties,</p>
 <ul>
 <li>msg - the success/failure string respective to the resource</li>
 <li>changed - "true" if resource has been modified at the infrastrucutre else "false"
 </li>
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
 <h5>Arguments Reference</h5>
 <p>The following arguments are supported,</p>
 <ul>
 <li>catalog_name - (Required) Name of the catalog</li>
 <li>shared - (Optional) "true"/"false" to share/unshare the catalog. The default value is "true" for the argument</li>
 <li>state == "operation" (Required) to share/unshare catalog</li>
</ul>
<h5>Response data</h5>
<p>The response should contain following properties,</p>
<ul>
<li>msg - the success/failure string respective to the resource</li>
<li>changed - "true" if resource has been modified at the infrastrucutre else "false"
</li>
</ul>
</li>
</ul>
</li>
</ol>
</div>
<!--				  -->

<!-- Catalog Item Use Case -->
<!--				  -->

<!-- vApp Use Case -->
<!--				  -->

<!-- vApp VM Use Case -->
<!--				  -->

<!-- Independent Disk Use Case -->
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
<h5>Arguments Reference</h5>
<p>The following arguments are supported,</p>
<ul>
<li>org_name - (Required) name of the organization</li>
<li>full_name - (Required) full name of the organization</li>
<li>is_enabled - (Optional) enable organization if True, default value will be False</li>
<li>state == "present" (Required) to create org</li>
</ul>
<h5>Response data</h5>
<p>The response should contain following properties,</p>
<ul>
<li>msg - the success/failure string respective to the resource</li>
<li>changed - "true" if resource has been modified at the infrastrucutre else "false"
</li>
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
<h5>Arguments Reference</h5>
<p>The following arguments are supported,</p>
<ul>
<li>org_name - (Required) name of the organization</li>
<li>is_enabled - (Optional) enable organization if True, default value will be None</li>
<li>state == "update" (Required) to update org</li>
</ul>
<h5>Response data</h5>
<p>The response should contain following properties,</p>
<ul>
<li>msg - the success/failure string respective to the resource</li>
<li>changed - "true" if resource has been modified at the infrastrucutre else "false"
</li>
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
<h5>Arguments Reference</h5>
<p>The following arguments are supported,</p>
<ul>
<li>org_name - (Required) name of the organization</li>
<li>force - (Optional) force=True along with recursive=True to remove
an organization and any objects it contains, regardless of their state</li>
<li>recursive - (Optional) recursive=True to remove an organization
and any objects it contains that are in a state that normally allows removal</li>
<li>state == "absent" (Required) to delete org</li>
</ul>
<h5>Response data</h5>
<p>The response should contain following properties,</p>
<ul>
<li>msg - the success/failure string respective to the resource</li>
<li>changed - "true" if resource has been modified at the infrastrucutre else "false"
</li>
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
<h5>Arguments Reference</h5>
<p>The following arguments are supported,</p>
<ul>
<li>org_name - (Required) name of the organization</li>
<li>operation == "read" (Required) to read organization</li>
</ul>
<h5>Response data</h5>
<p>The response should contain following properties,</p>
<ul>
<li>msg - the success/failure string respective to the resource</li>
<li>changed - "true" if resource has been modified at the infrastrucutre else "false"
</li>
</ul>
</ul>
</ol>
</div>
<!--				  -->

<!-- Org VDC Use Case -->
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
 <h5>Arguments Reference</h5>
 <p>The following arguments are supported,</p>
 <ul>
 <li>username - (Required) The username of the user</li>
 <li>userpassword - (Required) The password of the user (must be at least 6
 characters long)</li>
 <li>role_name - (Required) User role name</li>
 <li>full_username - (Required) The full name of the user</li>
 <li>description - (Required) The description for the User</li>
 <li>email - (Required) The email of the user</li>
 <li>telephone - (Required) The telephone of the user</li>
 <li>im - (Required) The im address of the user</li>
 <li>is_enabled - (Required) "true"/"false" Enable user</li>
 <li>stored_vm_quota - (Required) The quota of vApps that this user can store</li>
 <li>deployed_vm_quota - (Required) The quota of vApps that this user can deploy concurrently</li>
 <li>is_alert_enabled - (Required) "true"/"false" The alert email address</li>
 <li>is_external - (Required) "true"/"false" Indicates if user is imported from an external source</li>
 <li>is_default_cached - (Required) "true"/"false" Indicates if user should be cached</li>
 <li>is_group_role - (Required) "true"/"false" Indicates if the user has a group role</li>
 <li>alert_email_prefix - (Required) The string to prepend to the alert message subject line</li>
 <li>alert_email - (Required) The alert email address</li>
 <li>state == "present" (Required) to create user</li>
</ul>
<h5>Response data</h5>
<p>The response should contain following properties,</p>
<ul>
<li>msg - the success/failure string respective to the resource</li>
<li>changed - "true" if resource has been modified at the infrastrucutre else "false"
</li>
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
<h5>Arguments Reference</h5>
 <p>The following arguments are supported,</p>
 <ul>
 <li>username - (Required) username of the user</li>
 <li>is_enabled - (Required) "true"/"false" enable/disable the user</li>
 <li>state == "update" (Required) to update user</li>
</ul>
<h5>Response data</h5>
<p>The response should contain following properties,</p>
<ul>
<li>msg - the success/failure string respective to the resource</li>
<li>changed - "true" if resource has been modified at the infrastrucutre else "false"
</li>
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
<h5>Arguments Reference</h5>
 <p>The following arguments are supported,</p>
 <ul>
 <li>username - (Required) username of the user</li>
 <li>state == "absent" (Required) to update user</li>
</ul>
<h5>Response data</h5>
<p>The response should contain following properties,</p>
<ul>
<li>msg - the success/failure string respective to the resource</li>
<li>changed - "true" if resource has been modified at the infrastrucutre else "false"
</li>
</ul>
<!--				  -->
