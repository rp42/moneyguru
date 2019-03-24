# Copyright 2019 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from calendar import monthrange

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

    # --- Public
    def add_exception(self, date, txn):
        self._inner.add_exception(date, txn)

    def add_global_change(self, date, txn):
        self._inner.add_global_change(date, txn)

    def affected_accounts(self):
        return self._inner.affected_accounts()

    def change(self, **kwargs):
        return self._inner.change(**kwargs)

    def change_globally(self, spawn):
        self._inner.change_globally(spawn)

    def contains_ref(self, ref):
        return self._inner.contains_ref(ref)

    def delete_at(self, date):
        self._inner.delete_at(date)

    def get_spawns(self, end):
        return self._inner.get_spawns(end)

    def reassign_account(self, *args):
        self._inner.reassign_account(*args)

    def replicate(self):
        import copy
        result = copy.copy(self)
        result._inner = self._inner.replicate()
        return result

    def reset_exceptions(self):
        self._inner.reset_exceptions()

    def reset_spawn_cache(self):
        self._inner.reset_spawn_cache()

    # --- Properties
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
