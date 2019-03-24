# Copyright 2019 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from calendar import monthrange
from itertools import chain

from core.util import first
from core.trans import tr

from ._ccore import Recurrence as _Recurrence
from .date import RepeatType

def find_schedule_of_ref(ref, schedules):
    return first(s for s in schedules if s.contains_ref(ref))

def get_repeat_type_desc(repeat_type, start_date):
    res = {
        RepeatType.Daily: tr('Daily'),
        RepeatType.Weekly: tr('Weekly'),
        RepeatType.Monthly: tr('Monthly'),
        RepeatType.Yearly: tr('Yearly'),
        RepeatType.Weekday: '', # dynamic
        RepeatType.WeekdayLast: '', # dynamic
    }[repeat_type]
    if res:
        return res
    date = start_date
    weekday_name = date.strftime('%A')
    if repeat_type == RepeatType.Weekday:
        week_no = (date.day - 1) // 7
        position = [tr('first'), tr('second'), tr('third'), tr('fourth'), tr('fifth')][week_no]
        return tr('Every %s %s of the month') % (position, weekday_name)
    elif repeat_type == RepeatType.WeekdayLast:
        _, days_in_month = monthrange(date.year, date.month)
        if days_in_month - date.day < 7:
            return tr('Every last %s of the month') % weekday_name
        else:
            return ''


class Recurrence:
    """A recurring transaction (called "Schedule" in the app).

    .. rubric:: Schedule exceptions

    One of the great features of moneyGuru is its ability to easy allow exceptions in its schedule.
    The amount changes one month? No problem, just change it. The transaction happens a day later?
    No problem, change it. From now on, every following transaction is going to happen a day later?
    No problem, hold shift when you commit the change to make it "global".

    All these exceptions, they have to be recorded somewhere. The "one-time" exceptions are kept in
    :attr:`date2exception`. The date used in the mapping is :attr:`Spawn.recurrent_date` because
    when we change the date of an exception, we still want to remember which recurrent date it
    replaces, so we used the date at which the *regular* transaction was supposed to happen.

    There are also the "global" exceptions, which are stored in :attr:`date2globalchange` and work
    kinda like normal exception, except that from the date they first happen, all following spawns
    are going to use this exception as a transaction model. This includes date. That is, if a global
    exception is 3 days later than its :attr:`Spawn.recurrent_date`, then all following spawns are
    going to to be 3 days later.

    Exceptions can override each other. We can be riding on a global exception and, suddenly, a
    newer global or local exception is there! Well, we apply that exception.

    An exception can also be a deletion, that is "oh, this week that transaction didn't happen".
    This is recorded by putting ``None`` in :attr:`date2exception`. When this deletion is done as
    a global change (from this date, this recurrence doesn't happen anymore), we simply set
    :attr:`stop_date`.

    .. seealso:: :class:`DateCounter`

    :param ref: See :attr:`ref`
    :type ref: :class:`.Transaction`
    :param repeat_type: The type of interval we have in between spawns.
    :type repeat_type: :class:`RepeatType`
    :param int repeat_every: The amplitude of that repetition.
    """
    def __init__(self, ref, repeat_type, repeat_every):
        if repeat_type not in RepeatType.ALL:
            # invalid repeat type, default to monthly
            repeat_type = RepeatType.Monthly
        self._inner = _Recurrence(ref, repeat_type, repeat_every)

    def __repr__(self):
        return '<Recurrence %s %d>' % (self.repeat_type, self.repeat_every)

    # --- Private
    def _all_exceptions(self):
        exceptions = chain(
            self._inner.date2exception.values(), self._inner.date2globalchange.values())
        return (e for e in exceptions if e is not None)

    # --- Public
    def add_exception(self, date, txn):
        self._inner.add_exception(date, txn)

    def add_global_change(self, date, txn):
        self._inner.add_global_change(date, txn)

    def affected_accounts(self):
        """Returns a set of all :class:`.Account` affected by the schedule.

        This is pretty much the same as calling
        :meth:`~core.model.transaction.Transaction.affected_accounts` on :attr:`ref`, except that it
        also checks in exception instances to make there there isn't another affected account in
        there.
        """
        result = self._inner.ref.affected_accounts()
        for exception in self._all_exceptions():
            result |= exception.affected_accounts()
        return result

    def change(self, **kwargs):
        return self._inner.change(**kwargs)

    def change_globally(self, spawn):
        """Add a user-modified spawn into the global exceptions list.

        :param spawn: The spawn to add to :attr:`date2globalchange`.
        :type spawn: :class:`.Spawn`
        """
        for date in list(self._inner.date2globalchange.keys()):
            if date >= spawn.recurrence_date:
                del self._inner.date2globalchange[date]
        for date, exception in list(self._inner.date2exception.items()):
            # we don't want to remove local deletions
            if exception is not None and date >= spawn.recurrence_date:
                del self._inner.date2exception[date]
        self._inner.date2globalchange[spawn.recurrence_date] = spawn
        self._inner.update_ref()

    def contains_ref(self, ref):
        if self._inner.ref == ref:
            return True
        if ref in self._inner.date2globalchange.values():
            return True
        if ref in self._inner.date2instances.values():
            return True
        return False

    def delete_at(self, date):
        """Create an exception that prevents further spawn at ``date``."""
        self._inner.date2exception[date] = None
        self._inner.update_ref()

    def get_spawns(self, end):
        return self._inner.get_spawns(end)

    def reassign_account(self, account, reassign_to=None):
        """Reassigns accounts for :attr:`ref` and all exceptions.

        .. seealso:: :meth:`affected_accounts`
                     :meth:`~core.model.transaction.Transaction.reassign_account`
        """
        self._inner.ref.reassign_account(account, reassign_to)
        for exception in self._all_exceptions():
            exception.reassign_account(account, reassign_to)
        self.reset_spawn_cache()

    def replicate(self):
        """Returns a copy of ``self``."""
        result = Recurrence(
            self._inner.ref.replicate(), self.repeat_type, self.repeat_every)
        result.change(stop_date=self.stop_date)
        result._inner.date2exception.update(self._inner.date2exception)
        result._inner.date2globalchange.update(self._inner.date2globalchange)
        return result

    def reset_exceptions(self):
        self._inner.reset_exceptions()

    def reset_spawn_cache(self):
        self._inner.reset_spawn_cache()

    # --- Properties
    @property
    def is_alive(self):
        """Returns whether :meth:`get_spawns` can ever return anything."""
        if self.stop_date is None:
            return True
        return bool(self.get_spawns(self.stop_date))

    @property
    def repeat_every(self):
        """``int``. See :class:`DateCounter`."""
        return self._inner.repeat_every

    @property
    def repeat_type(self):
        """:class:`RepeatType`. See :class:`DateCounter`."""
        return self._inner.repeat_type

    @property
    def start_date(self):
        """``datetime.date``. When our recurrence begins.

        Same as the :attr:`Transaction.date` attribute of :attr:`ref`.
        """
        return self._inner.start_date

    @property
    def stop_date(self):
        return self._inner.stop_date

    @property
    def ref(self):
        return self._inner.ref

    @ref.setter
    def ref(self, value):
        self._inner.ref = value
        self.reset_spawn_cache()
