#!/usr/bin/env python3
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

from glob import glob
import os
import tempfile
import unittest

import asic
from cli import there_can_be_only_one

class TestAsic(unittest.TestCase):
    ''' Test Asic module '''

    def test_asics_valid(self):
        ''' Test asic-s valid files '''

        print("\nTesting asic-s valid files")
        for filename in sorted(glob(os.path.join("tests", "asics_valid_*.zip"))):
            container = asic.ASiCS(filename)
            print(filename)
            print("- valid: %s" % str(container.valid))
            print("- status: %s" % container.status)
            self.assertTrue(container.valid)


    def test_asics_notvalid(self):
        ''' Test asic-s NOT valid files '''

        print("\nTesting: asic-s NOT valid files")
        for filename in sorted(glob(os.path.join("tests", "asics_notvalid_*.zip"))):
            container = asic.ASiCS(filename)
            print(filename)
            print("- valid: %s" % str(container.valid))
            print("- status: %s" % container.status)
            self.assertFalse(container.valid)


class TestMain(unittest.TestCase):
    ''' Test Main module '''

    def test_m1_tcboo_one(self):
        ''' Test a regular file (Readme.md) as single param '''

        print("\nTesting: one regular file (Readme.md) as single param")
        name = "Readme.md"
        if not os.path.exists(name):
            print("Cannot execute test because file %s does not exist!" % name)
            self.assertFalse(True)
        file_result = there_can_be_only_one([name])
        print("Result of there_can_be_only_one(): %s" % file_result)
        self.assertTrue(file_result == name)

    def test__m2_tcboo_none(self):
        ''' Test a non-existent file as single param '''

        print("\nTesting: non-existent file as single param")
        name = next(tempfile._get_candidate_names())
        if os.path.exists(name):
            print("Cannot execute test because file %s exists!" % name)
            self.assertFalse(True)
        file_result = there_can_be_only_one([name])
        print("Result of there_can_be_only_one(): %s" % file_result)
        self.assertTrue(file_result is None)

    def test_m3_tcboo_dir(self):
        ''' Test a dir (not a regular file) as single param '''

        print("\nTesting: dir as single param")
        name = "tests"
        if not os.path.isdir(name):
            print("Cannot execute test because %s is not a directory!" % name)
            self.assertFalse(True)
        file_result = there_can_be_only_one([name])
        print("Result of there_can_be_only_one(): %s" % file_result)
        self.assertTrue(os.path.exists(file_result))
        # check if the result is a valid asic-s
        container = asic.ASiCS(file_result)
        self.assertTrue(container.valid)
        # cleaning
        os.remove(file_result)

    def test_m4_tcboo_files(self):
        ''' Test a list of files as param '''

        print("\nTesting: list of files as param")
        names = glob(os.path.join("*.py"))
        if len(names) < 2:
            print("Cannot execute test because *.py does not match more then one file!")
            self.assertFalse(True)
        file_result = there_can_be_only_one(names)
        print("Result of there_can_be_only_one(): %s" % file_result)
        self.assertTrue(os.path.exists(file_result))
        # check if the result is a valid asic-s
        container = asic.ASiCS(file_result)
        self.assertTrue(container.valid)
        # cleaning
        os.remove(file_result)


'''
    def tcboo_many(self)
        file_result = there_can_be_only_one(glob(path.join("*.py")))
'''

if __name__ == '__main__':
    unittest.main()

