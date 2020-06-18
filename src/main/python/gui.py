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
from time import sleep

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout,
                             QFileDialog, QMessageBox, QDialog, QDialogButtonBox,
                             QGroupBox, QFormLayout, QAction, QPlainTextEdit,
                             QProgressBar, QSizePolicy)
from PyQt5.QtGui import QFontDatabase, QTextCursor
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

import core
import gplv3

# global condition var accessible to threads (ugly but working)
# pylint: disable=W0603,W0604,C0103
global pathname
pathname = None

class Worker(QObject):
    ''' The worker class doing real job on a dedicated thread '''

    request_pathname = pyqtSignal()
    result = pyqtSignal(dict)
    finished = pyqtSignal()

    @pyqtSlot(list)
    def real_job(self, files):
        ''' get status '''

        ret = core.main(files, self.get_pathname)
        self.result.emit(ret)
        self.finished.emit()

    @pyqtSlot()
    def get_pathname(self):
        ''' get pathname of zip file to save '''

        global pathname
        pathname = None
        self.request_pathname.emit()

        while not pathname: # wait for condition var
            sleep(1)
        return pathname


class WorkDialog(QDialog):
    ''' Dialog to display work and result '''

    send_files = pyqtSignal(list)

    def __init__(self, files):
        super(WorkDialog, self).__init__()

        self.progress = MyProgressBar()
        self.progress.setRange(0, 0)
        self.progress.set_text("Wait a minute, please...")
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        self.button_box.setEnabled(True)
        self.create_groupbox(files)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(self.form_groupbox)
        self.layout.addWidget(self.progress)
        self.setLayout(self.layout)
        self.setWindowTitle("Your TimeBag status")

        # setup thread and worker
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        # signal and slot connections
        self.send_files.connect(self.worker.real_job)
        self.worker.request_pathname.connect(self.get_save_filename)
        self.worker.result.connect(self.update_groupbox)
        self.worker.finished.connect(self.thread.quit)
        self.button_box.accepted.connect(self.accept)

        # start
        self.thread.start()
        self.send_files.emit(files)



    def get_save_filename(self):
        ''' Ask for a filename to save new timebag '''

        # explain to the user what we need
        msg = "Please choose a name for the new TimeBag zip file.\n" \
                "For example: 'timebag.zip'\n"
        alert = QMessageBox()
        alert.setText(msg)
        alert.exec_()

        # get the pathfile name
        home = os.path.expanduser("~")
        dialog = QFileDialog(self)
        # DontConfirmOverwrite because is managed later and rejected
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

        # update label in the groupbox
        self.data['pathfile'].setText(filename)

        # make it visible to worker thread
        global pathname
        pathname = filename


    def create_groupbox(self, files):
        ''' Form to display the result '''

        # set empty data structure
        self.data = dict(pathfile=QLabel(""),
                         result=QLabel(""),
                         tsa=QLabel(""),
                         tst=QLabel(""),
                         btc=QLabel(""))

        # pathfile can be very long
        self.data['pathfile'].setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.data['pathfile'].setMinimumWidth(300)
        self.data['pathfile'].setWordWrap(True)

        # if the selection is single file with zip extension display it
        if len(files) == 1 and files[0].lower().endswith(".zip"):
            self.data['pathfile'].setText(files[0])

        # set groupbox layout
        self.form_groupbox = QGroupBox("Report")
        layout = QFormLayout()
        layout.addRow(QLabel("File:"), self.data['pathfile'])
        layout.addRow(QLabel("Status:"), self.data['result'])
        layout.addRow(QLabel("Time Stamp Authority:"), self.data['tsa'])
        layout.addRow(QLabel("Time Stamped (UTC):"), self.data['tst'])
        layout.addRow(QLabel("Bitcoin Blocks:"), self.data['btc'])
        self.form_groupbox.setLayout(layout)


    @pyqtSlot(dict)
    def update_groupbox(self, status):
        ''' Form to display the result '''

        if status is None:
            msg = "Some error occurred.\nSee the log file for details."
            alert = QMessageBox()
            alert.setText(msg)
            alert.exec_()

        else:
            # get data
            btc_blocks = []
            for attestation in status['dat-ots'][1] + status['tst-ots'][1]:
                btc_blocks += [attestation[0]]
            tsa_url = status['dat-tst'][1]
            tsa = "<a href=\"%s\">%s</a>" % (tsa_url, tsa_url)

            # update displayed data
            self.data['pathfile'].setText(status['pathfile'])
            self.data['result'].setText(status['result'])
            self.data['tsa'].setText(tsa)
            self.data['tsa'].setOpenExternalLinks(True)
            self.data['tst'].setText(str(status['dat-tst'][0]))
            self.data['btc'].setText(repr(sorted(set(btc_blocks))))

        self.layout.removeWidget(self.progress)
        self.progress.deleteLater()
        self.progress = None
        self.layout.addWidget(self.button_box)

class MyProgressBar(QProgressBar):
    """ Progress bar in busy mode with text displayed at the center.
        Credits: https://stackoverflow.com/questions/27564805
    """

    def __init__(self):
        super(MyProgressBar, self).__init__()
        self.setRange(0, 0)
        self._text = None

    def set_text(self, text):
        ''' Set text '''
        self._text = text

    def text(self):
        ''' Get text '''
        return self._text


class AboutDialog(QDialog):
    ''' Dialog to display the about info '''

    def __init__(self, version):
        super(AboutDialog, self).__init__()
        self.create_about_groupbox(version)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.form_groupbox)
        layout.addWidget(button_box)
        self.setLayout(layout)
        self.setWindowTitle("About")


    def create_about_groupbox(self, version):
        ''' Form to display the about info '''

        url = "<a href=\"https://timebags.org\">https://timebags.org</a>"
        url_label = QLabel(url)
        url_label.setOpenExternalLinks(True)
        self.form_groupbox = QGroupBox("TimeBags software informations")
        layout = QFormLayout()
        layout.addRow(QLabel("Website Url:"), url_label)
        layout.addRow(QLabel("Version:"), QLabel(str(version)))
        layout.addRow(QLabel("Copyright:"), QLabel("2019-2020 Emanuele Cisbani"))
        layout.addRow(QLabel("License:"), QLabel("GNU General Public License 3"))
        self.form_groupbox.setLayout(layout)



class LicenseDialog(QDialog):
    ''' Dialog to display the License '''

    def __init__(self):
        super(LicenseDialog, self).__init__()

        self.resize(650, 450)

        license_text = QPlainTextEdit()
        license_text.setReadOnly(True)
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        license_text.setFont(fixed_font)
        license_text.insertPlainText(gplv3.get_txt())
        license_text.moveCursor(QTextCursor.Start)
        license_text.ensureCursorVisible()


        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(license_text)
        layout.addWidget(button_box)
        self.setLayout(layout)
        self.setWindowTitle("License")




class MyMainWindow(QMainWindow):
    ''' Main Window '''

    def __init__(self, version):

        super(MyMainWindow, self).__init__()

        self.resize(350, 100)
        self.setWindowTitle("Put your files in TimeBags!")
        self.setCentralWidget(self.central_widget())
        self.create_menubar()
        self.version = version

    def about_dialog(self):
        ''' display the About Dialog '''
        dialog = AboutDialog(self.version)
        dialog.exec_()

    def create_menubar(self):
        ''' Menu Bar '''

        main_menu = self.menuBar()
        help_menu = main_menu.addMenu('Help')

        about_btn = QAction('About', self)
        about_btn.triggered.connect(self.about_dialog)
        help_menu.addAction(about_btn)

        def license_dialog():
            ''' Display the License Dialog '''
            dialog = LicenseDialog()
            dialog.exec_()

        license_btn = QAction('License', self)
        license_btn.triggered.connect(license_dialog)
        help_menu.addAction(license_btn)

        exit_btn = QAction('Exit', self)
        exit_btn.triggered.connect(self.close)
        help_menu.addAction(exit_btn)


    def select_clicked(self):
        ''' control: Select Button on Main Window clicked'''

        home = os.path.expanduser("~")
        dialog = QFileDialog(self)
        files, _ = dialog.getOpenFileNames(self, None, home)
        if files:
            dialog = WorkDialog(files)
            dialog.exec_()


    def central_widget(self):
        ''' construct: Central Widget '''

        c_w = QWidget()
        c_w.resize(200, 10)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Create or upgrade your TimeBag " +
                                "by clicking on the button below"))
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

        version = self.build_settings['version']
        window = MyMainWindow(version)
        window.show()
        return self.app.exec_()



def main():
    ''' Main '''

    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
