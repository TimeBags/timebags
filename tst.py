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
from rfc3161ng import RemoteTimestamper, get_timestamp, check_timestamp, TimeStampToken
from rfc3161ng.api import load_certificate
from cryptography.exceptions import InvalidSignature
from cryptography.x509.ocsp import _OIDS_TO_HASH as HASH
from pyasn1.codec.der import decoder
import yaml

import settings

def get_token(data):
    ''' Call a Remote TimeStamper to obtain a ts token of data '''

    tst = None
    tsa_url = None
    with open(os.path.join(settings.path_tsa_dir, settings.tsa_yaml)) as tsa_list_fh:
        tsa_list = yaml.load(tsa_list_fh, Loader=yaml.FullLoader)

        for tsa in tsa_list:
            tsa_pathfile = os.path.join(settings.path_tsa_dir, tsa['tsacrt'])
            if not os.path.isfile(tsa_pathfile):
                msg = "TSA cert file missing for %s" % tsa['url']
                logging.info(msg)
                continue
            with open(tsa_pathfile, 'rb') as tsa_fh:
                certificate = tsa_fh.read()
            timestamper = RemoteTimestamper(tsa['url'],
                                    certificate=certificate, cafile=tsa['cacrt'],
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
                tsa_url = tsa['url']
                break

    if tst is not None:
        msg = "TSA %s timestamped dataobject at: %s" % (tsa_url, get_timestamp(tst))
        logging.info(msg)
        return (tst, get_timestamp(tst), tsa_url)

    msg = "none of the TSA provided a timestamp"
    logging.critical(msg)
    return None


def get_info(tst):
    ''' Fetch timestamp and TSA info from token '''

    return (get_timestamp(tst), get_tsa_common_name(tst))


def verify_tst(tst_pf, dat_pf):
    ''' Verify timestamp token '''

    # TODO: Verify tst whenever it is possible.
    #       Generally I can verify a tst previously generated by others
    #       only if I have a trusted copy of the certificate of the TSA
    #       that issued the time stamp token.
    #       EU QTSP are listed in public lists with their certs.
    #       A trusted copy of the root CA certificate is needed too.

    with open(dat_pf, mode='rb') as dat_fd:
        dat = dat_fd.read()

    with open(tst_pf, mode='rb') as tst_fd:
        tst = tst_fd.read()

    if not isinstance(tst, TimeStampToken):
        tst, substrate = decoder.decode(tst, asn1Spec=TimeStampToken())
        if substrate:
            raise ValueError("extra data after tst")

    hash_oid = str(tst.tst_info.message_imprint.hash_algorithm[0])
    hashname = HASH[hash_oid].name
    msg = "Verify tst <%s> and dat <%s> hash <%s> commonName <%s>" \
            % (tst_pf, dat_pf, hashname, get_tsa_common_name(tst))
    logging.debug(msg)

    # FIXME: why geting crt from tst does not work?
    # crt = load_certificate(tst.content, b'')
    app_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    crt_pf = os.path.join(app_dir, settings.freetsa_pem)
    with open(crt_pf, mode='rb') as crt_fd:
        crt = crt_fd.read()

    ret = False
    try:
        ret = check_timestamp(tst, data=dat, certificate=crt, hashname=hashname)
    except ValueError as err:
        msg = "ValueError: %s" % str(err)
        logging.critical(msg)
    except InvalidSignature:
        msg = "InvalidSignature"
        logging.critical(msg)
    return ret


def get_tsa_common_name(tst):
    ''' Get the TSA commonName from tst embedded certificate '''

    if not isinstance(tst, TimeStampToken):
        tst, substrate = decoder.decode(tst, asn1Spec=TimeStampToken())
        if substrate:
            raise ValueError("extra data after tst")
    signed_data = tst.content
    cert = load_certificate(signed_data, b'')

    for rdns in cert.subject.rdns:
        for attr in rdns._attributes: # pylint: disable=W0212
            if attr.oid._name == "commonName": # pylint: disable=W0212
                return attr.value

    return None
