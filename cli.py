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
'''

import os.path
import zipfile
import tempfile
import asic


def there_can_be_only_one(pathfiles):
    ''' asic-s MUST have a single dataobject '''

    # sanity check: do files exist?
    for name in pathfiles:
        if not os.path.exists(name):
            print("%s is not a file" % name)
            return None

    # if only one, MUST be a "regular file"
    if len(pathfiles) == 1 and os.path.isfile(pathfiles[0]):
        pathfile = os.path.basename(pathfiles[0])

    else:
        # create a timebag.zip (default name) asic compliant
        pathfile = "timebag.zip"
        number = 0
        while os.path.exists(pathfile):
            # if file exist increment number suffix
            number += 1
            pathfile = "timebag_" + str(number) + ".zip"

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

    return pathfile


def main(pathfiles):
    ''' Main '''

    pathfile = there_can_be_only_one(pathfiles)
    if not pathfile:
        print("Error: params [%s] are not regular files!" % pathfiles)
        return False

    if os.stat(pathfile).st_size == 0:
        print("Error: file %s is empty!" % pathfile)
        return False

    container = asic.ASiCS(pathfile)
    while not container.valid:
        print(container.status)

        # the file is not a zip archive compliant with ASiC-S requirements
        # create a new zip_file using the original as a dataobject
        new_pathfile = pathfile + ".zip"

        # check if already exists
        if os.path.isfile(new_pathfile):
            print("Error: File %s already exists!" % new_pathfile)
            return False

        # create new_zip
        print("Creating new zip file %s with dataobject: %s" % (new_pathfile, pathfile))
        with zipfile.ZipFile(new_pathfile, mode='x') as new_zip:
            new_zip.write(pathfile)
            new_zip.close()

        # validate new_zip
        container = asic.ASiCS(new_pathfile)

    # update the ASiC-S container or the new_zip container (becoming ASiC-S)
    return container.update()
