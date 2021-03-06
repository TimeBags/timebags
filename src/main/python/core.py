# -*- coding: utf-8 -*-
# Copyright (C) 2019 The TimeBags developers
#
# This file is part of the TimeBags software.
#
# It is subject to the license terms in the LICENSE file-
# found in the top-level directory of this distribution.
#
# No part of the TimeBags software, including this file, may be copied,
# modified, propagated, or distributed except according to the terms-
# contained in the LICENSE file.

'''
This file belong to [TimeBags Project](https://timebags.org)
'''

import os.path
import zipfile
import tempfile
import logging

import asic


def add_to_zip(fh_zip, name, arcname=None):
    ''' try adding a file to the zip archive '''


    if not os.path.isfile(name):
        msg = "non regular file %s" % name
        logging.info(msg)
        return False

    # NOTE : an empty file could be accepted in general with a warning message
    #        because only when it's the single dataobject in the asic-s archive
    #        it can't be timestamped, and this error will be catched later
    if os.stat(name).st_size == 0:
        msg = "empty file %s" % name
        logging.warning(msg)

    try:
        fh_zip.write(name, arcname=arcname)
    except OSError:
        logging.critical(msg)
        return False

    msg = "zipped %s" % name
    logging.info(msg)
    return True


def create_zip(path_zip, path_files):
    ''' zip files '''

    with zipfile.ZipFile(path_zip, mode='x') as fh_zip:

        msg = "creating zipfile %s" % path_zip
        logging.info(msg)
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
        os.remove(path_zip)
        msg = "found not valid file, zip aborted"
        logging.critical(msg)
        return False
    return True


def there_can_be_only_one(pathfiles, pathzip=None):
    ''' asic-s MUST have a single dataobject (not empty)'''


    # if there is only an empty file, do not create an asic-s archive with it
    if len(pathfiles) == 1 and os.path.isfile(pathfiles[0]) and os.stat(pathfiles[0]).st_size == 0:
        msg = "can't create valid asic-s with an empty file(%s)" % pathfiles[0]
        logging.critical(msg)
        return None

    # if a new zipfile name is not provided build it
    if not pathzip:
        if len(pathfiles) == 1 and not os.path.isdir(pathfiles[0]):
            # use file name as the zip prefix
            prefix = os.path.basename(pathfiles[0])
        else:
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
        # when invoked by GUI this check has already be done in get_save_filename()
        # when invoked by CLI the new timebag filename is not choosen by user
        msg = "zipfile name provided already exists: %s" % pathzip
        logging.error(msg)
        # then, something nasty it's appening if we are here!
        raise Exception(msg)

    # create the asic-s zip
    result = False
    with zipfile.ZipFile(pathzip, mode='x') as timebag_zip:
        msg = "creating new asic-s file %s" % pathzip
        logging.info(msg)

        if len(pathfiles) == 1 and not os.path.isdir(pathfiles[0]):
            # put inside the asic-s zip the single file
            result = add_to_zip(timebag_zip, pathfiles[0], os.path.basename(pathfiles[0]))

        else:
            # put inside the asic-s zip a dataobject.zip with all that stuff
            with tempfile.TemporaryDirectory() as tmpdir:
                dataobject_path = os.path.join(tmpdir, "dataobject.zip")
                result = create_zip(dataobject_path, pathfiles)
                if result:
                    result = add_to_zip(timebag_zip, dataobject_path, \
                                        os.path.basename(dataobject_path))

    # remove filezip if creation failed
    if not result:
        os.remove(pathzip)
        msg = "valid file not found in params (%s)" % pathfiles
        logging.critical(msg)
        return None

    return pathzip


def main(pathfiles, get_timebag_pathname=None):
    ''' Main '''


    result_pathfile = None

    # if there is only one param check for valid asic-s
    if len(pathfiles) == 1 and not os.path.isdir(pathfiles[0]):
        container = asic.ASiCS(pathfiles[0])
        if container.valid:
            result_pathfile = pathfiles[0]

    # if it's not an asic-s, then create a new zip asic-s
    if result_pathfile is None:
        if get_timebag_pathname is None: # call came from CLI
            result_pathfile = there_can_be_only_one(pathfiles)
        else: # call came from GUI, use the dialog to get pathzip
            pathzip = get_timebag_pathname()
            if pathzip:
                result_pathfile = there_can_be_only_one(pathfiles, pathzip)

    # if success creating asic-s, then complete it with timestamps
    if result_pathfile is not None:
        container = asic.ASiCS(result_pathfile)
        msg = "asic %s, valid: %s, status: %s" % \
                (result_pathfile, container.valid, container.status['asic-s'])
        logging.info(msg)

        container.process_timestamps()
        msg = "asic %s, result: %s" % \
                (result_pathfile, container.status['result'])
        logging.info(msg)

        # FIXME: pathfile should be changed everywhere from var to dict
        container.status['pathfile'] = container.pathfile
        return container.status

    return None
