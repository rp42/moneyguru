# Copyright 2019 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from datetime import date

from ..testutil import eq_, with_app

from ...model.currency import Currencies
from ..base import TestApp

class TestPristine:
    def do_setup(self):
        app = TestApp()
        app.drsel.select_month_range()
        return app

    @with_app(do_setup)
    def test_cook_bar_overflow(self, app):
        # When some data is included in a bar that overflows, we must not forget to ensure cooking
        # until the end of the *overflow*, not the end of the date range.
        app.add_account('Checking')
        app.show_account()
        app.add_entry('01/11/2008', transfer='Income', increase='42') #sunday
        app.drsel.select_prev_date_range() # oct 2008
        app.add_entry('31/10/2008', transfer='Income', increase='42')
        app.show_pview()
        # now, the creation of the txn forced a recook. what we want to make sure is that both
        # entries will be in the bar
        eq_(app.pgraph.data[0][2], 84)


class TestIncomesAndExpensesInDifferentAccounts:
    def do_setup(self):
        app = TestApp()
        app.drsel.select_month_range()
        Currencies.get_rates_db().set_CAD_value(date(2008, 7, 1), 'USD', 1.42)
        # in july 2008, the first mondy is the 7th
        app.add_account('asset')
        app.show_account()
        app.add_entry('12/6/2008', transfer='income1', increase='10') # will be ignored
        app.add_entry('3/7/2008', transfer='income1', increase='50') # 1st week
        app.add_entry('5/7/2008', transfer='income1', increase='80')
        app.add_entry('7/7/2008', transfer='income1', increase='90') # 2nd week
        app.add_entry('1/7/2008', transfer='income2', increase='32') # 1st week
        app.add_entry('5/7/2008', transfer='income2', increase='22')
        app.add_entry('15/7/2008', transfer='income2', increase='54') # 3rd week
        app.add_entry('1/7/2008', transfer='expense1', decrease='10 cad')
        app.add_entry('8/7/2008', transfer='expense2', decrease='100') # 2nd week
        app.show_pview()
        app.clear_gui_calls()
        return app

    @with_app(do_setup)
    def test_exclude_account(self, app):
        # excluding an account removes it from the net worth graph
        app.istatement.selected = app.istatement.income[0]
        app.istatement.toggle_excluded()
        # We don't want to test the padding, so we only go for the amounts here
        amounts = [data[2] for data in app.pgraph.data]
        # the mock conversion system is rather hard to predict, but the converted amount for 10 CAD
        # on 1/7/2008 is 7.04 USD
        expected = [32 + 22 - 7.04, -100, 54]
        eq_(amounts, expected)
        app.check_gui_calls(app.pgraph.view, ['refresh'])

    @with_app(do_setup)
    def test_profit_graph(self, app):
        # We don't want to test the padding, so we only go for the amounts here
        amounts = [data[2] for data in app.pgraph.data]
        # the mock conversion system is rather hard to predict, but the converted amount for 10 CAD
        # on 1/7/2008 is 7.04 USD
        expected = [50 + 80 + 32 + 22 - 7.04, 90 - 100, 54]
        eq_(amounts, expected)
        eq_(app.pgraph.title, 'Profit & Loss')
        eq_(app.pgraph.currency, 'USD')

