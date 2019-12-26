import json
import requests
from packaging import version
import sys

def version(package):
    url = "https://pypi.python.org/pypi/%s/json" % package
    data = requests.get(url).json()
    versions = sorted(data['releases'])
    #versions = sorted(data['releases'], key=version.parse())
    #versions.sort(key=version.parse)
    return versions


print ("\n", version(sys.argv[1]))
