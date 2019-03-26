# Copyright 2019 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from ..testutil import eq_

from ..base import TestApp
from ...gui.transaction_print import TransactionPrint

# --- Split transaction
def app_split_transaction():
    app = TestApp()
    splits = [
        ('foo', '', '100', ''),
        ('bar', '', '', '100'),
        ('split1', 'some memo', '10', ''),
        ('split2', '', '', '1'),
        ('', '', '', '9'),
    ]
    app.add_txn_with_splits(splits)
    app.add_txn(from_='foo', to='bar', amount='42')
    app.pv = TransactionPrint(app.tview)
    return app

def test_split_count():
    app = app_split_transaction()
    eq_(app.pv.split_count_at_row(0), 5)
    eq_(app.pv.split_count_at_row(1), 2)
    # Instead of crashing, split_count_at_row returns 0 on total row
    eq_(app.pv.split_count_at_row(2), 0)

def test_split_values():
    app = app_split_transaction()
    eq_(app.pv.split_values(0, 2), ('split1', 'some memo', '10.00'))
    eq_(app.pv.split_values(0, 4), ('Unassigned', '', '-9.00'))

