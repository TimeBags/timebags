# -*- coding: utf-8 -*-

'''
This file belong to [TimeBags Project](https://timebags.org)

openssl ts -query -data data.txt -no_nonce -sha512 -out file.tsq

curl -H "Content-Type: application/timestamp-query" --data-binary
    '@file.tsq' https://freetsa.org/tsr > file.tsr

curl -o tsa.crt https://freetsa.org/files/tsa.crt

curl -o cacert.pem https://freetsa.org/files/cacert.pem

openssl ts -verify -in file.tsr -data data.txt -CAfile cacert.pem -untrusted tsa.crt
'''

from os import urandom
from struct import unpack
from rfc3161ng import RemoteTimestamper


def get_token(data):
    ''' Call a Remote TimeStamper to obtain a ts token of data '''

    url = "https://freetsa.org/tsr"
    tsafile = "freetsa.crt"
    cafile = None
    username = None
    password = None
    timeout = 10
    hashname = 'sha256'
    include_tsa_cert = True

    certificate = open(tsafile, "rb").read()
    timestamper = RemoteTimestamper(url, certificate=certificate, cafile=cafile,
                                    hashname=hashname, timeout=timeout,
                                    username=username, password=password,
                                    include_tsa_certificate=include_tsa_cert)
    nonce = unpack('<q', urandom(8))[0]
    return timestamper.timestamp(data=data, nonce=nonce)

#with open(dataobject, "rb") as data_file:
#    nonce = unpack('<q', urandom(8))[0]
#    tst = timestamper.timestamp(data=data_file.read(), nonce=nonce)

#with open(tst_file, "wb") as tst_der:
#    tst_der.write(tst)

#with open(tst_file, "rb") as tst_der:
#    tst = tst_der.read()
#    print(rfc3161ng.get_timestamp(tst))
#rt.check(tst, data=data_file.read())

# openssl ts -reply -in timestamp.tst -token_in -text

# openssl ts -verify -in timestamp.tst -token_in -CAfile cacert.pem
# -untrusted tsa.crt -data data.txt
