#!/usr/bin/env python3
"""Emulates QKDServer key and notification output.

'localconn' and 'remoteconn' are typically supplied, to provide a
deterministic way of deciding which direction the key should go, i.e.
the ledger from A to B, or the other way around.

Notifications 'notifypipe' and 'notifyfile' will not be written to unless
their paths are supplied. Paths will be relative to 'epochdir', but can
also be absolute paths. If 'epochdir' is not specified, the current
working directory will be used.

If 'seed' is not provided, a random seed will be used for generating keys.
The starting 'epoch' (in hex), number of epochs per keyfile 'length', as
well as the desired 'bitrate' can be supplied. Note that the script
always write the first keyfile immediately (i.e. the bits for the first
keyfile is assumed to already have been generated), before performing
the expected waiting time.

Examples:
    python3 ./simulate_keygen.py --localconn QKDA --remoteconn QKB

Changelog:
    2023-10-26 Justin: Init
"""

import datetime as dt
import itertools
import logging
import os
import struct
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import configargparse
import numpy as np
from fpfind.lib import parse_epochs as eparser

logger = logging.getLogger(__name__)

handler = logging.StreamHandler(stream=sys.stderr)
handler.setFormatter(
    logging.Formatter(
        fmt="{asctime}\t{levelname:<s}\t{funcName}:{lineno} | {message}",
        datefmt="%Y%m%d_%H%M%S",
        style="{",
    )
)
logger.addHandler(handler)
logger.propagate = False

EPOCH_DURATION = (1 << 29) * 1e-9  # in seconds
STREAM_TAG = 0x007


def generate_stream7(epoch, length, bitsize):
    header = struct.pack("IIII", STREAM_TAG, epoch, length, bitsize)
    num_words = (bitsize + 31) // 32
    if num_words == 0:
        return header

    # Generate bits
    data = np.random.randint(1 << 32, dtype=np.uint32, size=num_words)

    # Zero unused bits
    last_byte_mask = ~np.uint32((1 << (-bitsize % 32)) - 1)
    data[-1] &= last_byte_mask
    return header + data.tobytes()

@contextmanager
def singleuse():
    yield

def main(args):
    # Initialize script parameters
    if args.seed is not None:
        np.random.seed(args.seed)

    file_duration = args.length * EPOCH_DURATION
    file_bits = int(args.bitrate * file_duration)
    curr_epochint = eparser.epoch2int(args.epoch)
    keydirection = int(args.localconn <= args.remoteconn)

    # Open pipe
    if args.notifypipe is not None:
        fd = os.open(args.notifypipe, os.O_WRONLY)
        notifypipe = os.fdopen(fd, "w")
    else:
        notifypipe = singleuse()

    # Open file
    if args.notifyfile is not None:
        notifyfile = open(args.notifyfile, "a+")
    else:
        notifyfile = singleuse()

    # Catch user exception
    try:
        with notifypipe, notifyfile:

            # Specify number of loops
            geniter = itertools.count()
            if args.single:
                geniter = [0]

            # Start loop
            start_time = time.time()
            for num_elapsed_files in geniter:

                # Wait for next epoch
                end_time = start_time + num_elapsed_files * file_duration
                curr_time = time.time()
                while curr_time < end_time:
                    time.sleep(end_time - curr_time + EPOCH_DURATION)  # within next duration
                    curr_time = time.time()

                # Time to spit out some bits
                epoch = eparser.int2epoch(curr_epochint)
                contents = generate_stream7(curr_epochint, args.length, file_bits)

                # Output
                with open(args.epochdir / epoch, "wb") as f:
                    f.write(contents)

                notification = f"{epoch} {args.remoteconn} {keydirection}\n"
                if args.notifypipe is not None:
                    notifypipe.write(notification)
                    notifypipe.flush()
                if args.notifyfile is not None:
                    notifyfile.write(notification)
                    notifyfile.flush()
                logger.debug(f"Wrote '{file_bits}' key bits for file '{epoch}'")

                # Update for next iteration
                curr_epochint += args.length
                keydirection = 1 - keydirection

    except KeyboardInterrupt:
        logger.info("User terminated.")
    except BrokenPipeError:
        logger.error("Notification pipe closed prematurely.")

def check_args(args):
    # Verify paths
    if args.epochdir is not None:
        args.epochdir = Path(args.epochdir)

        # Assume the directory already exists
        if not args.epochdir.exists():
            raise ValueError(
                f"'{args.epochdir}' is not a valid directory path."
            )
    else:
        args.epochdir = Path()  # local directory

    # Verify notification pipe
    if args.notifypipe is not None:
        args.notifypipe = args.epochdir / args.notifypipe
        if not args.notifypipe.exists():
            os.mkfifo(str(args.notifypipe))

    # Parse notification file path
    if args.notifyfile is not None:
        args.notifyfile = args.epochdir / args.notifyfile

    # Set epoch to current datetime
    if args.epoch is None:
        args.epoch = eparser.date2epoch(dt.datetime.now())

    # Check size of epoch length
    if args.length <= 0:
        raise ValueError("Number of epochs per keyfile should be positive.")

    # Check local and remote conn
    if args.localconn == args.remoteconn:
        logger.warning(
            f"Local and remote connection IDs are the same: '{args.localconn}'"
        )

    # Set logging level
    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    logger.setLevel(levels[args.verbose])


if __name__ == "__main__":
    filename = Path(__file__).name
    parser = configargparse.ArgumentParser(
        default_config_files=[f"{filename}.default.conf"],
        description=__doc__.partition("\n")[0],
    )

    # Boilerplate
    parser.add_argument(
        "--config", is_config_file_arg=True,
        help="Path to configuration file")
    parser.add_argument(
        "--save", is_write_out_config_file_arg=True,
        help="Path to configuration file for saving, then immediately exit")
    parser.add_argument(
        "--verbose", "-v", action="count", default=0,
        help="Specify debug verbosity, e.g. -vv for more verbosity")
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress errors, but will not block logging")

    # Script arguments
    parser.add_argument(
        "--seed", type=int,
        help="Sets the initial seed for random number generation")
    parser.add_argument(
        "--epoch",
        help="Sets the initial epoch filename, defaults to current datetime")
    parser.add_argument(
        "--length", type=int, default=1,
        help="Determines the number of epochs to be used per keyfile")
    parser.add_argument(
        "--bitrate", type=int, default=1000,
        help="Sets the desired overall keyrate in bits/s")
    parser.add_argument(
        "--epochdir",
        help="Specifies the directory to write epoch key files into")
    parser.add_argument(
        "--notifypipe",
        help="Specifies the pipe in the output directory to write epoch names into")
    parser.add_argument(
        "--notifyfile",
        help="Specifies the file in the output directory to write epoch names into. "
             "Used in guardian for when watcher restarts")
    parser.add_argument(
        "--localconn", default="QKDE0001",
        help="Specifies the local connection ID to assign key to, e.g. QKDE0001")
    parser.add_argument(
        "--remoteconn", default="QKDE0001",
        help="Specifies the remote connection ID to assign key to, e.g. QKDE0002. "
             "Used to decide which direction the first key file should go to")
    parser.add_argument(
        "--single", action="store_true",
        help="Generate only for one epoch and exit")

    # Arguments
    if len(sys.argv) > 1:
        args = parser.parse_args()
        check_args(args)
        main(args)

