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

    logging.basicConfig(format='%(message)s')

    if args.verbosity == 0:
        logging.root.setLevel(logging.INFO)
    elif args.verbosity > 0:
        logging.root.setLevel(logging.DEBUG)
    elif args.verbosity == -1:
        logging.root.setLevel(logging.WARNING)
    elif args.verbosity < -1:
        logging.root.setLevel(logging.ERROR)

    if not hasattr(args, 'cmd_func'):
        args.parser.error('No command specified')

    # FIXME: cannot handle errors?!
    args.cmd_func(args)


def tokens(zip_handler, dataobject_name, tst_name):
    ''' Generate, upgrade, prune, verify ots '''

    with tempfile.TemporaryDirectory() as tmpdir:
        stamp_list = []
        # extract dataobject
        dataobject_path = os.path.join(tmpdir, dataobject_name)
        msg = "extraxting dataobject to: %s" % dataobject_path
        logging.debug(msg)
        with open(dataobject_path, 'xb') as dataobject:
            dataobject.write(zip_handler.read(dataobject_name))
        # extract tst
        tst_path = os.path.join(tmpdir, os.path.basename(tst_name))
        msg = "extraxting tst to: %s" % tst_path
        logging.debug(msg)
        with open(tst_path, 'xb') as tst:
            tst.write(zip_handler.read(tst_name))

        # ots of dataobject
        zip_ots_dataobject_name = os.path.join("META-INF", dataobject_name + ".ots")
        if zip_ots_dataobject_name in zip_handler.namelist():
            # if exist extract
            with open(dataobject_path + ".ots", 'xb') as ots_dataobject:
                ots_dataobject.write(zip_handler.read(zip_ots_dataobject_name))
            # TODO: upgrade, prune, verify
        else:
            # append to list to generate it
            stamp_list.append(dataobject_path)

        # ots of tst
        ots_tst_name = tst_name + ".ots"
        ots_tst_path = tst_path + ".ots"
        if ots_tst_name in zip_handler.namelist():
            # if exist extract
            with open(ots_tst_path, 'xb') as ots_tst:
                ots_tst.write(zip_handler.read(ots_tst_name))
            # TODO: upgrade, prune, verify
        else:
            # append to list to generate it
            stamp_list.append(tst_path)

        # generate if needed
        if stamp_list:
            stamp_list.insert(0, "stamp")
            logging.info(stamp_list)
            ots_cmd(stamp_list)

        # add into zip what is missing
        if zip_ots_dataobject_name not in zip_handler.namelist():
            zip_handler.write(dataobject_path + ".ots", zip_ots_dataobject_name)
        if ots_tst_name not in zip_handler.namelist():
            zip_handler.write(ots_tst_path, ots_tst_name)



def token(zip_handler, name):
    ''' Generate or upgrade ots '''

    with tempfile.TemporaryDirectory() as tmpdir:
        # extract obj
        obj_path = os.path.join(tmpdir, name)
        msg = "extraxting object to: %s" % obj_path
        logging.debug(msg)
        with open(obj_path, 'xb') as obj:
            obj.write(zip_handler.read(name))

        # ots of obj
        ots_path = obj_path + ".ots"
        if name.startswith(METAINF_DIR):
            ots_name = name + ".ots"
        else:
            ots_name = os.path.join(METAINF_DIR, name + ".ots")
        if ots_name in zip_handler.namelist():
            # if already exist in zipfile then extract it
            with open(ots_path, 'xb') as ots_obj:
                ots_obj.write(zip_handler.read(ots_name))
            ots_cmd(["upgrade", obj_path])
            # FIXME: check result ots-cli exitcode?
            #zip_handler.delete(ots_name)
            #zip_handler.write(ots_path, ots_name)
            # TODO: prune, verify
        else:
            # generate it
            ots_cmd(["stamp", obj_path])
            # FIXME: check result ots-cli exitcode?
            if os.path.exists(ots_path):
                zip_handler.write(ots_path, ots_name)
            else:
                msg = "ots not generated: %s" % ots_path
                logging.critical(msg)
