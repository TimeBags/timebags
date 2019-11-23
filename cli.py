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


def add_to_zip(fh_zip, name, arcname=None):
    ''' try adding a file to the zip archive '''

    try:
        if os.stat(name).st_size == 0:
            # FIXME: should raise exception
            print("Skip empty file %s" % name)
            return False
        elif os.path.isfile(name):
            fh_zip.write(name, arcname=arcname)
            print("Zip %s" % name)
            return True
        else:
            # FIXME: should raise exception
            print("Skip non regular file %s" % name)
            return False
    except OSError as err:
        print("Failed to zip %s, error=%s" % (name, err))
        return False

def create_zip(path_zip, path_files):
    ''' zip files '''

    with zipfile.ZipFile(path_zip, mode='x') as fh_zip:

        counter = 0
        for name in path_files:

            if os.path.isdir(name):
                for root, _, files in os.walk(name):
                    for leaf in files:
                        path_leaf = os.path.join(root, leaf)
                        if add_to_zip(fh_zip, path_leaf):
                            counter += 1 # one more file stored
                        else:
                            counter = 0
                            break

            elif add_to_zip(fh_zip, name):
                counter += 1 # one more file stored
            else:
                counter = 0
                break


    # check if there is some file stored
    if counter == 0:
        print("Error: not valid file found!")
        os.remove(path_zip)
        return False
    return True


def there_can_be_only_one(pathfiles, pathzip=None):
    ''' asic-s MUST have a single dataobject '''


    # if zipfile name is not provided build it
    if not pathzip:
        if len(pathfiles) == 1 and not os.path.isdir(pathfiles[0]):
            # use file name as the zip prefix
            prefix = os.path.basename(pathfiles[0])
        else:
            # FIXME: when invoked by GUI the user has to be asked for the path
            # use "timebag" as default prefix
            prefix = "timebag"

        pathzip = prefix + ".zip"

        # now check if this name already exists
        name_number = 0
        while os.path.exists(pathzip):
            # if file exists, then increment number suffix
            name_number += 1
            pathzip = prefix + "_" + str(name_number) + ".zip"

    elif os.path.exists(pathzip):
        # FIXME: this check could be moved to args check
        print("Error: zipfile name provided already exists: %s" % pathzip)
        return None

    # create the asic-s zip
    with zipfile.ZipFile(pathzip, mode='x') as timebag_zip:
        print("Creating new asic-s file %s" % pathzip)

        if len(pathfiles) == 1 and not os.path.isdir(pathfiles[0]):
            # put inside the asic-s zip the single file
            result = add_to_zip(timebag_zip, pathfiles[0], os.path.basename(pathfiles[0]))

        else:
            # put inside the asic-s zip a dataobject.zip with all that stuff
            with tempfile.TemporaryDirectory() as tmpdir:
                dataobject_path = os.path.join(tmpdir, "dataobject.zip")
                result = create_zip(dataobject_path, pathfiles)
                if result:
                    result = add_to_zip(timebag_zip, dataobject_path, os.path.basename(dataobject_path))

    # remove filezip if creation failed
    if not result:
        os.remove(pathzip)
        print("Error: valid file not found in params (%s)" % pathfiles)
        return None

    return pathzip


def main(pathfiles):
    ''' Main '''

    # if there are more then one param, create a zip with a single dataobject containing them
    pathfile = there_can_be_only_one(pathfiles)
    if pathfile:

        # complete the zip container and get an ASiC-S
        container = asic.ASiCS(pathfile)
        return container.complete()
