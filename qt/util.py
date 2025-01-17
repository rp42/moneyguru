# Copyright 2018 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import io
import logging

from hscommon.util import first

from PyQt5.QtCore import QStandardPaths
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDesktopWidget, QSpacerItem, QSizePolicy, QAction, QHBoxLayout

def moveToScreenCenter(widget):
    frame = widget.frameGeometry()
    frame.moveCenter(QDesktopWidget().availableGeometry().center())
    widget.move(frame.topLeft())

def verticalSpacer(size=None):
    if size:
        return QSpacerItem(1, size, QSizePolicy.Fixed, QSizePolicy.Fixed)
    else:
        return QSpacerItem(1, 1, QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)

def horizontalSpacer(size=None):
    if size:
        return QSpacerItem(size, 1, QSizePolicy.Fixed, QSizePolicy.Fixed)
    else:
        return QSpacerItem(1, 1, QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

def horizontalWrap(widgets):
    """Wrap all widgets in `widgets` in a horizontal layout.

    If, instead of placing a widget in your list, you place an int or None, an horizontal spacer
    with the width corresponding to the int will be placed (0 or None means an expanding spacer).
    """
    layout = QHBoxLayout()
    for widget in widgets:
        if widget is None or isinstance(widget, int):
            layout.addItem(horizontalSpacer(size=widget))
        else:
            layout.addWidget(widget)
    return layout

def createActions(actions, target):
    # actions = [(name, shortcut, icon, desc, func)]
    for name, shortcut, icon, desc, func in actions:
        action = QAction(target)
        if icon:
            action.setIcon(QIcon(QPixmap(':/' + icon)))
        if shortcut:
            action.setShortcut(shortcut)
        action.setText(desc)
        action.triggered.connect(func)
        setattr(target, name, action)

def setAccelKeys(menu):
    actions = menu.actions()
    titles = [a.text() for a in actions]
    available_characters = {c.lower() for s in titles for c in s if c.isalpha()}
    for action in actions:
        text = action.text()
        c = first(c for c in text if c.lower() in available_characters)
        if c is None:
            continue
        i = text.index(c)
        newtext = text[:i] + '&' + text[i:]
        available_characters.remove(c.lower())
        action.setText(newtext)

def getAppData():
    return QStandardPaths.standardLocations(QStandardPaths.DataLocation)[0]

class SysWrapper(io.IOBase):
    def write(self, s):
        if s.strip(): # don't log empty stuff
            logging.warning(s)

def setupQtLogging(level=logging.WARNING):
    log = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

def escapeamp(s):
    # Returns `s` with escaped ampersand (& --> &&). QAction text needs to have & escaped because
    # that character is used to define "accel keys".
    return s.replace('&', '&&')
