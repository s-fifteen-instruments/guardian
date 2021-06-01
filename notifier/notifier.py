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


import logging as logger
import os
import sys
import time

from notifier_config import settings


logger.basicConfig(stream=sys.stdout, level=logger.DEBUG)


class NotifierClient:
    """foo
    """

    def __init__(self):
        """foo
        """
        try:
            os.mkfifo(settings.NOTIFY_PIPE_FILEPATH)
        except OSError:
            logger.info(f"FIFO {settings.NOTIFY_PIPE_FILEPATH} already exists")
        epoch_file_list = list(self.list_epoch_files())
        if len(epoch_file_list) > 0:
            with open(settings.NOTIFY_PIPE_FILEPATH, "w") as FIFO:
                num_epoch_delay: int = 0
                last_file_hex: int = hex(0)
                for epoch_file_name in epoch_file_list:
                    current_file_hex = int(epoch_file_name, 16)
                    if last_file_hex == hex(0):
                        last_file_hex = current_file_hex
                    num_epoch_delay = 0
                    if settings.REAL_TIME_DELAY:
                        num_epoch_delay = int(current_file_hex - last_file_hex)
                    logger.info(f"Notification Delay [s]: {num_epoch_delay * settings.EPOCH_DELAY_INTERVAL}; "
                                f"Epoch Filename: {epoch_file_name}")
                    FIFO.write(epoch_file_name + "\n")
                    FIFO.flush()
                    time.sleep(settings.EPOCH_DELAY_INTERVAL * num_epoch_delay)
                    last_file_hex = current_file_hex
        else:
            logger.info("No files to notify about")

    def list_epoch_files(self):
        """foo
        """
        all_files = sorted(os.listdir(settings.EPOCH_FILES_DIRPATH))
        for file in all_files:
            if not file.startswith(".") and not file.endswith(".pipe"):
                yield file


if __name__ == "__main__":
    notifier = NotifierClient()
