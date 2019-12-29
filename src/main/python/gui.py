# -*- coding: utf-8 -*-
# Copyright (C) 2019 The TimeBags developers
#
# This file is part of the TimeBags software.
#
# It is subject to the license terms in the LICENSE file
# found in the top-level directory of this distribution.
#
# No part of the TimeBags software, including this file, may be copied,
# modified, propagated, or distributed except according to the terms
# contained in the LICENSE file.

'''
This file belong to [TimeBags Project](https://timebags.org)
'''

import os
import sys

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, \
QVBoxLayout, QFileDialog, QMessageBox

import core


class MyMainWindow(QMainWindow):
    ''' Main Window '''

    def get_save_filename(self):
        ''' Ask for a filename to save new timebag '''

        home = os.path.expanduser("~")
        dialog = QFileDialog(self)
        options = (QFileDialog.DontConfirmOverwrite)
        filename, _ = dialog.getSaveFileName(self, "Choose a new name for your TimeBags",
                                                home, 'Zip File (*.zip)', None, options)
        # check if already exists
        while os.path.exists(filename):
            msg = "File %s already exist!\nPlease use a different name." % filename
            alert = QMessageBox()
            alert.setText(msg)
            alert.exec_()
            filename, _ = dialog.getSaveFileName(self, "Choose a new name for your TimeBags",
                                                home, 'Zip File (*.zip)', None, options)

        # FIXME: This is just an ugly workaround, otherwise dialog does not close...
        #        An experienced Qt5 programmer is welcome!
        msg = "Wait a minute, please..."
        alert = QMessageBox()
        alert.setText(msg)
        alert.exec_()
        return filename


    def select_clicked(self):
        ''' control: Select Button on Main Window clicked'''

        home = os.path.expanduser("~")
        dialog = QFileDialog(self)
        files, _ = dialog.getOpenFileNames(self, None, home)
        if files:
            ret = core.main(files, self.get_save_filename)
            if ret is not None:
                msg = repr(ret)
            else:
                msg = "Some error occurred.\nSee the log file for details."
            alert = QMessageBox()
            alert.setText(msg)
            alert.exec_()


    def central_widget(self):
        ''' construct: Central Widget '''

        c_w = QWidget()
        c_w.resize(200, 10)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("To create or upgrade a TimeBag\n"
                                "just use the button below!"))
        select = QPushButton("Select")
        select.clicked.connect(self.select_clicked)
        layout.addWidget(select)
        layout.setContentsMargins(10, 10, 10, 10)
        c_w.setLayout(layout)
        return c_w




class AppContext(ApplicationContext):
    ''' App Context class '''

    def run(self):
        ''' App execution '''

        window = MyMainWindow()
        version = self.build_settings['version']
        window.setWindowTitle("TimeBags ver. %s" % version)
        window.resize(250, 150)
        window.setCentralWidget(window.central_widget())
        window.show()
        return self.app.exec_()



def main():
    ''' Main '''

    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
