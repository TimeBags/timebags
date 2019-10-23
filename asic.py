# -*- coding: utf-8 -*-

'''
This file belong to [TimeBags Project](https://timebags.org)

Associated Signature Containers (ASiC) is a file format defined by
European Telecommunications Standards Institute (ETSI) in the document
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
import re
import tst
import ots


TIMESTAMP = os.path.join("META-INF", "timestamp.tst")

class ASiCS():
    ''' Class for managing ASiC-S files '''

    def __init__(self, pathfile):
        ''' Initialize ASiC-S container '''

        self.pathfile = pathfile
        self.valid = False
        self.dataobject = None
        self.status = ""

        # does file exist?
        if not os.path.isfile(self.pathfile):
            self.status = "%s is not a file" % self.pathfile

        # is it a zipfile?
        elif not zipfile.is_zipfile(self.pathfile):
            self.status = "%s is not a zip archive" % self.pathfile
        else:
            self.validate()


    def validate(self):
        ''' Check if file is a valid ASiC-S container '''

        n_dataobject = 0
        with zipfile.ZipFile(self.pathfile) as container:

            # integrity check
            if container.testzip() is not None:
                self.status = "%s is a corrupted zip archive" % self.pathfile
            else:

                # asic-s validity check
                for item in container.namelist():

                    # ignore others meta-info files
                    if re.search('META-INF/.*$', item) is not None:
                    # TODO: test on win this slash "/" or adapt it to the current os
                        pass

                    # mimetype file does not count as a dataobject
                    elif item == "mimetype":
                        pass

                    # count dataobjects
                    else:
                        n_dataobject += 1
                        self.dataobject = item


        # a valid ASiC-S container must have exactly one dataobject
        if n_dataobject != 1:
            self.dataobject = None
            self.valid = False
            self.status = "%s is not ASiC-S because has %d dataobject" \
                            % (self.pathfile, n_dataobject)
        else:
            self.valid = True
            self.status = "%s is a good ASiC-S container!" % self.pathfile


    def update(self):
        '''  Update an ASiC-S file '''

        with zipfile.ZipFile(self.pathfile, mode='a') as container:

            # Add mimetype labels to ASiC-S file only if are missed
            if "mimetype" not in container.namelist():
                container.writestr("mimetype", "application/vnd.etsi.asic-s+zip")
            if not container.comment:
                container.comment = "mimetype=application/vnd.etsi.asic-s+zip".encode()

            # add tst
            if TIMESTAMP not in container.namelist():
                with container.open(self.dataobject, mode='r') as data:
                    token = tst.get_token(data.read())
                container.writestr(TIMESTAMP, token)

            # TODO: verify tst if it is already present

            # TODO: add ots
            if TIMESTAMP+".ots" not in container.namelist():
                with container.open(TIMESTAMP, mode='r') as data:
                    ots_token = ots.get_token(data.read())
                container.writestr(TIMESTAMP+".ots", ots_token)

            # TODO: verify/upgrade/prune ots

            container.close()

        return 0
