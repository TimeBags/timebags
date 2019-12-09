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
import tst
import ots


METAINF_DIR = os.path.join("META-INF", "")
TIMESTAMP = os.path.join("META-INF", "timestamp.tst")
TIMESTAMP_OTS = TIMESTAMP + ".ots"

MIMETYPE = "application/vnd.etsi.asic-s+zip"
ZIPCOMMENT = "mimetype=application/vnd.etsi.asic-s+zip"

class ASiCS():
    ''' Class for managing ASiC-S files '''

    def __init__(self, pathfile):
        ''' Initialize ASiC-S container '''

        self.pathfile = pathfile
        self.valid = False
        self.dataobject = None
        self.mimetype = ""
        # TST values: None | (<date>, <verified>)
        # OTS values: None | ('Pending', None) | ('BTC:<block height>', <verified>)
        self.status = {'result': None, 'asic-s': None, 'dat-tst': None,
                       'dat-ots': None, 'tst-ots': None}

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


    def complete(self):
        '''  Complete an ASiC-S file '''

        with zipfile.ZipFile(self.pathfile, mode='a') as container:

            # Add mimetype labels to ASiC-S file only if are missed
            if "mimetype" not in container.namelist():
                container.writestr("mimetype", MIMETYPE)
            if not container.comment:
                container.comment = ZIPCOMMENT.encode()

            # add tst
            if TIMESTAMP not in container.namelist():

                with container.open(self.dataobject, mode='r') as data_object:
                    data = data_object.read()

                if len(data) > 0:

                    token = tst.get_token(data)
                    if token is not None:
                        container.writestr(TIMESTAMP, token)
                    else:
                        msg = "timestamping failed"
                        logging.critical(msg)

                else:
                    msg = "Error: can't timestamp an empty dataobject: %s" % self.dataobject
                    logging.critical(msg)

            # TBD:  Verify tst whenever it is possible.
            #       Generally I can verify a tst previously generated by others
            #       only if I have a trusted copy of the certificate of the TSA
            #       that issued the time stamp token.
            #       EU QTSP are listed in public lists with their certs.
            #       A trusted copy of the root CA certificate is needed too.

            dataobject_ots = os.path.join("META-INF", self.dataobject + ".ots")
            if TIMESTAMP in container.namelist():
                # if tst is present then move on adding or upgrading ots
                ots.token(container, self.dataobject, dataobject_ots)
                ots.token(container, TIMESTAMP, TIMESTAMP_OTS)

            result = set((TIMESTAMP, TIMESTAMP_OTS, dataobject_ots)) <= set(container.namelist())
            logging.debug(repr(set((TIMESTAMP, TIMESTAMP_OTS, dataobject_ots))))
            logging.debug(repr(set(container.namelist())))
            logging.debug(result)

        return result





    def process_timestamps(self):
        ''' Process asic-s file content looking for timestamps:
            add missing, upgrade/verify what already exists '''

        with tempfile.TemporaryDirectory() as tmpdir:

            # find a name not already used for the new zip
            new_pathfile = self.pathfile + "_new"
            name_number = 0
            while os.path.exists(new_pathfile):
                # if file exists, then increment number suffix
                name_number += 1
                new_pathfile = new_pathfile + "_" + str(name_number)

            # create new zip in tempdir
            # new_pathfile = os.path.join(tmpdir, "new.zip")

            with zipfile.ZipFile(self.pathfile, mode='r') as container:
                container.extractall(path=tmpdir)
                # apply changes to extracted files
                # TBD: complete
                # TBD: verify/upgrade
                with zipfile.ZipFile(new_pathfile, mode='x') as new_zip:
                    for item in container.infolist():
                        # new_zip.write(item, container.read(item.filename))
                        with open(os.path.join(tmpdir, ), "rb") as new_item:
                            new_zip.write(item, new_item.read())

            # replace old zip with the new
            # shutil.move(new_pathfile, self.pathfile)

        return self.status
