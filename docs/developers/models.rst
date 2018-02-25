Models
======

.. image:: /_static/db-schema.png

Querying objects
----------------

.. automodule:: gardenhub.managers

.. autoclass:: OrderQuerySet
  :members:

  The following fields enable filtering orders via ``Order.objects``. **For
  example,**

  .. code-block:: python

    from gardenhub.models import Order

    # All open orders
    orders = Order.objects.open()

    # All open orders that haven't been picked today
    orders = Order.objects.open().unpicked_today()

.. autoclass:: UserManager
  :members:


Full model reference
--------------------
.. automodule:: gardenhub.models
    :members:
