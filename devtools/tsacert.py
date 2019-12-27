
'''
openssl x509 -text -in tsa.crt | grep -A 3 "Authority Information Access"
'''

import sys
from cryptography import x509
from cryptography.hazmat.backends import default_backend

with open(sys.argv[1], "rb") as tsa_pem:
    cert = x509.load_pem_x509_certificate(tsa_pem.read(), default_backend())
for rdns in cert.subject.rdns:
    #print(dir(rdns._attributes))
    for a in rdns._attributes:
        if a.oid._name == "organizationName":
            print("Organization = %s" % a.value)
        if a.oid._name == "commonName":
            print("Common Name = %s" % a.value)

#for e in cert.extensions:
#    print(e.oid, e.value)

from cryptography.x509.oid import ExtensionOID
#print(dir(ExtensionOID))

e = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
print("Subject Key Identifier = %s" % e.value.digest.hex())

e = cert.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
print("Authority Information Access:")
for item in e.value:
    #print(item.access_method.dotted_string, item.access_method._name, item.access_location.value)
    print("- %s = %s" % (item.access_method._name, item.access_location.value))
print("CRL Distribution Points:")
e = cert.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)
for item in e.value:
    for url in item.full_name:
        print("- %s" % url.value)
