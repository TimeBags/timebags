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

Associated Signature Containers (ASiC) is a file format defined by
European Telecommunications Standards Institute (ETSI) with the document
ETSI TS 102 918 V1.3.1 (2013-06), a tecnical specifications availbale here:
https://www.etsi.org/deliver/etsi_ts/102900_102999/102918/01.03.01_60/ts_102918v010301p.pdf

The document "specifies the use of container structures for associating
either detached CAdES signatures or detached XAdES signatures or time-stamp
tokens, with one or more signed objects to which they apply."

Time-stamp token formats and methods different from RFC 3161 "could be
considered in future versions".

"The ASiC is a data container holding a set of data objects and associated
signatures using the ZIP format. The ZIP format was chosen as it is used
by many popular container formats and it is natively supported by most
operating systems. Any ASiC container has an internal structure including:
    - a root folder, for all the container content possibly including folders
        reflecting the content structure;
    - a META-INF folder, in the root folder, for metadata about the content,
        including associated signatures."

The TimeBags implementation of an ASiC-S file contains the following objects:
    - mimetype (containing the string "application/vnd.etsi.asic-s+zip")
    - dataobject (a single file with arbitrary name, containing data)
    - META-INF/timestamp.tst (containing a binary TimeStampToken as defined in
        RFC 3161 [3], calculated over the entire binary content of the dataobject)
    - META-INF/timestamp.tst.ots (containing the binary stamp as definded by the
        [OpenTimeStamps](https://opentimestamps.org) format/protocol, calculated
        over the "META-INF/timestamp.tst" file)

Also the archive level comment field in the ZIP header is used to identify the
mimetype with the string "mimetype=application/vnd.etsi.asic-s+zip"
'''

import os.path
import zipfile
import tempfile
import logging
import shutil
import time
from pathlib import Path

import tst
import ots


METAINF_DIR = os.path.join("META-INF", "")
TIMESTAMP = os.path.join("META-INF", "timestamp.tst")
TIMESTAMP_OTS = TIMESTAMP + ".ots"

MIMETYPE = "application/vnd.etsi.asic-s+zip"
ZIPCOMMENT = "mimetype=application/vnd.etsi.asic-s+zip"



def add_missing_items(tmpdir):
    ''' Add missing items to complete ASIC-S '''


    # add mimetype file if missed
    mimetype_pf = os.path.join(tmpdir, "mimetype")
    if not os.path.exists(mimetype_pf):
        with open(mimetype_pf, mode='x') as mimetype_fd:
            mimetype_fd.write(MIMETYPE)

    # add META-INF dir if missed
    if not os.path.isdir(os.path.join(tmpdir, "META-INF")):
        os.makedirs(os.path.join(tmpdir, "META-INF"))



def get_new_name(pathfile):
    ''' Get a new name '''

    # find a name not already used for the new zip
    new_pathfile = pathfile + "_new"
    name_number = 0
    while os.path.exists(new_pathfile):
        # if file exists, then increment number suffix
        name_number += 1
        new_pathfile = new_pathfile + "_" + str(name_number)

    return new_pathfile



def unzip(container, tmpdir):
    ''' unzip container into directory '''

    # extract all from zip preserving date and time
    for item in container.infolist():
        name, date_time = item.filename, item.date_time
        name = os.path.join(tmpdir, name)
        folder = os.path.dirname(name)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(name, mode='wb') as out_item:
            with container.open(item.filename, mode='r') as zip_item:
                out_item.write(zip_item.read())
        date_time = time.mktime(date_time + (0, 0, -1))
        os.utime(name, (date_time, date_time))


def zipdir(new_pathfile, tmpdir):
    ''' zip a directory '''

    with zipfile.ZipFile(new_pathfile, mode='x') as new_zip:
        # set ASIC-S comment
        new_zip.comment = ZIPCOMMENT.encode()
        # zip all files
        for root, _, files in os.walk(tmpdir):
            for leaf in files:
                leaf_pf = os.path.join(root, leaf)
                # remove tmpdir path from name in zip
                leaf_zip = str(Path(leaf_pf).relative_to(tmpdir))
                new_zip.write(leaf_pf, leaf_zip)



class ASiCS():
    ''' Class for managing ASiC-S files '''

    def __init__(self, pathfile):
        ''' Initialize ASiC-S container '''

        self.pathfile = pathfile
        self.valid = False
        self.dataobject = None
        self.mimetype = ""
        # result  = UNKNOWN | INCOMPLETE | PENDING | UPGRADED
        # FIXME: when ots are not upgradable in no way, will be also a CORRUPTED result
        # asic-s  = description string to explain many cases of not valid asic-s
        # dat-tst = (<date_time>, <tsa-url>)
        # *-ots   = ('PENDING', None) | (<block height>, '<merkle-root>')
        self.status = {'result': 'UNKNOWN', 'asic-s': None, 'dat-tst': (None, None),
                       'dat-ots': (None, None), 'tst-ots': (None, None)}

        if not zipfile.is_zipfile(self.pathfile):
            self.status['asic-s'] = "%s is not a zip archive" % self.pathfile
        else:
            self.validate()


    def validate(self):
        ''' Check if file is a valid ASiC-S container '''

        n_dataobject = 0
        dataobject_size = None
        with zipfile.ZipFile(self.pathfile) as container:

            # integrity check
            if container.testzip() is not None:
                self.status['asic-s'] = "%s is not a valid zip archive, " \
                            "it will be encapsulated as a dataobject" % self.pathfile
                logging.debug(self.status['asic-s'])
            else:

                # asic-s validity check
                for item in container.namelist():
                    # mimetype does not count as dataobject
                    if item == "mimetype":
                        with container.open("mimetype", mode='r') as mime_type:
                            self.mimetype = mime_type.read().decode().rstrip('\n')
                        continue

                    # item inside META-INF does not count as dataobject
                    if item.startswith(METAINF_DIR):
                        continue

                    # any other file is a datobject
                    n_dataobject += 1

                    # but asic-s require only one dataobject in root
                    if item == os.path.basename(item) and n_dataobject == 1:
                        # first dataobject in root found
                        self.dataobject = item
                        dataobject_info = container.getinfo(item)
                        dataobject_size = dataobject_info.file_size
                        msg = "dataobject size: %d" % dataobject_size
                        logging.debug(msg)
                        continue

                    # if you are here there are more then one dataobject
                    self.dataobject = None
                    dataobject_size = None

                msg = "n: %d - dataobject: %s - size: %s - mimetype: %s" \
                    % (n_dataobject, self.dataobject, str(dataobject_size), self.mimetype)
                logging.debug(msg)
                if n_dataobject != 1 or self.dataobject is None:
                    # a valid ASiC-S container must have exactly one dataobject
                    # if ASiC-S contains detached signatures or META-INF files
                    # then it is better timestamping the ASiC-S as a dataobject
                    self.status['asic-s'] = "%s encapsulated because has %d dataobjects" \
                                    % (self.pathfile, n_dataobject)
                elif dataobject_size == 0:
                    self.status['asic-s'] = "%s has dataobject '%s' with size == 0" \
                                    % (self.pathfile, self.dataobject)
                elif self.mimetype not in ("", MIMETYPE):
                    # zip files with mimetype other then asic-s should not be modified
                    # but used as dataobject in a fresh asic-s zip file
                    self.status['asic-s'] = "%s encapsulated because mimetype not ASiC-S: %s" \
                                    % (self.pathfile, self.mimetype)
                else:
                    # 1. only one dataobjec; 2. size>0; 3. MIMETYPE absent or asic-s
                    self.valid = True
                    self.status['asic-s'] = "%s is a valid ASiC-S container" % self.pathfile

        logging.info(self.status['asic-s'])



    def add_timestamps(self, tmpdir):
        ''' Add missing items to complete ASIC-S '''


        data_pf = os.path.join(tmpdir, self.dataobject)
        tst_pf = os.path.join(tmpdir, TIMESTAMP)
        data_ots_pf = os.path.join(tmpdir, "META-INF", self.dataobject + ".ots")
        tst_ots_pf = os.path.join(tmpdir, TIMESTAMP + ".ots")

        # add tst
        if not os.path.exists(tst_pf):

            with open(data_pf, mode='rb') as data_object:
                data = data_object.read()

            if len(data) > 0:

                ret = tst.get_token(data)
                if ret is not None:
                    token, date_time, url = ret
                    with open(tst_pf, mode='xb') as tst_fd:
                        tst_fd.write(token)
                    self.status['dat-tst'] = (date_time, url)
                else:
                    msg = "timestamping failed"
                    logging.critical(msg)

            else:
                msg = "Error: can't timestamp an empty dataobject: %s" % self.dataobject
                logging.critical(msg)


        # add data ots
        if not os.path.exists(data_ots_pf):
            if ots.ots_stamp([data_pf], timeout=20):
                self.status['dat-ots'] = ('PENDING', None)
                msg = "Done ots of dataobject"
                logging.debug(msg)
                data_ots_new = os.path.join(tmpdir, self.dataobject + ".ots")
                shutil.move(data_ots_new, data_ots_pf)
            else:
                msg = "Failed ots of dataobject"
                logging.critical(msg)


        # add tst ots
        if os.path.exists(tst_pf):
            # if tst is present then move on adding or upgrading ots
            if not os.path.exists(tst_ots_pf):
                if ots.ots_stamp([tst_pf], timeout=20):
                    self.status['tst-ots'] = ('PENDING', None)
                    msg = "Done ots of tst"
                    logging.debug(msg)
                else:
                    msg = "Failed ots of tst"
                    logging.critical(msg)



    def upgrade_ots(self, tmpdir):
        ''' Upgrade opentimestamps '''


        data_ots_pf = os.path.join(tmpdir, "META-INF", self.dataobject + ".ots")
        data_ots_tmp = os.path.join(tmpdir, self.dataobject + ".ots")
        tst_ots_pf = os.path.join(tmpdir, TIMESTAMP + ".ots")


        # upgrade data ots
        shutil.move(data_ots_pf, data_ots_tmp)
        res, att = ots.ots_upgrade(data_ots_tmp)
        if res == 'UPGRADED':
            self.status['dat-ots'] = (res, att)
            msg = "Upgraded ots of dataobject"
            logging.debug(msg)
        # TODO: elif res == 'CORRUPTED':
        else:
            msg = "Failed ots of dataobject"
            logging.critical(msg)
        shutil.move(data_ots_tmp, data_ots_pf)


        # upgrade tst ots
        res, att = ots.ots_upgrade(tst_ots_pf)
        if res == 'UPGRADED':
            self.status['tst-ots'] = (res, att)
            msg = "Upgraded ots of timestamp"
            logging.debug(msg)
        # TODO: elif res == 'CORRUPTED':
        else:
            msg = "Failed ots of timestamp"
            logging.critical(msg)



    def check_timestamps_status(self, tmpdir):
        ''' Check for timestamps status'''


        tst_pf = os.path.join(tmpdir, TIMESTAMP)
        data_ots_pf = os.path.join(tmpdir, "META-INF", self.dataobject + ".ots")
        tst_ots_pf = os.path.join(tmpdir, TIMESTAMP + ".ots")

        if os.path.exists(tst_pf):

            with open(tst_pf, mode='rb') as tst_fd:
                self.status['dat-tst'] = tst.get_info(tst_fd.read())


        if self.status['result'] in ('UNKNOWN', 'INCOMPLETE'):

            if not os.path.exists(tst_pf) or not os.path.exists(data_ots_pf) \
                or not os.path.exists(tst_ots_pf):
                self.status['result'] = 'INCOMPLETE'
                logging.info('ASIC-S not completed')
            else:
                self.status['result'] = 'PENDING'
                logging.info('ASIC-S completed and pending')


        elif self.status['result'] == 'PENDING' \
                and self.status['dat-ots'][0] == 'UPGRADED' \
                and self.status['tst-ots'][0] == 'UPGRADED':
                # TODO: check if ots corrupted also here
            self.status['result'] = 'UPGRADED'
            logging.info('ASIC-S completed and upgraded')


        elif self.status['result'] == 'UPGRADED':
            # TODO: check for ots verified/corrupted
            pass


    def process_timestamps(self):
        ''' Process asic-s file content looking for timestamps:
            add missing, upgrade/verify what already exists '''

        with tempfile.TemporaryDirectory() as tmpdir:

            with zipfile.ZipFile(self.pathfile, mode='r') as container:

                unzip(container, tmpdir)

                # process to complete asic-s
                add_missing_items(tmpdir)
                self.check_timestamps_status(tmpdir)
                if self.status['result'] == 'INCOMPLETE':
                    self.add_timestamps(tmpdir)
                    self.check_timestamps_status(tmpdir)

                # process to upgrade
                elif self.status['result'] == 'PENDING':
                    self.upgrade_ots(tmpdir)
                    self.check_timestamps_status(tmpdir)

                # process to verify
                elif self.status['result'] == 'UPGRADED':
                    pass
                    # TBE:  Verify tst whenever it is possible.
                    #       Generally I can verify a tst previously generated by others
                    #       only if I have a trusted copy of the certificate of the TSA
                    #       that issued the time stamp token.
                    #       EU QTSP are listed in public lists with their certs.
                    #       A trusted copy of the root CA certificate is needed too.

                new_pathfile = get_new_name(self.pathfile)
                zipdir(new_pathfile, tmpdir)

            # replace old zip with the new one
            shutil.move(new_pathfile, self.pathfile)

        ret = self.status['result']
        msg = "asic.process_timestamps() return value: %s" % ret
        logging.debug(msg)
        return ret
