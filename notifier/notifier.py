#!/usr/bin/env python

import os
import sys
import time


class notifierClient:
    EPOCH_FILES_DIRPATH: str = "/epoch_files"
    EPOCH_DELAY_INTERVAL: float = 2**29 / 1E9  # One qcrypto epoch
    NOTIFY_PIPE_FILEPATH: str = "/epoch_files/notify.pipe"

    def __init__(self):
        try:
            os.mkfifo(notifierClient.NOTIFY_PIPE_FILEPATH)
        except OSError as e:
            print(f"Failed to create FIFO {notifierClient.NOTIFY_PIPE_FILEPATH}: {e}")
        with open(notifierClient.NOTIFY_PIPE_FILEPATH, "w") as FIFO:
            num_epoch_delay: int = 0
            last_file_hex: int = hex(0)
            for epoch_file_name in self.list_epoch_files():
                current_file_hex = int(epoch_file_name, 16)
                if last_file_hex == hex(0):
                    last_file_hex = current_file_hex
                num_epoch_delay = 1  # int(current_file_hex - last_file_hex)
                FIFO.write(epoch_file_name + "\n")
                FIFO.flush()
                print(num_epoch_delay, epoch_file_name, file=sys.stderr)
                time.sleep(notifierClient.EPOCH_DELAY_INTERVAL * num_epoch_delay)
                last_file_hex = current_file_hex

    def list_epoch_files(self):
        """foo
        """
        all_files = sorted(os.listdir(notifierClient.EPOCH_FILES_DIRPATH))
        for file in all_files:
            if not file.startswith(".") and not file.endswith(".pipe"):
                yield file


if __name__ == "__main__":
    notifier = notifierClient()
