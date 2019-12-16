# Copyright (C) 2016-2018 The OpenTimestamps developers
#
# This file is part of the OpenTimestamps Client.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of the OpenTimestamps Client, including this file, may be copied,
# modified, propagated, or distributed except according to the terms contained
# in the LICENSE file.

''' module derived from OpenTimestamps Client but usable as a python library '''

import sys

import logging
import os
import time
import threading
from queue import Queue, Empty

from opentimestamps.core.timestamp import DetachedTimestampFile, make_merkle_tree
from opentimestamps.core.timestamp import OpAppend, OpSHA256, Timestamp
from opentimestamps.core.serialize import StreamSerializationContext

import opentimestamps.calendar

import otsclient


DEF_MIN_RESP = 2
DEF_TIMEOUT = 10


def remote_calendar(calendar_uri):
    """Create a remote calendar with User-Agent set appropriately"""
    return opentimestamps.calendar.RemoteCalendar(calendar_uri,
                                                  user_agent="OpenTimestamps-Client/%s"
                                                  % otsclient.__version__)


def create_timestamp(timestamp, calendar_urls, min_resp, timeout):
    """Create a timestamp

    calendar_urls - List of calendar's to use
    """


    n_cals = len(calendar_urls)
    msg = "Doing %d-of-%d request, timeout %d sec." % (min_resp, n_cals, timeout)
    logging.debug(msg)

    q_cals = Queue()
    for calendar_url in calendar_urls:
        submit_async(calendar_url, timestamp.msg, q_cals, timeout)

    start = time.time()
    merged = 0
    for i in range(n_cals): # pylint: disable=W0612
        try:
            remaining = max(0, timeout - (time.time() - start))
            result = q_cals.get(block=True, timeout=remaining)
            try:
                if isinstance(result, Timestamp):
                    timestamp.merge(result)
                    merged += 1
                else:
                    logging.debug(str(result))
            except Exception as error:
                logging.debug(str(error))

        except Empty:
            # Timeout
            continue

    if merged < min_resp:
        msg = "Failed to create timestamp: need at least %d attestation%s " \
              "but received %s within timeout" \
              % (min_resp, "" if min_resp == 1 else "s", merged)
        logging.error(msg)
        return False

    msg = "%.2f seconds elapsed" % (time.time()-start)
    logging.debug(msg)
    return True


def submit_async(calendar_url, message, q_cals, timeout):
    ''' async call to calendar '''

    def submit_async_thread(remote, message, q_cals, timeout):
        ''' async thread '''

        try:
            calendar_timestamp = remote.submit(message, timeout=timeout)
            q_cals.put(calendar_timestamp)
        except Exception as exc:
            q_cals.put(exc)

    msg = 'Submitting to remote calendar %s' % calendar_url
    logging.info(msg)
    remote = remote_calendar(calendar_url)
    t_cal = threading.Thread(target=submit_async_thread, args=(remote, message, q_cals, timeout))
    t_cal.start()


def ots_stamp(file_list, min_resp=DEF_MIN_RESP, timeout=DEF_TIMEOUT):
    ''' stamp function '''

    merkle_roots = []
    file_timestamps = []

    for file_name in file_list:
        with open(file_name, 'rb') as file_handler:
            try:
                file_timestamp = DetachedTimestampFile.from_fd(OpSHA256(), file_handler)
            except OSError as exp:
                msg = "Could not read %r: %s" % (file_name, exp)
                logging.error(msg)
                raise

        # nonce
        nonce_appended_stamp = file_timestamp.timestamp.ops.add(OpAppend(os.urandom(16)))
        merkle_root = nonce_appended_stamp.ops.add(OpSHA256())

        merkle_roots.append(merkle_root)
        file_timestamps.append(file_timestamp)

    merkle_tip = make_merkle_tree(merkle_roots)

    calendar_urls = []
    calendar_urls.append('https://a.pool.opentimestamps.org')
    calendar_urls.append('https://b.pool.opentimestamps.org')
    calendar_urls.append('https://a.pool.eternitywall.com')
    calendar_urls.append('https://ots.btc.catallaxy.com')

    if not create_timestamp(merkle_tip, calendar_urls, min_resp, timeout):
        return False

    for (file_name, file_timestamp) in zip(file_list, file_timestamps):
        timestamp_file_path = file_name + '.ots'
        try:
            with open(timestamp_file_path, 'xb') as timestamp_fd:
                ctx = StreamSerializationContext(timestamp_fd)
                file_timestamp.serialize(ctx)
        except IOError as exp:
            msg = "Failed to create timestamp %r: %s" % (timestamp_file_path, exp)
            logging.error(msg)
            raise

    return True



if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    #ots_stamp(sys.argv[1:], min_resp=DEF_MIN_RESP, timeout=DEF_TIMEOUT)
    ots_stamp(sys.argv[1:])
