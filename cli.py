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
            print("Error: %s is not a file" % name)
            return None


    # if only one, MUST be a "regular file"
    # FIXME: isfile does not detect special device files like /dev/ttyS0?
    if len(pathfiles) == 1 and os.path.isfile(pathfiles[0]):

        if os.stat(pathfiles[0]).st_size == 0:
            print("Error: file %s is empty!" % pathfiles[0])
            pathfile = None
        else:
            pathfile = pathfiles[0]

        return pathfile


    else:
        counter = 0 # initialize number of valid files to store

        # create a timebag.zip (default name)
        # FIXME: when invoked by GUI the user has to be asked for the path
        pathfile = "timebag.zip"

        # check if already exists
        name_number = 0
        while os.path.exists(pathfile):
            # if file exist increment number suffix
            name_number += 1
            pathfile = "timebag_" + str(name_number) + ".zip"

        # create an asic-s
        with zipfile.ZipFile(pathfile, mode='x') as timebag_zip:
            # put inside timebag.zip a dataobject.zip with all that stuff
            print("Creating new zip file %s with dataobject.zip inside" % pathfile)

            with tempfile.TemporaryDirectory() as tmpdir:
                dataobject_path = os.path.join(tmpdir, "dataobject.zip")
                with zipfile.ZipFile(dataobject_path, mode='x') as dataobject_zip:

                    for name in pathfiles:
                        if os.path.isfile(name):
                            if os.stat(name).st_size == 0:
                                print("Skip empty file %s" % name)
                            else:
                                print("Adding %s inside dataobject" % name)
                                dataobject_zip.write(name)
                                counter += 1 # one more file stored
                        elif os.path.isdir(name):
                            for root, dirs, files in os.walk(name):
                                for leaf in files:
                                    if os.stat(os.path.join(root, leaf)).st_size == 0:
                                        print("Skip empty file %s" % os.path.join(root, leaf))
                                    elif os.path.isfile(os.path.join(root, leaf)):
                                        print("Adding %s inside dataobject" % os.path.join(root, leaf))
                                        dataobject_zip.write(os.path.join(root, leaf))
                                        counter += 1
                                    else:
                                        print("Skip non regular file %s" % os.path.join(root, leaf))
                        else:
                            print("Skip non regular file %s" % name)

                    dataobject_zip.close()
                timebag_zip.write(dataobject_path, os.path.basename(dataobject_path))
            timebag_zip.close()

        # check if there is some file stored
        if counter == 0:
            print("Error: no files to put inside dataobject!")
            os.remove(pathfile)
            return None
        else:
            return pathfile


def main(pathfiles):
    ''' Main '''

    # if there are more then one param, create a zip with a single dataobject containing them
    pathfile = there_can_be_only_one(pathfiles)
    if not pathfile:
        print("Error: valid file not found in params (%s)" % pathfiles)
        return False

    # check if file is already a vaid asic-s
    container = asic.ASiCS(pathfile)

    while not container.valid:

        # the file is not a zip archive compliant with ASiC-S requirements
        print(container.status)

        # create a new zip_file using the original as a dataobject
        new_pathfile = pathfile + ".zip"

        # check if already exists
        name_number = 0
        while os.path.exists(new_pathfile):
            # if file exist increment number suffix
            name_number += 1
            new_pathfile = pathfile + "." + str(name_number) + ".zip"

        # create an asic-s
        print("Creating new zip file %s with dataobject: %s" % (new_pathfile, pathfile))
        with zipfile.ZipFile(new_pathfile, mode='x') as new_zip:
            new_zip.write(pathfile, os.path.basename(pathfile))
            new_zip.close()

        # validate the asic-s
        container = asic.ASiCS(new_pathfile)

    # update the ASiC-S container or the new_zip container (becoming ASiC-S)
    return container.update()
