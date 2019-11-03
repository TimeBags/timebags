# -*- coding: utf-8 -*-

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
import tst
import ots


METAINF_DIR = os.path.join("META-INF", "")
TIMESTAMP = os.path.join("META-INF", "timestamp.tst")
TIMESTAMP_OTS = TIMESTAMP+".ots"

class ASiCS():
    ''' Class for managing ASiC-S files '''

    def __init__(self, pathfile):
        ''' Initialize ASiC-S container '''

        self.pathfile = pathfile
        self.valid = False
        self.dataobject = None
        self.status = ""

        if not zipfile.is_zipfile(self.pathfile):
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

                    # mimetype, timestamp files tst/ots and META-INF dir
                    # do not count as dataobjects
                    if item in (TIMESTAMP, TIMESTAMP_OTS, METAINF_DIR, "mimetype"):
                        pass

                    # we shall count any other file as a dataobject because any
                    # signature and other META-INF files need to be timestamped
                    else:
                        n_dataobject += 1
                        self.dataobject = item

        # a valid ASiC-S container must have exactly one dataobject
        # if ASiC-S contains detached signatures or META-INF files
        # then it is better timestamping the ASiC-S as a dataobject
        if n_dataobject != 1:
            self.dataobject = None
            self.valid = False
            self.status = "%s will be encapsulated because it has %d dataobjects" \
                            % (self.pathfile, n_dataobject)
        else:
            self.valid = True
            self.status = "%s can be updated as a simple ASiC-S container" % self.pathfile


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
                    if token is not None:
                        container.writestr(TIMESTAMP, token)

            # TBD:  Verify tst whenever it is possible.
            #       Generally I can verify a tst previously generated by others
            #       only if I have a trusted copy of the certificate of the TSA
            #       that issued the time stamp token.
            #       Only EU QTSP are listed in public lists with their certs.
            #       A trusted copy of the root CA certificate is needed too.

            if TIMESTAMP in container.namelist():
                # if tst is present, then move on adding ots
                if TIMESTAMP_OTS not in container.namelist():
                    with container.open(TIMESTAMP, mode='r') as data:
                        ots_token = ots.get_token(data.read())
                        if ots_token is not None:
                            container.writestr(TIMESTAMP_OTS, ots_token)
                else:
                    pass
                    # TODO: try to upgrade ots if incomplete

                    # TBD: try to prune ots if complete

                    # TBD: verify ots

            container.close()
            return bool(TIMESTAMP in container.namelist() and TIMESTAMP_OTS in container.namelist())
