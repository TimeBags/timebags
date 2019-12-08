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

import os.path
import tempfile
import logging
import otsclient.args


METAINF_DIR = os.path.join("META-INF", "")


def ots_cmd(params):
    ''' Execute ots command '''
    args = otsclient.args.parse_ots_args(params)
    if not hasattr(args, 'cmd_func'):
        args.parser.error('No command specified')

    # FIXME: no return value? cannot handle errors?!
    args.cmd_func(args)


def token(zip_handler, obj_zip, ots_zip):
    ''' Generate or upgrade ots '''

    with tempfile.TemporaryDirectory() as tmpdir:

        # construct ots and obj tmp names
        if obj_zip.startswith(METAINF_DIR):
            # if obj is inside META-INF dir then
            # create META-INF dir also inside temp dir
            os.mkdir(os.path.join(tmpdir, METAINF_DIR))
        # ots in temp dir are in the same dir to be used by ots_cmd
        obj_tmp = os.path.join(tmpdir, obj_zip)
        ots_tmp = obj_tmp + ".ots"

        # extract obj
        msg = "extraxting object to: %s" % obj_tmp
        logging.debug(msg)
        with open(obj_tmp, 'xb') as obj:
            obj.write(zip_handler.read(obj_zip))

        # check for ots existence
        if ots_zip in zip_handler.namelist():
            # if already exist in zipfile then extract it
            with open(ots_tmp, 'xb') as ots_obj:
                ots_obj.write(zip_handler.read(ots_zip))
            # verify automagically upgrade too
            # FIXME: upgrade and catch output
            #ots_cmd(["--no-bitcoin", "verify", ots_tmp])
            # FIXME: update ots
            #zip_handler.delete(ots_zip)
            #zip_handler.write(ots_tmp, ots_zip)
        else:
            # generate it
            ots_cmd(["stamp", "--timeout", "20", obj_tmp])
            # FIXME: check result ots-cli exitcode?
            if os.path.exists(ots_tmp):
                zip_handler.write(ots_tmp, ots_zip)
                msg = "ots %s added as: %s" % (ots_tmp, ots_zip)
                logging.debug(msg)
            else:
                msg = "ots not generated: %s" % ots_tmp
                logging.critical(msg)
