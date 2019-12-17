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
import urllib.request

from bitcoin.core import b2x, b2lx
from opentimestamps.bitcoin import BitcoinBlockHeaderAttestation
from opentimestamps.core.notary import PendingAttestation
from opentimestamps.core.timestamp import DetachedTimestampFile, make_merkle_tree
from opentimestamps.core.timestamp import OpAppend, OpSHA256, Timestamp
from opentimestamps.core.serialize import StreamSerializationContext, BadMagicError
from opentimestamps.core.serialize import StreamDeserializationContext, DeserializationError
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



def is_timestamp_complete(stamp):
    """Determine if timestamp is complete and can be verified"""

    for _, attestation in stamp.all_attestations():
        if attestation.__class__ == BitcoinBlockHeaderAttestation:
            # FIXME: we should actually check this attestation, rather than
            # assuming it's valid
            return True

    return False



def get_attestations_list(stamp):
    """Determine if timestamp is complete and can be verified"""

    att_list = []
    for msg, attestation in stamp.all_attestations():
        if attestation.__class__ == BitcoinBlockHeaderAttestation:
            # FIXME: we should actually check this attestation, rather than
            # assuming it's valid
            ret = (int(attestation.height), b2lx(msg))
            att_list.append(ret)

    return att_list



def upgrade_timestamp(timestamp):
    """Attempt to upgrade an incomplete timestamp to make it verifiable

    Returns True if the timestamp has changed, False otherwise.

    Note that this means if the timestamp that is already complete, False will
    be returned as nothing has changed.
    """

    def directly_verified(stamp):
        if stamp.attestations:
            yield stamp
        else:
            for result_stamp in stamp.ops.values():
                yield from directly_verified(result_stamp)
        yield from ()

    def get_attestations(stamp):
        #return set(attest for msg, attest in stamp.all_attestations())
        return set(attest for _, attest in stamp.all_attestations())


    changed = False
    existing_attestations = get_attestations(timestamp)
    if not is_timestamp_complete(timestamp):
        # Check remote calendars for upgrades.
        #
        # This time we only check PendingAttestations - we can't be as
        # agressive.
        for sub_stamp in directly_verified(timestamp):
            for attestation in sub_stamp.attestations:
                if attestation.__class__ == PendingAttestation:
                    commitment = sub_stamp.msg
                    #for calendar_url in calendar_urls:
                    for calendar_url in [attestation.uri]:
                        logging.debug("Checking calendar %s for %s" % (attestation.uri, b2x(commitment)))
                        calendar = remote_calendar(calendar_url)

                        try:
                            upgraded_stamp = calendar.get_timestamp(commitment)
                        except opentimestamps.calendar.CommitmentNotFoundError as exp:
                            logging.warning("Calendar %s: %s" % (attestation.uri, exp.reason))
                            continue
                        except urllib.error.URLError as exp:
                            logging.warning("Calendar %s: %s" % (attestation.uri, exp.reason))
                            continue

                        atts_from_remote = get_attestations(upgraded_stamp)
                        if atts_from_remote:
                            logging.info("Got %d attestation(s) from %s" % (len(atts_from_remote), calendar_url))
                            for att in get_attestations(upgraded_stamp):
                                logging.debug("    %r" % att)

                        new_attestations = get_attestations(upgraded_stamp).difference(existing_attestations)
                        if new_attestations:
                            changed = True
                            existing_attestations.update(new_attestations)

                            # FIXME: need to think about DoS attacks here
                            #args.cache.merge(upgraded_stamp)
                            sub_stamp.merge(upgraded_stamp)


    return changed







def ots_upgrade(filename):
    ''' upgrade function '''

    logging.debug("Upgrading %s" % filename)

    try:
        with open(filename, 'rb') as old_stamp_fd:
            ctx = StreamDeserializationContext(old_stamp_fd)
            detached_timestamp = DetachedTimestampFile.deserialize(ctx)

    # IOError's are already handled by argparse
    except BadMagicError:
        logging.error("Error! %r is not a timestamp file" % filename)
        raise
    except DeserializationError as exp:
        logging.error("Invalid timestamp file %r: %s" % (filename, exp))
        raise

    changed = upgrade_timestamp(detached_timestamp.timestamp)

    if changed:
        try:
            with open(old_stamp_fd.name, 'wb') as new_stamp_fd:
                ctx = StreamSerializationContext(new_stamp_fd)
                detached_timestamp.serialize(ctx)
        except IOError as exp:
            logging.error("Could not upgrade timestamp %s: %s" % (old_stamp_fd.name, exp))
            raise

    if is_timestamp_complete(detached_timestamp.timestamp):
        logging.info("Success! Timestamp complete")
        return ('UPGRADED', get_attestations_list(detached_timestamp.timestamp))

    logging.warning("Failed! Timestamp not complete")
    return (None, None)



if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    #ots_stamp(sys.argv[1:], min_resp=DEF_MIN_RESP, timeout=DEF_TIMEOUT)
    ots_upgrade(sys.argv[1])
