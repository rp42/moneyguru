# Copyright 2018 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

import os.path as op

from PyQt5.QtCore import Qt, QSettings, QRect, QObject, pyqtSignal, QLocale
from PyQt5.QtWidgets import QApplication

from hscommon.trans import trget
from hscommon.util import tryint

from core.model.date import clean_format

tr = trget('ui')

def normalize_for_serialization(v):
    # QSettings doesn't consider set/tuple as "native" typs for serialization, so if we don't
    # change them into a list, we get a weird serialized QVariant value which isn't a very
    # "portable" value.
    if isinstance(v, (set, tuple)):
        v = list(v)
    if isinstance(v, list):
        v = [normalize_for_serialization(item) for item in v]
    return v

def adjust_after_deserialization(v):
    # In some cases, when reading from prefs, we end up with strings that are supposed to be
    # bool or int. Convert these.
    if isinstance(v, list):
        return [adjust_after_deserialization(sub) for sub in v]
    if isinstance(v, str):
        # might be bool or int, try them
        if v == 'true':
            return True
        elif v == 'false':
            return False
        else:
            return tryint(v, v)
    return v

# About QRect conversion:
# I think Qt supports putting basic structures like QRect directly in QSettings, but I prefer not
# to rely on it and stay with generic structures.

class PreferencesBase(QObject):
    prefsChanged = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.reset()
        self._settings = QSettings()

    def _load_values(self, settings, get):
        pass

    def get_rect(self, name, default=None):
        r = self.get_value(name, default)
        if r is not None:
            return QRect(*r)
        else:
            return None

    def get_value(self, name, default=None):
        if self._settings.contains(name):
            result = adjust_after_deserialization(self._settings.value(name))
            if result is not None:
                return result
            else:
                # If result is None, but still present in self._settings, it usually means a value
                # like "@Invalid".
                return default
        else:
            return default

    def load(self):
        self.reset()
        self._load_values(self._settings)

    def reset(self):
        pass

    def _save_values(self, settings, set_):
        pass

    def save(self):
        self._save_values(self._settings)
        self._settings.sync()

    def set_rect(self, name, r):
        if isinstance(r, QRect):
            rectAsList = [r.x(), r.y(), r.width(), r.height()]
            self.set_value(name, rectAsList)

    def set_value(self, name, value):
        self._settings.setValue(name, normalize_for_serialization(value))

    def saveGeometry(self, name, widget):
        # We save geometry under a 5-sized int array: first item is a flag for whether the widget
        # is maximized and the other 4 are (x, y, w, h).
        m = 1 if widget.isMaximized() else 0
        r = widget.geometry()
        rectAsList = [r.x(), r.y(), r.width(), r.height()]
        self.set_value(name, [m] + rectAsList)

    def restoreGeometry(self, name, widget):
        l = self.get_value(name)
        if l and len(l) == 5:
            m, x, y, w, h = l
            if m:
                widget.setWindowState(Qt.WindowMaximized)
            else:
                r = QRect(x, y, w, h)
                widget.setGeometry(r)


class Preferences(PreferencesBase):
    def _load_values(self, settings):
        get = self.get_value
        self.recentDocuments = get('RecentDocuments', self.recentDocuments)
        self.recentDocuments = list(filter(op.exists, self.recentDocuments))
        self.dateFormat = get('DateFormat', self.dateFormat)
        self.tableFontSize = get('TableFontSize', self.tableFontSize)
        self.language = get('Language', self.language)
        self.debugMode = get('DebugMode', self.debugMode)

    def reset(self):
        locale = QLocale.system()
        self.recentDocuments = []
        dateFormat = str(locale.dateFormat(QLocale.ShortFormat))
        dateFormat = clean_format(dateFormat)
        self.dateFormat = dateFormat
        self.tableFontSize = QApplication.font().pointSize()
        self.language = ''
        self.debugMode = False

    def _save_values(self, settings):
        set_ = self.set_value
        set_('RecentDocuments', self.recentDocuments)
        set_('DateFormat', self.dateFormat)
        set_('TableFontSize', self.tableFontSize)
        set_('Language', self.language)
        set_('DebugMode', self.debugMode)

