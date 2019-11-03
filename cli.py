# -*- coding: utf-8 -*-
'''
This file belong to [TimeBags Project](https://timebags.org)
'''

import os.path
import zipfile
import tempfile
import asic


def main(pathfiles):
    ''' Main '''

    # do files exist?
    for name in pathfiles:
        if not os.path.exists(name):
            print("%s is not a file" % name)
            return 1

    if len(pathfiles) == 1 and os.path.isfile(pathfiles[0]):
        pathfile = pathfiles[0]

    else:
        # create a timebag.zip (default name) asic compliant
        pathfile = "timebag.zip"
        number = 0
        while os.path.isfile(pathfile):
            # if file exist increment number suffix
            number += 1
            pathfile = "timebag" + str(number) + ".zip"

        with zipfile.ZipFile(pathfile, mode='x') as timebag_zip:
            # put inside timebag.zip a dataobject.zip with all that stuff
            print("Creating new zip file %s with dataobject.zip inside" % pathfile)

            with tempfile.TemporaryDirectory() as tmpdir:
                dataobject_path = os.path.join(tmpdir, "dataobject.zip")
                with zipfile.ZipFile(dataobject_path, mode='x') as dataobject_zip:

                    for name in pathfiles:
                        if os.path.isfile(name):
                            dataobject_zip.write(name)
                        elif os.path.isdir(name):
                            for root, dirs, files in os.walk(name):
                                for leaf in files:
                                    dataobject_zip.write(os.path.join(root, leaf))

                    dataobject_zip.close()
                timebag_zip.write(dataobject_path, os.path.basename(dataobject_path))
            timebag_zip.close()

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
