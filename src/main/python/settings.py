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
Global settings
'''
import os
import ctypes
import tsa_keystore


def tsa_yaml():
    ''' Get the TSA configuration filename '''

    return os.path.join(path_tsa_dir(), "tsa.yaml")

def freetsa_pem():
    ''' Get the FreeTSA certificate filename '''

    return os.path.join(path_tsa_dir(), "freetsa.pem")

def path_conf_dir():
    ''' Get the conf dir full pathname '''

    home = os.path.expanduser("~")
    prefix = '.' if os.name != 'nt' else ''
    return os.path.join(home, prefix + "timebags")


def path_tsa_dir():
    ''' Get the tsa dir full pathname '''

    return os.path.join(path_conf_dir(), 'tsa')


def init():
    ''' Initializing env and global vars '''

    conf_dir = path_conf_dir()

    # check/create conf dir
    if not os.path.exists(conf_dir):
        os.mkdir(conf_dir)
        if os.name == 'nt':
            if not ctypes.windll.kernel32.SetFileAttributesW(conf_dir, 0x02):
                raise ctypes.WinError()

    if not os.path.isdir(conf_dir):
        error = "unable to use configuration dir: " % conf_dir
        raise Exception(error)

    # check/create tsa files
    tsa_dir = path_tsa_dir()
    if not os.path.exists(tsa_dir):
        os.makedirs(path_tsa_dir())
        tsa_keystore.create_tsa_yaml(tsa_yaml())
        tsa_keystore.create_freetsa_pem(freetsa_pem())
