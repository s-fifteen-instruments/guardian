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
import signal
import sys
import time


class watcherClient:
    NOTIFY_PIPE_FILEPATH: str = "/epoch_files/notify.pipe"
    KILL_NOW: bool = False
    BACKOFF_FACTOR: float = 1.0
    BACKOFF_MAX: float = 8.0
    MAX_NUM_ATTEMPTS: int = 100

    def __init__(self):
        """foo
        """
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.mainloop()

    def exit_gracefully(self, signum, frame):
        """foo
        """
        print("Signal Caught...Shutting Down.", file=sys.stderr)
        self.KILL_NOW = True

    def mainloop(self):
        """foo
        """
        self.backoff_factor: float = watcherClient.BACKOFF_FACTOR
        self.backoff_max: float = watcherClient.BACKOFF_MAX
        self.max_num_attempts: int = watcherClient.MAX_NUM_ATTEMPTS
        attempt_num: int = 0
        total_stall_time: float = 0.0
        while not self.KILL_NOW and attempt_num < self.max_num_attempts:
            attempt_num = attempt_num + 1
            stall_time: float = self.backoff_factor * (2 ** (attempt_num - 1))
            stall_time = min(self.backoff_max, stall_time)
            total_stall_time = total_stall_time + stall_time
            # print(f"Sleeping for {stall_time} seconds", file=sys.stderr)
            # print("Restarting", file=sys.stderr)
            try:
                # print("Opening FIFO read-only non-blocking...", file=sys.stderr)
                with open(os.open(watcherClient.NOTIFY_PIPE_FILEPATH,
                                  os.O_NONBLOCK | os.O_RDONLY)) as FIFO:
                    # print(f"{watcherClient.NOTIFY_PIPE_FILEPATH} is now opened", file=sys.stderr)
                    while not self.KILL_NOW:
                        if not os.path.exists(watcherClient.NOTIFY_PIPE_FILEPATH):
                            print(f"{watcherClient.NOTIFY_PIPE_FILEPATH} does not exist. Retrying...")
                            break
                        data = FIFO.readline().strip("\n")
                        if not data:
                            time.sleep(0.5)
                        else:
                            attempt_num = 0
                            total_stall_time = 0.0
                            print(f"The DATA: {data}", file=sys.stderr)
            except FileNotFoundError:
                print(f"FIFO not found; Sleep time {stall_time}; Attempt Number: {attempt_num}/{self.max_num_attempts}: Total Stall Time: {total_stall_time} s", file=sys.stderr)
                time.sleep(stall_time)


if __name__ == "__main__":
    watcher = watcherClient()
