# -*- coding: utf-8 -*-
# Copyright (C) 2019 The TimeBags developers
#
# This file is part of the TimeBags software.
#
# It is subject to the license terms in the LICENSE file
# found in the top-level directory of this distribution.
#
# No part of the Timebags software, including this file, may be copied,
# modified, propagated, or distributed except according to the terms
# contained in the LICENSE file.

'''
TSA keysore
'''

def create_tsa_yaml(tsa_yaml):
    ''' create default tsa configuration file '''

    data = \
'''
- # Free TSA
    url: https://freetsa.org/tsr
    tsacrt: freetsa.pem
    cacrt: null
    username: null
    password: null
    timeout: 10
    hashname: sha256
    include_tsa_cert: true

#- # Comodo TSA
    # url: http://timestamp.comodoca.com/rfc3161
    # tsacrt: comodotsa.pem
    # cacrt: null
    # username: null
    # password: null
    # timeout: 10
    # hashname: sha256
    # include_tsa_cert: false '''

    with open(tsa_yaml, 'x') as ty_fd:
        ty_fd.write(data)


def create_freetsa_pem(freetsa_pem):
    ''' create freetsa certificate pem file '''

    data = \
'''-----BEGIN CERTIFICATE-----
MIIIATCCBemgAwIBAgIJAMHphhYNqOmCMA0GCSqGSIb3DQEBDQUAMIGVMREwDwYD
VQQKEwhGcmVlIFRTQTEQMA4GA1UECxMHUm9vdCBDQTEYMBYGA1UEAxMPd3d3LmZy
ZWV0c2Eub3JnMSIwIAYJKoZIhvcNAQkBFhNidXNpbGV6YXNAZ21haWwuY29tMRIw
EAYDVQQHEwlXdWVyemJ1cmcxDzANBgNVBAgTBkJheWVybjELMAkGA1UEBhMCREUw
HhcNMTYwMzEzMDE1NzM5WhcNMjYwMzExMDE1NzM5WjCCAQkxETAPBgNVBAoTCEZy
ZWUgVFNBMQwwCgYDVQQLEwNUU0ExdjB0BgNVBA0TbVRoaXMgY2VydGlmaWNhdGUg
ZGlnaXRhbGx5IHNpZ25zIGRvY3VtZW50cyBhbmQgdGltZSBzdGFtcCByZXF1ZXN0
cyBtYWRlIHVzaW5nIHRoZSBmcmVldHNhLm9yZyBvbmxpbmUgc2VydmljZXMxGDAW
BgNVBAMTD3d3dy5mcmVldHNhLm9yZzEiMCAGCSqGSIb3DQEJARYTYnVzaWxlemFz
QGdtYWlsLmNvbTESMBAGA1UEBxMJV3VlcnpidXJnMQswCQYDVQQGEwJERTEPMA0G
A1UECBMGQmF5ZXJuMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAtZEE
jE5IbzTp3Ahif8I3UWIjaYS4LLEwvv9RfPw4+EvOXGWodNqyYhrgvOfjNWPg7ek0
/V+IIxWfB4SICCJ0YMHtiCYXBvQoEzQ1nfu4G9E1P8F5YQrxqMjIZdwA6iOzqJvm
vQO6hansgn1gVlkF4i1qWE7ROArhUCgM7jl+mKAS84BGQAeGJEO8B3y5X0Ia8xcS
2Wg8223/uvPIululZq5SPUWdYXc0bU2EDieIa3wBxbiQ14ouJ7uo3S+aKBLhV9Yv
khxlliVIBp3Nt9Bt4YHeDpVw1m+HIgzii2KKtVkG8+4MIQ9wUej0hYr4uaktCeRq
8tnLpb/PrRaM32BEkaSwZgOxFMr3Ax8GXn7u+lPFdfNJDAWdLjLdx2rE1MTHEGg7
l/0b5ZG8YQVRhtiPmgORswe2+R7ZVNqjb5rNah4Uqi5K3xdGS1TbGNu2/+MAgCRl
RzcENs5Od7rl3m/g8/nW5/++tGHnlOkvsJUfiq5hpBLM6bIQdGNci+MnrhoPa0pk
brD4RjvGO/hFUwQ10Z6AJRHsn2bDSWlS2L7LabCqTUxB9gUV/n3LuJMZzdpZumrq
S+POrnGOb8tszX25/FC7FbEvNmWwqjByicLm3UsRHOSLotnv21prmlBgaTNPs09v
x64zDws0IIqsgN8yZv3ZBGWHa6LLiY2VBTFbbnsCAwEAAaOCAdswggHXMAkGA1Ud
EwQCMAAwHQYDVR0OBBYEFG52C3tOT5zhYMptLOknoqKUs3c3MB8GA1UdIwQYMBaA
FPpVDYw0ZlFDTPfns6dsla965qSXMAsGA1UdDwQEAwIGwDAWBgNVHSUBAf8EDDAK
BggrBgEFBQcDCDBjBggrBgEFBQcBAQRXMFUwKgYIKwYBBQUHMAKGHmh0dHA6Ly93
d3cuZnJlZXRzYS5vcmcvdHNhLmNydDAnBggrBgEFBQcwAYYbaHR0cDovL3d3dy5m
cmVldHNhLm9yZzoyNTYwMDcGA1UdHwQwMC4wLKAqoCiGJmh0dHA6Ly93d3cuZnJl
ZXRzYS5vcmcvY3JsL3Jvb3RfY2EuY3JsMIHGBgNVHSAEgb4wgbswgbgGAQAwgbIw
MwYIKwYBBQUHAgEWJ2h0dHA6Ly93d3cuZnJlZXRzYS5vcmcvZnJlZXRzYV9jcHMu
aHRtbDAyBggrBgEFBQcCARYmaHR0cDovL3d3dy5mcmVldHNhLm9yZy9mcmVldHNh
X2Nwcy5wZGYwRwYIKwYBBQUHAgIwOxo5RnJlZVRTQSB0cnVzdGVkIHRpbWVzdGFt
cGluZyBTb2Z0d2FyZSBhcyBhIFNlcnZpY2UgKFNhYVMpMA0GCSqGSIb3DQEBDQUA
A4ICAQClyUTixvrAoU2TCn/QoLFytB/BSDw+lXxoorzZuXZPGpUBYf1yRy1Bpe7S
d3hiA7VCIkD7OibN4XYIe2+xAR30zBniVxqkoFEQlmXpTEb1C9Kt7mrEE34lGyWj
navaRRUV2P+eByCejsILeHT34aDt58AJN/6EozT4syZc7S2O2d9hOWWDZ3/rOCwe
47I+bqXwXfMN57n4kAXSUmb2EvOci09tq6bXv7rBljK5Bjcyn1Km8GahDkPqqB+E
mmxf4/6LXqIydfaH8gUuUC6mwwdipmjM4Hhx3Y6X4xW7qSniVYmXegoxLOlsUQax
Q3x3nys2GxgoiPPuiiNDdPoGPpVhkmJ/fEMQc5ZdEmCSjroAnoA0Ka4yTPlvBCNU
83vKWv3cefeTRqs4i/x58B3JhhJU6mzBKZQQdrg9IFVvO+UTJoN/KHb3gzs3Dnw9
QQUjgn1PU0AMciGNdSKf8QxviJOpo6HAxCu0yJjBPfQcf2VztPxWUVlxphCnsNKF
fIIlqfsgTqzsouiXGqGvh4hqKuPHL+CgquhCmAp3vvFrkhFUWAkNmCtZRmA3ZOda
CtPRFFS5mG9ni5q2r+hJcDOuOr/U60O3vJ3uaIFZSeZIFYKoLnhSd/IoIQfv45Ag
DgUIrLjqguolBSdvPJ2io9O0rTi7+IQr2jb8JEgpH1WNwC3R4A==
-----END CERTIFICATE-----'''

    with open(freetsa_pem, 'x') as pem_fd:
        pem_fd.write(data)
