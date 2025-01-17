# Copyright 2018 Virgil Dupras
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSizePolicy, QSpacerItem, QPushButton
)

from hscommon.trans import trget
from hscommon.plat import ISWINDOWS

from .panel import Panel
from .selectable_list import ComboboxModel

tr = trget('ui')

class AccountReassignPanel(Panel):
    PERSISTENT_NAME = 'accountReassignPanel'

    def __init__(self, model, mainwindow):
        Panel.__init__(self, mainwindow)
        self._setupUi()
        self.model = model
        self.accountComboBox = ComboboxModel(model=self.model.account_list, view=self.accountComboBoxView)

        self.continueButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def _setupUi(self):
        if ISWINDOWS:
            self.resize(250, 140)
        else:
            self.resize(340, 165)
        self.setWindowTitle(tr("Re-assign Account"))
        self.verticalLayout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setText(tr(
            "You\'re about to delete a non-empty account. Select an account to re-assign its "
            "transactions to."
        ))
        self.verticalLayout.addWidget(self.label)
        self.accountComboBoxView = QComboBox(self)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.accountComboBoxView.sizePolicy().hasHeightForWidth())
        self.accountComboBoxView.setSizePolicy(sizePolicy)
        self.accountComboBoxView.setMinimumSize(QSize(200, 0))
        self.verticalLayout.addWidget(self.accountComboBoxView)
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QHBoxLayout()
        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.cancelButton = QPushButton(self)
        self.cancelButton.setText(tr("Cancel"))
        self.cancelButton.setShortcut("Esc")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.continueButton = QPushButton(self)
        self.continueButton.setDefault(True)
        self.continueButton.setText(tr("Continue"))
        self.horizontalLayout.addWidget(self.continueButton)
        self.verticalLayout.addLayout(self.horizontalLayout)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QDialog
    app = QApplication([])
    dialog = QDialog(None)
    AccountReassignPanel._setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())
