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

import sys

import logging
import os
import time
import threading
from queue import Queue, Empty

from opentimestamps.core.timestamp import DetachedTimestampFile, make_merkle_tree, OpAppend, OpSHA256, Timestamp
from opentimestamps.core.serialize import StreamSerializationContext

import opentimestamps.calendar

import otsclient

def remote_calendar(calendar_uri):
    """Create a remote calendar with User-Agent set appropriately"""
    return opentimestamps.calendar.RemoteCalendar(calendar_uri,
                                                  user_agent="OpenTimestamps-Client/%s" % otsclient.__version__)


def create_timestamp(timestamp, calendar_urls):
    """Create a timestamp

    calendar_urls - List of calendar's to use
    """


    m = 2
    n = len(calendar_urls)
    timeout = 10
    logging.debug("Doing %d-of-%d request, timeout %d sec." % (m, n, timeout))

    q = Queue()
    for calendar_url in calendar_urls:
        submit_async(calendar_url, timestamp.msg, q, timeout)

    start = time.time()
    merged = 0
    for i in range(n):
        try:
            remaining = max(0, timeout - (time.time() - start))
            result = q.get(block=True, timeout=remaining)
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

    if merged < m:
        logging.error("Failed to create timestamp: need at least %d attestation%s but received %s within timeout" % (m, "" if m == 1 else "s", merged))
        sys.exit(1)
    logging.debug("%.2f seconds elapsed" % (time.time()-start))


def submit_async(calendar_url, msg, q, timeout):

    def submit_async_thread(remote, msg, q, timeout):
        try:
            calendar_timestamp = remote.submit(msg, timeout=timeout)
            q.put(calendar_timestamp)
        except Exception as exc:
            q.put(exc)

    logging.info('Submitting to remote calendar %s' % calendar_url)
    remote = remote_calendar(calendar_url)
    t = threading.Thread(target=submit_async_thread, args=(remote, msg, q, timeout))
    t.start()


def ots_stamp(file_list):

    merkle_roots = []
    file_timestamps = []

    for file_name in file_list:
        with open(file_name, 'rb') as file_handler:
            try:
                file_timestamp = DetachedTimestampFile.from_fd(OpSHA256(), file_handler)
            except OSError as exp:
                logging.error("Could not read %r: %s" % (file_name, exp))
                sys.exit(1)

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

    create_timestamp(merkle_tip, calendar_urls)

    for (file_name, file_timestamp) in zip(file_list, file_timestamps):
        timestamp_file_path = file_name + '.ots'
        try:
            with open(timestamp_file_path, 'xb') as timestamp_fd:
                ctx = StreamSerializationContext(timestamp_fd)
                file_timestamp.serialize(ctx)
        except IOError as exp:
            logging.error("Failed to create timestamp %r: %s" % (timestamp_file_path, exp))
            sys.exit(1)

ots_stamp(sys.argv[1:])
