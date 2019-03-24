# Copyright 2019 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from calendar import monthrange

from core.util import first
from core.trans import tr

from ._ccore import Recurrence # noqa
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
