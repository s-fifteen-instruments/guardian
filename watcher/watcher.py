#!/usr/bin/env python
#
# Guardian is a quantum key distribution REST API and supporting software stack.
# Copyright (C) 2021  W. Cyrus Proctor
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#

import concurrent.futures as cf
import errno
import logging as logger
# import getpass
import multiprocessing
import os
import signal
# import socket
import sys
import struct
import time
import traceback

# Consider https://documentation.solarwinds.com/en/success_center/papertrail/content/kb/configuration/configuring-centralized-logging-from-python-apps.htm?cshid=pt-configuration-configuring-centralized-logging-from-python-apps
# hostname = socket.gethostname()
# user = user = getpass.getuser()
logger.basicConfig(stream=sys.stdout, level=logger.DEBUG)  # ,
#                    format="%(levelname)s " +
#                    "%(threadName)s " +
#                    f"{hostname}: " +
#                    f"{user}: " +
#                    "%(asctime)s: " +
#                    "%(filename)s;" +
#                    "%(funcName)s();" +
#                    "%(lineno)d: " +
#                    "%(message)s")


class watcherClient:
    DELETE_EPOCH_FILES: bool = False
    EPOCH_FILES_DIRPATH: str = "/epoch_files"
    NOTIFY_PIPE_FILEPATH: str = f"{EPOCH_FILES_DIRPATH}/notify.pipe"
    KILL_NOW: bool = False
    BACKOFF_FACTOR: float = 1.0
    BACKOFF_MAX: float = 8.0
    MAX_NUM_ATTEMPTS: int = 100
    NOTIFY_SLEEP_TIME: float = 0.5  # seconds
    NOTIFY_SLEEP_TIME_DELTA: float = 30.0  # seconds

    def __init__(self, threads: int = None):
        """foo
        """
        # Shut down gracefully with a SIGINT or SIGTERM
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        # Default to thread count equal to number of CPU cores
        if not threads:
            threads = multiprocessing.cpu_count()
        self._threads = threads
        # Initialize a concurrent futures threadpool
        self.executor = cf.ThreadPoolExecutor(max_workers=self._threads)
        self.mainloop()

    def exit_gracefully(self, signum, frame):
        """foo
        """
        logger.info("Signal Caught...Shutting Down")
        self.KILL_NOW = True
        for exception in self.exception_list:
            logger.warn(f"Exception occurred when processing file: {exception}")
        # Wait for currently executing threads to finish
        self.executor.shutdown(wait=True)
        logger.debug("All currently executing threads have finished")

    @staticmethod
    def read_epoch_file(filepath):
        """foo
        """
        try:
            with open(filepath, "rb") as efh:
                raw_file = efh.read()
            logger.debug(f"Filename: {filepath}: Successfully read in")
        except Exception as e:
            logger.error(f"Filename: {filepath}: Unexpected I/O read error: {e}")
            raise e

        return raw_file

    @staticmethod
    def parse_epoch_file_contents(filepath, raw_file):
        """foo
        """
        # Header should be the first 16 bytes of type 7 epoch file
        # native byte order, int, unsigned int, unsigned int, int
        file_tag, start_epoch, num_epochs, num_valid_key_bits = \
            struct.unpack('=iIIi', raw_file[:16])
        # Raw key is everything after the first 16 bytes
        raw_key = raw_file[16:]
        logger.debug(f"Filename: {filepath}; File Tag: {file_tag}; "
                     f"Start Epoch {start_epoch:x}; "
                     f"Number of Epochs: {num_epochs}; "
                     f"Number of Key Bits: {num_valid_key_bits}; "
                     f"Raw Key Size {len(raw_key)} bytes")
        # Key bytestream from qcrypto packaged in 32-bit (4-byte) words
        assert len(raw_key) % 4 == 0
        num_raw_key_bits: int = len(raw_key) * 8  # bytes to bits
        # Integer division
        num_raw_key_32bit_words: int = len(raw_key) // 4
        assert 0 <= num_raw_key_bits >= num_valid_key_bits
        num_raw_key_padding_bits: int = num_raw_key_bits - num_valid_key_bits
        assert 0 <= num_raw_key_padding_bits <= 31
        key_word_list = list()
        # Read in each 32-bit word into a zero padded 32-bit binary string
        for key_word in struct.unpack(f"{num_raw_key_32bit_words}I", raw_key):
            key_word_list.append(f"{key_word:032b}")
        # TODO: Key exposure
        logger.debug(f"Number of padding bits: {num_raw_key_padding_bits}")
        logger.debug(f"Last Key Word: {key_word_list[-1][:]}")
        logger.debug(f"Padding bits: {key_word_list[-1][-num_raw_key_padding_bits:]}")
        # Remove the padding bits from the last 4-byte word (if any; 0 okay)
        key_word_list[-1] = key_word_list[-1][:32 - num_raw_key_padding_bits]
        logger.debug(f"Last Key Word (Padding Removed): {key_word_list[-1][:]}")
        # Combine all list elements into one string with no delimeters
        key_str = "".join(key_word_list)

        return key_str

    @staticmethod
    def delete_epoch_file(filepath):
        """foo
        """
        try:
            if watcherClient.DELETE_EPOCH_FILES:
                os.remove(filepath)
                logger.debug(f"Filename: {filepath}; successfully deleted")
            else:
                logger.debug(f"Filename: {filepath}; remains due to configuration settings")
        except OSError as e:
            # No such file or directory
            if e.errno == errno.ENOENT:
                logger.warning(f"Attempt Delete: Filename: {filepath} does not exist")
            else:
                logger.error(f"Attempt Delete: Filename: {filepath}: unexpected error: {e}")
                raise e

    @staticmethod
    def process_epoch_file(filepath):
        """foo
        """
        logger.debug(f"Worker started on Filename: {filepath}")
        raw_file = watcherClient.read_epoch_file(filepath)
        key_str = watcherClient.parse_epoch_file_contents(filepath, raw_file)
        watcherClient.delete_epoch_file(filepath)

        return {f"{filepath}": True}

    def mainloop(self):
        """foo
        """
        # Initialization
        self.backoff_factor: float = watcherClient.BACKOFF_FACTOR
        self.backoff_max: float = watcherClient.BACKOFF_MAX
        self.max_num_attempts: int = watcherClient.MAX_NUM_ATTEMPTS
        attempt_num: int = 0
        total_stall_time: float = 0.0
        total_notify_sleep_time: float = 0.0
        notify_sleep_iteration_count: int = 0
        # Worker pool
        workers = {}
        # Exception list
        self.exception_list = list()
        # Watch for notifications unless max attempts has been reached waiting
        # for the creation of the notify pipe or a signal was received to stop
        while not self.KILL_NOW and attempt_num < self.max_num_attempts:
            # Keep track of number of attemps to open notify pipe
            attempt_num = attempt_num + 1
            # Exponential backoff waiting for notificaiton pipe
            stall_time: float = self.backoff_factor * (2 ** (attempt_num - 1))
            # Don't exceed max backoff
            stall_time = min(self.backoff_max, stall_time)
            # Keep track of total stall time waiting on notify pipe creation
            total_stall_time = total_stall_time + stall_time
            try:
                # Attempt to open the notify pipe read-only, non-blocking
                with open(os.open(watcherClient.NOTIFY_PIPE_FILEPATH,
                                  os.O_NONBLOCK | os.O_RDONLY)) as FIFO:
                    logger.debug(f"{watcherClient.NOTIFY_PIPE_FILEPATH} opened read-only, non-blocking")
                    # Notify pipe was successfully opened; iterate until otherwise
                    while not self.KILL_NOW:
                        # Break out of inner loop if notify pipe no longer exists
                        if not os.path.exists(watcherClient.NOTIFY_PIPE_FILEPATH):
                            logger.info(f"{watcherClient.NOTIFY_PIPE_FILEPATH} does not exist. Retrying...")
                            break
                        if total_notify_sleep_time > \
                           watcherClient.NOTIFY_SLEEP_TIME_DELTA * \
                           notify_sleep_iteration_count:
                            notify_sleep_iteration_count += 1
                            logger.debug(f"Sleeping until notification; Total Time Slept: {total_notify_sleep_time:.1f} seconds")
                        # Attempt to read a line from the notify pipe
                        data = FIFO.readline().strip("\n")
                        # We found data in the notify pipe
                        if data:
                            # Rest our attempt counter and timers
                            attempt_num = 0
                            notify_sleep_iteration_count = 0
                            total_stall_time = 0.0
                            total_notify_sleep_time = 0.0
                            # Data should point us to a final key epoch filename
                            epoch_filepath = f"{watcherClient.EPOCH_FILES_DIRPATH}/{data}"
                            # Name of thread worker callback function and argument filepath
                            args = (watcherClient.process_epoch_file,
                                    epoch_filepath)
                            logger.debug(f"Filename submitted to worker threadpool: {epoch_filepath}")
                            # Submit the filepath to a worker thread for processing
                            workers[self.executor.submit(*args)] = epoch_filepath
                        # No data is in the notify pipe at this time
                        else:
                            start_time = time.time()
                            # Attempt to process any already completed worker threads
                            for future in cf.as_completed(workers):
                                try:
                                    result = future.result()
                                    logger.info(f"Filename: {workers[future]}; Worker result: {result}")
                                # Something happened to a worker thread
                                except Exception:
                                    logger.warning(f"Worker for: {workers[future]} generated an exception: {traceback.print_exc()}")
                                    self.exception_list.append(workers[future])

                                logger.debug(f"Removing worker: {workers[future]} from threadpool")
                                # Remove the completed future from our worker pool
                                del workers[future]

                            end_time = time.time()
                            # Sleep for a bit and then recheck the notify pipe
                            notify_sleep_time = max(0, watcherClient.NOTIFY_SLEEP_TIME - (end_time - start_time))
                            time.sleep(notify_sleep_time)
                            total_notify_sleep_time += notify_sleep_time

            except FileNotFoundError:
                logger.info(f"FIFO not found; Sleep time {stall_time}; Attempt Number: {attempt_num}/{self.max_num_attempts}: Total Stall Time: {total_stall_time} s")
                time.sleep(stall_time)


if __name__ == "__main__":
    watcher = watcherClient()
