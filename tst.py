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

openssl ts -query -data data.txt -no_nonce -sha512 -out file.tsq

curl -H "Content-Type: application/timestamp-query" --data-binary
    '@file.tsq' https://freetsa.org/tsr > file.tsr

curl -o tsa.crt https://freetsa.org/files/tsa.crt

curl -o cacert.pem https://freetsa.org/files/cacert.pem

openssl ts -reply -in timestamp.tst -token_in -text

openssl ts -verify -in timestamp.tst -data data.txt -CAfile cacert.pem -untrusted tsa.crt
'''

from os import urandom
from struct import unpack
from rfc3161ng import RemoteTimestamper, get_timestamp


def get_token(data):
    ''' Call a Remote TimeStamper to obtain a ts token of data '''

    # TBD: read the list from a config file and append cli params
    tsa_list = [{
        'url' : "https://freetsa.org/tsrx",
        'tsafile' : "freetsa.crt",
        'cafile' : None,
        'username' : None,
        'password' : None,
        'timeout' : 10,
        'hashname' : 'sha256',
        'include_tsa_cert' : True
    }, {
        'url' : "https://freetsa.org/tsr",
        'tsafile' : "freetsa.crt",
        'cafile' : None,
        'username' : None,
        'password' : None,
        'timeout' : 10,
        'hashname' : 'sha256',
        'include_tsa_cert' : True
    }]

    for tsa in tsa_list:
        certificate = open(tsa['tsafile'], 'rb').read()
        timestamper = RemoteTimestamper(tsa['url'], certificate=certificate, cafile=tsa['cafile'],
                                        hashname=tsa['hashname'], timeout=tsa['timeout'],
                                        username=tsa['username'], password=tsa['password'],
                                        include_tsa_certificate=tsa['include_tsa_cert'])
        nonce = unpack('<q', urandom(8))[0]

        try:
            tst = timestamper.timestamp(data=data, nonce=nonce)
        except RuntimeError:
            tst = None

    if tst is not None:
        print("TSA %s timestamped dataobject at: %s" % (tsa['url'], get_timestamp(tst)))
    else:
        print("ERROR: none of the tsa provided a timestamp")

    return tst

# def verify_token(data):
# verify calling remote timestamper?
#
# timestamper.check(tst, data)
