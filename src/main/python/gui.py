# -*- coding: utf-8 -*-
# Copyright (C) 2019 The TimeBags developers
#
# This file is part of the TimeBags software.
#
# It is subject to the license terms in the LICENSE file-
# found in the top-level directory of this distribution.
#
# No part of the Timebags software, including this file, may be copied,
# modified, propagated, or distributed except according to the terms-
# contained in the LICENSE file.

'''
This file belong to [TimeBags Project](https://timebags.org)
'''

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtWidgets import QFileDialog

import sys



def select_clicked():
    ''' control: Select Button on Main Window clicked'''


    dialog = QFileDialog()
    dialog.exec_()

def central_widget():
    ''' construct: Central Widget '''

    cw = QWidget()
    cw.resize(200, 10)
    layout = QVBoxLayout()
    layout.addWidget(QLabel("To create or upgrade a Timebag, just drag files here\n"
                            "or use the button below!"))
    select = QPushButton("Select")
    select.clicked.connect(select_clicked)
    layout.addWidget(select)
    layout.setContentsMargins(10, 10, 10, 10)
    cw.setLayout(layout)
    return cw



def main():
    ''' Main '''

    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = QMainWindow()
    window.resize(250, 150)
    window.setCentralWidget(central_widget())
    window.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)
