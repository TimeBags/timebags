#!/usr/bin/env python3
'''
This library belong to [TimeBags Project](https://timebags.org)

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

The basic TimeBags implementation of an ASiC file requires the following ojects:
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

import libarchive-c


