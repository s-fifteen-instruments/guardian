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


import os
import sys
import time


class notifierClient:
    """foo
    """
    EPOCH_FILES_DIRPATH: str = "/epoch_files"
    EPOCH_DELAY_INTERVAL: float = 2**29 / 1E9  # One qcrypto epoch
    NOTIFY_PIPE_FILEPATH: str = "/epoch_files/notify.pipe"

    def __init__(self):
        """foo
        """
        try:
            os.mkfifo(notifierClient.NOTIFY_PIPE_FILEPATH)
        except OSError:
            print(f"FIFO {notifierClient.NOTIFY_PIPE_FILEPATH} already exists")
        epoch_file_list = list(self.list_epoch_files())
        if len(epoch_file_list) > 0:
            with open(notifierClient.NOTIFY_PIPE_FILEPATH, "w") as FIFO:
                num_epoch_delay: int = 0
                last_file_hex: int = hex(0)
                for epoch_file_name in epoch_file_list:
                    current_file_hex = int(epoch_file_name, 16)
                    if last_file_hex == hex(0):
                        last_file_hex = current_file_hex
                    num_epoch_delay = 1  # int(current_file_hex - last_file_hex)
                    print(num_epoch_delay, epoch_file_name, file=sys.stderr)
                    FIFO.write(epoch_file_name + "\n")
                    FIFO.flush()
                    time.sleep(notifierClient.EPOCH_DELAY_INTERVAL * num_epoch_delay)
                    last_file_hex = current_file_hex
        else:
            print("No files to notify about", file=sys.stderr)

    def list_epoch_files(self):
        """foo
        """
        all_files = sorted(os.listdir(notifierClient.EPOCH_FILES_DIRPATH))
        for file in all_files:
            if not file.startswith(".") and not file.endswith(".pipe"):
                yield file


if __name__ == "__main__":
    notifier = notifierClient()
