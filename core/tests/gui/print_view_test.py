# Copyright 2019 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from ..testutil import eq_

from ..base import TestApp
from ...gui.print_view import PrintView

def test_attributes_on_april_2009(monkeypatch):
    # We don't bother testing other views, but they're expected to have PRINT_TITLE_FORMAT
    monkeypatch.patch_today(2009, 4, 1)
    app = TestApp()
    app.drsel.select_month_range()
    app.show_tview()
    app.pv = PrintView(app.tview)
    eq_(app.pv.title, 'Transactions from 01/04/2009 to 30/04/2009')

