Client view vs admin panel
==========================

There are two main parts of the site that are used to manage data: the **client view** and the **admin panel**.

There are some things that can only be accomplished within the client view, and others that can only be accomplished in the admin panel.

Client view
-----------

The client view is what end-users will see. This design is geared towards gardeners and pickers. It is the default view that will show when visiting the GardenHub app. In the client view, **people can only see plots and gardens they are assigned to**, even if they are an administrator. This is by design. Administrators are treated just like any other user in this view with no special capabilities.

The client view is the only place that users can invite other users to GardenHub via email.

.. image:: /_static/client.png

Admin panel
-----------

The admin panel is a tool for directly editing data in GardenHub's database. You can use this to manually create users, manage gardens and plots, and edit the master list of crops. Administrators can access the entire site's database through this view, regardless of whether they're assigned to those gardens or plots.

.. image:: /_static/admin-panel.png

The admin panel can be accessed by first logging into GardenHub, then going under your user dropdown in the top navigation and clicking "Admin". Note that only superusers and staff members can access the admin panel.

.. image:: /_static/admin-button.png
