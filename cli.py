# -*- coding: utf-8 -*-

'''
This file belong to [TimeBags Project](https://timebags.org)
'''
import os.path
import zipfile
import asic

def main(pathfile):
    ''' Main '''

    # does file exist?
    if not os.path.isfile(pathfile):
        print("%s is not a file" % pathfile)
        return 1

    container = asic.ASiCS(pathfile)
    while not container.valid:
        print(container.status)

        # the file is not a zip archive compliant with ASiC-S requirements
        # create a new zip_file using the original as a dataobject
        new_pathfile = pathfile + ".zip"

        # check if already exists
        if os.path.isfile(new_pathfile):
            print("File %s already exists!" % new_pathfile)
            return 1

        # create new_zip
        print("Creating new zip file %s with dataobject: %s" % (new_pathfile, pathfile))
        with zipfile.ZipFile(new_pathfile, mode='x') as new_zip:
            new_zip.write(pathfile)
            new_zip.close()

        # validate new_zip
        container = asic.ASiCS(new_pathfile)

    # update the ASiC-S container or the new_zip container (becoming ASiC-S)
    return container.update()
