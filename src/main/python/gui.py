# -*- coding: utf-8 -*-
# Copyright (C) 2019 The TimeBags developers
#
# This file is part of the TimeBags software.
#
# It is subject to the license terms in the LICENSE file
# found in the top-level directory of this distribution.
#
# No part of the Timebags software, including this file, may be copied,
# modified, propagated, or distributed except according to the terms
# contained in the LICENSE file.

'''
This file belong to [TimeBags Project](https://timebags.org)
'''

import os
import sys

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, \
QFileDialog, QMessageBox

import core



def get_save_filename():
    ''' Ask for a filename to save new timebag '''

    home = os.path.expanduser("~")
    filename, _ = QFileDialog.getSaveFileName(None, None, home)
    return filename


def select_clicked():
    ''' control: Select Button on Main Window clicked'''

    home = os.path.expanduser("~")
    files, _ = QFileDialog.getOpenFileNames(None, None, home)
    if files:
        ret = core.main(files, get_save_filename())
        if ret is not None:
            msg = repr(ret)
        else:
            msg = "Some error occurred.\nSee the log file for details."
        alert = QMessageBox()
        alert.setText(msg)
        alert.exec_()


def central_widget():
    ''' construct: Central Widget '''

    c_w = QWidget()
    c_w.resize(200, 10)
    layout = QVBoxLayout()
    layout.addWidget(QLabel("To create or upgrade a Timebag, just drag files here\n"
                            "or use the button below!"))
    select = QPushButton("Select")
    select.clicked.connect(select_clicked)
    layout.addWidget(select)
    layout.setContentsMargins(10, 10, 10, 10)
    c_w.setLayout(layout)
    return c_w




class AppContext(ApplicationContext):
    ''' App Context class '''

    def run(self):
        ''' App execution '''

        window = QMainWindow()
        version = self.build_settings['version']
        window.setWindowTitle("Timebags ver. %s" % version)
        window.resize(250, 150)
        window.setCentralWidget(central_widget())
        window.show()
        return self.app.exec_()



def main():
    ''' Main '''

    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
