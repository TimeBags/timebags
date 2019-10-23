
'''
openssl x509 -text -in tsa.crt | grep -A 3 "Authority Information Access"
'''

from cryptography import x509
from cryptography.hazmat.backends import default_backend

with open("tsa.crt", "rb") as tsa_der:
    cert = x509.load_pem_x509_certificate(tsa_der.read(), default_backend())
for rdns in cert.subject.rdns:
    #print(dir(rdns._attributes))
    for a in rdns._attributes:
        if a.oid._name in ("organizationName", "commonName"):
            print("%s - %s" % (a.oid._name, a.value))

#for e in cert.extensions:
#    print(e.oid, e.value)

from cryptography.x509.oid import ExtensionOID
#print(dir(ExtensionOID))

e = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
print("SUBJECT_KEY_IDENTIFIER")
print(e.value.digest.hex())

e = cert.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
print("AUTHORITY_INFORMATION_ACCESS")
for item in e.value:
    print(item.access_method.dotted_string, item.access_method._name, item.access_location.value)
print("CRL_DISTRIBUTION_POINTS")
e = cert.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)
for item in e.value:
    for url in item.full_name:
        print(url.value)
