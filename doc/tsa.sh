#!/bin/bash

############# EDIT SECTION BEGIN

# get it from https://webgate.ec.europa.eu/tl-browser/#/
# 1. copy and paste form browser
# 2. convert from base64 to DER (base64 -d ...)
# 3. convert from DER to PEM (openssl x509 -in ... -inform DER -out ...)
CAFILE=example_CA.pem

# This is the URL of your favorite TSA
TSAURL=https://example.com/tsa

# This are your credentials in the format "<user>:<password>"
SECRET="goofy:123"

############# EDIT SECTION END

############# Do not change if you don't know what you are doing
DATAFILE=$1
HASH=sha256
CURL_HEADER="Content-Type: application/timestamp-query"
TSQFILE=data.tsq
TSRFILE=data.tsr
TSTFILE=data.tst
TSAFILE=TSA.pem

# build query
openssl ts -query -data "$DATAFILE" -cert -no_nonce -"$HASH" -out "$TSQFILE"

# get timestamp
curl -u $SECRET -H "$CURL_HEADER" --data-binary @"$TSQFILE" "$TSAURL" > "$TSRFILE"

# show reply
openssl ts -reply -in "$TSRFILE" -text

# estract token
openssl ts -reply -in "$TSRFILE" -token_out -out "$TSTFILE"

# extract TSA certificate
openssl pkcs7 -in data.tst -inform der -print_certs -out "$TSAFILE"

# verify fail because openssl does not support extended attributes
# https://github.com/elabftw/elabftw/issues/242#issuecomment-211988705
#openssl ts -verify -in "$TSRFILE" -data "$DATAFILE" -CAfile "$CAFILE" -untrusted "$TSAFILE"
