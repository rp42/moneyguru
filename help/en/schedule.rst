Schedules
=========

Some transactions happen in a regular manner, like salaries, utility bills,
rent, loan payment, etc.. These are fit for **schedules**.

How it works
------------

Schedules work with a system of "occurrences". When you create a schedule (in
the Schedules view), you create a "master" transaction. From this master
transaction, occurrences will be created at regular intervals (which you define
in your master transaction) and will be shown in the Transactions and Account
views.

Schedule occurrences can be directly edited from the Transactions and Account
views. When you modify such an occurrence, moneyGuru asks you for the scope of
your modification. You can either modify just one occurrence (if, for example,
a loan payment was exceptionally higher once), or you can choose to give a
global scope to your modification, that is, affecting all future occurrences
(if, for example, your rent was raised).

When you modify a master schedule, these changes affect all occurrences,
*except* for occurrences you manually edited.

Creating a schedule
-------------------

To create a scheduled transaction, go the the Schedules view and click on the
New Item button. A Schedule Info panel will pop up. This panel is similar to
the Transaction Info panel, but has a few extra fields: Repeat Type, Repeat
Every and Stop Date. The Repeat type field determines what kind of interval you
want (daily, weekly, etc..). The Repeat Every field is to tell how many of that
interval type you want between each occurrences. For example, if you want a
bi-weekly schedule, you would set the Repeat Type to Weekly, and the Repeat
Every to 2.

If you already have a "model transaction" from which you want a schedule to be
created, there's a shortcut for this in the menu called Make Schedule From
Selected. This will create a new schedule and copy all info from the selected
transaction to populate it.

When you create a scheduled transaction, all future occurrences of that
schedule for the current date range will be displayed with a little |clock|
next to them indicating that they are scheduled.

Editing a schedule
------------------

In addition to being able to edit your schedules through the Schedules view,
you can also edit *any occurrence of it* in the Transactions or Account view!
These occurrences can be edited like any other transaction, but there are a few
tricks with the Shift key you can do to control the schedule.

* **Editing only one occurrence:** If you change an occurrence like you would
  with a normal transaction, an exception will be created in the schedule. Only
  this occurrence will contain the edition you made.
* **Editing all future occurrences:** Sometimes, you want a schedule to be
  changed from a certain date until the end. To do so, hold Shift when you end
  the edition of the transaction. When you do so, all future occurrences of the
  schedule will be changed.
* **Skip an occurrence:** Planning an unpaid 3 weeks vacation? Just delete the
  future occurrences in your salary's schedule just like you would do with a
  normal transaction.
* **Stop a schedule:** Not all schedules run indefinitely. To stop a schedule
  at a certain date, just select the occurrence just after the last planned
  occurrence and delete it while holding Shift. All future occurrences will be
  removed.

As you can see, the concept is rather simple: You can edit scheduled
transactions like any other transaction, but by holding Shift, the changes you
make affect all future occurrences of the schedule.

**When occurrences happen:** Scheduling transactions is all nice, but they have
to happen at some point. In moneyGuru, they "happen" when the transaction is
reconciled. When you reconcile a scheduled occurrence, it becomes a normal
transaction (it loses its |clock| and it can't be used to change future
occurrences of the schedule anymore). We call this "materializing" an
occurrence.

Editing an occurrence and selecting the "Just this one" option in the scope
dialog also materializes it.

If you want to quickly materialize an occurrence without having to make changes
to it, press return twice (once to start editing and once to stop editing right
away) while the occurrence is selected. This only work for occurrences in the
past.

.. |clock| image:: image/clock.png
