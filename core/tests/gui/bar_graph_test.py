# Copyright 2019 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from ..testutil import eq_, with_app

from ..base import TestApp
from ...const import AccountType

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
        app.add_account('Income', account_type=AccountType.Income)
        app.show_account()
        app.add_entry('01/11/2008', transfer='Checking', increase='42') #sunday
        app.drsel.select_prev_date_range() # oct 2008
        app.add_entry('31/10/2008', transfer='Checking', increase='42')
        # now, the creation of the txn forced a recook. what we want to make sure is that both
        # entries will be in the bar
        eq_(app.bar_graph_data()[0][2], '84.00')


class TestForeignAccount:
    def do_setup(self):
        app = TestApp()
        app.add_account('Visa', account_type=AccountType.Income, currency='CAD')
        app.show_account()
        return app

    @with_app(do_setup)
    def test_graph(self, app):
        eq_(app.bargraph.currency, 'CAD')


class TestSomeIncomeInTheFutureWithRangeOnYearToDate:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2010, 1, 12)
        app = TestApp()
        app.add_account('Checking')
        app.show_account()
        app.add_entry('13/01/2010', transfer='Income', increase='42')
        app.drsel.select_year_to_date_range()
        return app

    @with_app(do_setup)
    def test_bar_graphs_during_ytd_dont_show_future_data(self, app):
        # Unlike all other date ranges, bar charts during YTD don't overflow
        app.show_pview()
        eq_(len(app.pgraph.data), 0)


class TestSomeIncomeTodayAndInTheFuture:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2010, 1, 12)
        app = TestApp()
        app.add_account('Checking')
        app.add_account('Income', account_type=AccountType.Income)
        app.show_account()
        app.add_entry('13/01/2010', transfer='Checking', increase='12')
        app.add_entry('12/01/2010', transfer='Checking', increase='30')
        app.drsel.select_year_range()
        return app

    @with_app(do_setup)
    def test_bar_split_in_two(self, app):
        # when some amounts are in the future, but part of the same bar, the amounts are correctly
        # split in the data point
        eq_(app.bargraph.data[0][2:], (30, 12))


class TestRunningYearWithSomeIncome:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2008, 11, 1)
        app = TestApp()
        app.add_account('Checking')
        app.show_account()
        app.add_entry('11/09/2008', transfer='Income', increase='42')
        app.add_entry('24/09/2008', transfer='Income', increase='44')
        app.drsel.select_running_year_range()
        return app

    @with_app(do_setup)
    def test_data_is_taken_from_shown_account(self, app):
        # Ensure that bargraph's data is taken from shown_account, *not* selected_account
        app.show_tview()
        app.add_txn('23/09/2008', from_='something else', to='Checking', amount='1')
        app.ttable.select([0])
        app.ttable.show_from_account()
        app.link_aview()
        # shown: Income selected: Checking
        eq_(app.bargraph.title, 'Income')
        eq_(app.bar_graph_data()[0][2], '86.00') # *not* 87, like what would show with Checking

    @with_app(do_setup)
    def test_monthly_bars(self, app):
        # with the running year range, the bars are monthly
        app.show_pview()
        eq_(len(app.pgraph.data), 1) # there is only one bar

