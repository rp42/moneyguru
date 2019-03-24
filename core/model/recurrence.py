# Copyright 2019 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import datetime
from calendar import monthrange
from itertools import chain

from core.util import nonone, first
from core.trans import tr

from ._ccore import Transaction, inc_date, Recurrence as _Recurrence
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


class DateCounter:
    """Iterates over dates in a regular manner.

    This is an iterator, so once we've created our DateCounter, we simply iterate over it to get our
    dates (we yield ``datetime.date`` instances).

    Sometimes (well, only with ``RepeatType.Weekday``), we have to skip a beat. If, for example, we
    have to return the 5th friday of the month and that our current month doesn't have it, we skip
    it and return the first month to have it. So, sometimes, we can have big gap in between our
    dates.

    :param base_date: Date from which we start our iteration. For weekly repeat types, this date
                      also determines which weekday we're looking for in our next dates. If our base
                      date is the 2nd friday of its month, then we're going to iterate over all 2nd
                      friday of months.
    :type base_date: datetime.date
    :param repeat_type: The type of interval we want to put in between our yielded dates.
    :type repeat_type: :class:`RepeatType`
    :param int repeat_every: Amplitude of the interval to put in between our dates. For example,
                             with a monthly repeat type, ``3`` would mean "every 3 months". For
                             "weekday" types, ``repeat_every`` is also in months.
    :param datetime.date end: Date at which to stop the iteration.

    .. seealso:: :doc:`/forecast`
    """
    def __init__(self, base_date, repeat_type, repeat_every, end):
        self.base_date = base_date
        self.end = end
        self.inccount = 0
        self.repeat_type = repeat_type
        self.incsize = repeat_every
        self.current_date = None

    def __iter__(self):
        return self

    def __next__(self):
        # It's possible for a DateCounter to be created with an end date smaller than its start
        # date. In this case, simply never yield any date.
        if self.base_date > self.end:
            raise StopIteration()
        if self.current_date is None: # first date of the iteration is base_date
            self.current_date = self.base_date
            return self.current_date
        new_date = None
        while new_date is None:
            self.inccount += self.incsize
            new_date = inc_date(self.base_date, self.repeat_type, self.inccount)
        if new_date <= self.current_date or new_date > self.end:
            raise StopIteration()
        self.current_date = new_date
        return new_date


def _Spawn(ref, recurrence_date, date):
    res = Transaction(
        2, date, ref.description, ref.payee, ref.checkno, None, None)
    #: ``datetime.date``. Date at which the spawn is "supposed to happen", which can be
    #: overridden by the ``date`` argument, if we're in an "exception" situation. We need to
    #: keep track of this date because it's used as a kind of ID (oh, the spawn
    #: ``schedule42@03-04-2014``? Yeah, there's an exception for that one) in the save file.
    res.recurrence_date = recurrence_date
    #: :class:`.Transaction`. Template transaction for our spawn. Most of the time, it's the
    #: same as :attr:`Recurrence.ref`, unless we have an "exception" in our schedule.
    res.ref = ref
    res.change(splits=ref.splits)
    for split in res.splits:
        split.reconciliation_date = None
    res.balance()
    return res


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
        spawn = _Spawn(txn, date, txn.date)
        self._inner.date2exception[date] = spawn

    def add_global_change(self, date, txn):
        spawn = _Spawn(txn, date, txn.date)
        self._inner.date2globalchange[date] = spawn

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
        """Returns the list of transactions spawned by our recurrence.

        We start at :attr:`start_date` and end at ``end``. We have to specify an end to our spawning
        to avoid getting infinite results.

        .. rubric:: End date adjustment

        If a changed date end up being smaller than the "spawn date", it's possible that a spawn
        that should have been spawned for the date range is not spawned. Therefore, we always
        spawn at least until the date of the last exception. For global changes, it's even more
        complicated. If the global date delta is negative enough, we can end up with a spawn that
        doesn't go far enough, so we must adjust our max date by this delta.

        :param datetime.date end: When to stop spawning.
        :rtype: list of :class:`Spawn`
        """
        if self._inner.date2exception:
            end = max(end, max(self._inner.date2exception.keys()))
        if self._inner.date2globalchange:
            min_date_delta = min(ref.date-date for date, ref in self._inner.date2globalchange.items())
            if min_date_delta < datetime.timedelta(days=0):
                end += -min_date_delta
        end = min(end, nonone(self.stop_date, datetime.date.max))

        date_counter = DateCounter(self.start_date, self.repeat_type, self.repeat_every, end)
        result = []
        global_date_delta = datetime.timedelta(days=0)
        current_ref = self._inner.ref
        for current_date in date_counter:
            if current_date in self._inner.date2globalchange:
                current_ref = self._inner.date2globalchange[current_date]
                global_date_delta = current_ref.date - current_date
            if current_date in self._inner.date2exception:
                exception = self._inner.date2exception[current_date]
                if exception is not None:
                    result.append(exception)
            else:
                if current_date not in self._inner.date2instances:
                    spawn = _Spawn(current_ref, current_date, current_date)
                    if global_date_delta:
                        # Only muck with spawn.date if we have a delta. otherwise we're breaking
                        # budgets.
                        spawn.date = current_date + global_date_delta
                    self._inner.date2instances[current_date] = spawn
                result.append(self._inner.date2instances[current_date])
        return result

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
