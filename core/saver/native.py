# Copyright 2019 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os.path as op

from ..model._ccore import save_native
from core.util import ensure_folder

def save(filename, document_id, properties, accounts, transactions, schedules):
    ensure_folder(op.dirname(filename))
    return save_native(
        filename, document_id, accounts, transactions, schedules,
        properties['default_currency'], properties['first_weekday'],
        properties['ahead_months'], properties['year_start_month'])
