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

openssl ts -verify -data Readme.md -in timestamp.tst -CAfile freetsa.pem -partial_chain -token_in
'''

import os
import inspect
from struct import unpack
import logging
from rfc3161ng import RemoteTimestamper, get_timestamp, check_timestamp
from cryptography.exceptions import InvalidSignature


def get_token(data):
    ''' Call a Remote TimeStamper to obtain a ts token of data '''

    # TBD: read the list from a config file and append cli params
    tsa_list = [{
        'url' : "http://timestamp.comodoca.com/rfc3161",
        'tsacrt' : "freetsa.crt",
        'cacrt' : None,
        'username' : None,
        'password' : None,
        'timeout' : 10,
        'hashname' : 'sha256',
        'include_tsa_cert' : False
    }, {
        'url' : "https://freetsa.org/tsr",
        'tsacrt' : "freetsa.crt",
        'cacrt' : None,
        'username' : None,
        'password' : None,
        'timeout' : 10,
        'hashname' : 'sha256',
        'include_tsa_cert' : True
    }]
    tst = None

    app_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    for tsa in tsa_list:
        if not os.path.isfile(tsa['tsacrt']):
            msg = "TSA cert file missing for %s" % tsa['url']
            logging.info(msg)
            continue
        tsa_pathfile = os.path.join(app_dir, tsa['tsacrt'])
        with open(tsa_pathfile, 'rb') as tsa_fh:
            certificate = tsa_fh.read()
        timestamper = RemoteTimestamper(tsa['url'], certificate=certificate, cafile=tsa['cacrt'],
                                        hashname=tsa['hashname'], timeout=tsa['timeout'],
                                        username=tsa['username'], password=tsa['password'],
                                        include_tsa_certificate=tsa['include_tsa_cert'])
        nonce = unpack('<q', os.urandom(8))[0]

        msg = "try using TSA endpoint %s to timestamp data" % tsa['url']
        logging.debug(msg)
        try:
            tst = timestamper.timestamp(data=data, nonce=nonce)
        except RuntimeError as err:
            logging.debug(err)
        except InvalidSignature:
            msg = "Invalid signature in timestamp from %s" % tsa['url']
            logging.info(msg)
        else:
            break

    if tst is not None:
        msg = "TSA %s timestamped dataobject at: %s" % (tsa['url'], get_timestamp(tst))
        logging.info(msg)
        return (tst, get_timestamp(tst), tsa['url'])

    msg = "none of the TSA provided a timestamp"
    logging.critical(msg)
    return None


def get_info(tst):
    ''' Fetch timestamp from token '''

    # TODO: extract tsa-url from token using asn1 lib
    url = None
    return (get_timestamp(tst), url)


def verify_tst(tst_pf, dat_pf, tsa_pf):

    with open(tsa_pf, mode='rb') as tsa_fd:
        tsa = tsa_fd.read()

    with open(dat_pf, mode='rb') as dat_fd:
        dat = dat_fd.read()

    with open(tst_pf, mode='rb') as tst_fd:
        tst = tst_fd.read()

    # FIXME: hashname must be read from tst
    hashname='sha256'
    return check_timestamp(tst, data=dat, certificate=tsa, hashname=hashname)
