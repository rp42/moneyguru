# Copyright 2019 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from ..testutil import eq_, with_app

from ..base import TestApp
from ...const import AccountType

# --- Pristine
@with_app(TestApp)
def test_balgraph_yaxis_scaling_works_if_negative(app):
    # The y axis scaling (ymin being "higher" than 0) works when the balance is negative.
    app.add_account()
    app.show_account()
    app.add_entry('01/01/2010', decrease='1000')
    app.drsel.select_next_date_range()
    eq_(app.balgraph.ymax, -900)
    eq_(app.balgraph.ymin, -1100)

class TestTwoLiabilityTransactions:
    def do_setup(self):
        app = TestApp()
        app.drsel.select_month_range()
        app.add_account('Visa', account_type=AccountType.Liability)
        app.show_account()
        app.add_entry('3/1/2008', increase='120.00')
        app.add_entry('5/1/2008', decrease='40.00')
        return app

    @with_app(do_setup)
    def test_graph(self, app):
        expected = [('04/01/2008', '120.00'), ('05/01/2008', '120.00'),
                    ('06/01/2008', '80.00'), ('01/02/2008', '80.00')]
        eq_(app.graph_data(), expected)
        eq_(app.balgraph.title, 'Visa')


class TestForeignAccount:
    def do_setup(self):
        app = TestApp()
        app.add_account('Visa', currency='CAD')
        app.show_account()
        return app

    @with_app(do_setup)
    def test_graph(self, app):
        eq_(app.balgraph.currency, 'CAD')


# ---
class TestTwoAccountsOneTransaction:
    def do_setup(self):
        app = TestApp()
        app.add_account('account1')
        app.add_account('account2')
        app.add_txn('12/01/2010', to='account1', amount='42')
        return app

    @with_app(do_setup)
    def test_show_to_account(self, app):
        # The data shown in the balgraph when showing account1 is accurate. Previously, the balgraph
        # would use data from the *selected* account, not the *shown* account.
        app.ttable.show_to_account()
        app.link_aview()
        # No account is selected now
        eq_(app.graph_data()[0], ('13/01/2010', '42.00'))
        eq_(app.balgraph.title, 'account1')

