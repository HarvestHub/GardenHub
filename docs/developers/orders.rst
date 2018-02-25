Order states
============

Orders are often queried by one of more possible states they can be in. Below is a chart of all the possible states.

==========  ======  =======  ========  ================  ========
State:      open    closed   upcoming  active            inactive
==========  ======  =======  ========  ================  ========
start date  Any     Past     Future    Up through today  Future
end date    Future  Past     Future    Today forward     Past
canceled    No      Coerced  No        No                Coerced
comparison  and     and      and       and               or
==========  ======  =======  ========  ================  ========

**Legend:**

* **canceled = No** means that if the order is canceled it *cannot* be this state.
* **canceled = Coerced** means that the order will automatically be in this state by virtue of the fact it is canceled.
* **comparison** describes how the start date and end date of the order are compared. For instance, an open order can have any start date **and** an end date in the future. An inactive order can have a start date in the future **or** an end date in the past.

QuerySet filtering
------------------

Corresponding to the table above, orders have custom QuerySet functions for each of the states. For instance, ``Order.objects.open()`` or ``Order.objects.active()``.
