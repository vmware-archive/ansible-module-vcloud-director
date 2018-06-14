---

layout: default
---
<!-- Setting Use Case -->
<!--				  -->

<!-- Catalogs Use Case -->
<div class="catalog-usage col-12" id="catalog-usage">
 <h2>Catalogs Example Usage</h2>
 <hr />
 <ol>
 <li>
 <h3>Catalogs States</h3>
 <ul>
 <li>
 <h5>Create Catalogs</h5>
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
 <p>The following arguments are supported</p>
 <ul>
 <li>catalog_name - (Required) Name of the catalog</li>
 <li>description - (Required) Description Text for the catalog</li>
 <li>state == "present" (Required) to create catalogs</li>
 </ul>
 <li>
 <h5>Update Catalogs</h5>
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
 <p>The following arguments are supported</p>
 <ul>
 <li>catalog_name - (Required) Old name of the catalog</li>
 <li>new_catalog_name - (Required) New name of the catalog</li>
 <li>description - (Required) New description text for the catalog</li>
 <li>state == "update" (Required) to update catalogs</li>
 </ul>
 <li>
 <h5>Delete Catalogs</h5>
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
 <p>The following arguments are supported</p>
 <ul>
 <li>catalog_name - (Required) Name of the catalog</li>
 <li>state == "absent" (Required) to delete catalogs</li>
 </ul>
 </ul>
</li>
 <li>
 <h3>Catalogs Operations</h3>
 <ul>
 <li>
 <h5>Share/Unshare Catalogs</h5>
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
 <p>The following arguments are supported</p>
 <ul>
 <li>catalog_name - (Required) Name of the catalog</li>
 <li>shared - (Optional) "true"/"false" to share/unshare the catalog. The default value is "true" for the argument</li>
 <li>state == "operation" (Required) to update catalogs</li>
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
 <h5>Create Users</h5>
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
 <p>The following arguments are supported</p>
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
 <p>The following arguments are supported</p>
 <ul>
 <li>username - (Required) username of the user</li>
 <li>is_enabled - (Required) "true"/"false" enable/disable the user</li>
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
<h5>Arguments Reference</h5>
 <p>The following arguments are supported</p>
 <ul>
 <li>username - (Required) username of the user</li>
 <li>state == "absent" (Required) to update user</li>
</ul>
<!--				  -->
