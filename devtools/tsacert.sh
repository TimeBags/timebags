# <TrustServiceStatusList xmlns="http://uri.etsi.org/02231/v2#" xmlns:ns2="http://www.w3.org/2000/09/xmldsig#" xmlns:ns3="http://uri.etsi.org/01903/v1.3.2#" xmlns:ns4="http://uri.etsi.org/02231/v2/additionaltypes#" xmlns:ns5="http://uri.etsi.org/TrstSvc/SvcInfoExt/eSigDir-1999-93-EC-TrustedList/#" xmlns:ns6="http://uri.etsi.org/01903/v1.4.1#" Id="ID100001" TSLTag="http://uri.etsi.org/19612/TSLTag">
# <SchemeInformation>...</SchemeInformation>
# <TrustServiceProviderList>...</TrustServiceProviderList>
# <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Id="id-80730647ac17b28a14230ebf673ddb34">...</ds:Signature>
# </TrustServiceStatusList>
#

# http://tlbrowser.tsl.website/tools/

# https://ec.europa.eu/information_society/policy/esignature/trusted-list/tl-mp.xml
# https://security.stackexchange.com/questions/185948/how-to-validate-that-a-eu-list-of-trusted-lists-is-authentic/210074

# https://webgate.ec.europa.eu/tl-browser/#/tl/IT/43/2

name="CN=Intesi Group EU Qualified Time-Stamp CA G2"

curl -s https://eidas.agid.gov.it/TL/TSL-IT.xml | grep -A 5 "${name}" |grep X509Certificate| sed 's/<\/*X509Certificate>//g' | base64 -d | openssl x509 -inform DER -text

