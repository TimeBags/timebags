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

import unittest
import asic
from glob import glob
from os import path

class TestAsic(unittest.TestCase):
    ''' Test Asic module '''

    def test_asics_valid(self):
        ''' Test asic-s valid files '''

        print("asic-s valid files")
        for filename in glob(path.join("tests", "asics_valid_*.zip")):
            container = asic.ASiCS(filename)
            print(filename)
            print("- valid: %s" % str(container.valid))
            print("- status: %s" % container.status)
            self.assertTrue(container.valid)


    def test_asics_notvalid(self):
        ''' Test asic-s NOT valid files '''

        print("asic-s NOT valid files")
        for filename in glob(path.join("tests", "asics_notvalid_*.zip")):
            container = asic.ASiCS(filename)
            print(filename)
            print("- valid: %s" % str(container.valid))
            print("- status: %s" % container.status)
            self.assertFalse(container.valid)

if __name__ == '__main__':
    unittest.main()

