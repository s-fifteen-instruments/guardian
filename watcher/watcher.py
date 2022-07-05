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

import base64
import concurrent.futures as cf
import errno
import hashlib
import hmac
import hvac
import json
import logging as logger
import multiprocessing
import os
import pathlib
import signal
import sys
import struct
import time
import traceback

from watcher_config import settings

logger.basicConfig(stream=sys.stdout, level=int(settings.WATCHER_LOG_LEVEL))


class watcherClient:

    def __init__(self, threads: int = None):
        """foo
        """
        # Shut down gracefully with a SIGINT or SIGTERM
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.KILL_NOW: bool = False
        # Default to thread count equal to number of CPU cores
        if not threads:
            threads = multiprocessing.cpu_count()
        self._threads = threads
        # Initialize a concurrent futures threadpool
        self.executor = \
            cf.ThreadPoolExecutor(max_workers=self._threads,
                                  thread_name_prefix=self.__class__.__name__)
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

    def vault_client_auth(self):
        """foo
        """
        try:
          if self.vclient.is_authenticated():
              logger.debug("Vault client already authenticated.")
              return None
        except AttributeError:
            logger.info("No Vault client created yet; creating")

        self.vclient: hvac.Client = \
            hvac.Client(url=settings.GLOBAL.VAULT_SERVER_URL,
                        cert=(settings.CLIENT_CERT_FILEPATH,
                              settings.CLIENT_KEY_FILEPATH),
                        verify=settings.GLOBAL.SERVER_CERT_FILEPATH)
        mount_point = "cert"
        logger.debug("Attempt TLS client login")
        #auth_response = self.vclient.auth_tls(mount_point=mount_point,
        #                                      use_token=False)
        self.vclient.adapter = mount_point
        auth_response = self.vclient.auth.cert.login()
        logger.debug("Vault auth response:")
        self._dump_response(auth_response, secret=True)
        self.vclient.token = auth_response["auth"]["client_token"]
        self.vclient.lease_end = auth_response["auth"]["lease_duration"] + time.time()
        if self.vclient.is_authenticated():
            logger.info(f"\"{settings.CLIENT_NAME}\" is now authenticated")
        else:
            logger.info(f"\"{settings.CLIENT_NAME}\" has failed to authenticate")

    def vault_can_create_new_keys(self, full_filepath: str):
        """foo
        """
        can_create_new_keys = False
        logger.debug(f"Attempt to query Vault self capabilities on "
                     f"full_filepath: {full_filepath}")
        cap_response = \
            self.vclient.sys.get_capabilities(paths=full_filepath)
        logger.debug(f"full_filepath: {full_filepath} capabilities response:")
        self._dump_response(cap_response, secret=False)
        capabilities = cap_response["data"][full_filepath]
        if "create" in capabilities:
            can_create_new_keys = True

        return can_create_new_keys

    def vault_get_current_secret_version(self, filepath: str, mount_point: str):
        """foo
        """
        secret_version = -1
        logger.debug(f"Attempt to query Vault secret version on "
                     f"filepath: {filepath}; mount_point: {mount_point}")
        try:
            metadata_response = \
                self.vclient.secrets.kv.v2.\
                read_secret_metadata(path=filepath,
                                     mount_point=mount_point)
        except hvac.exceptions.InvalidPath:
           logger.debug("There is no secret yet at filepath: "
                        f"{filepath}; mount_point: {mount_point}")
           secret_version = 0
        else:
            logger.debug(f"filepath: {filepath} version response:")
            self._dump_response(metadata_response, secret=False)
            version_keys = sorted(list(map(int, metadata_response["data"]["versions"].keys())))
            max_version = max(version_keys)
            current_version = int(metadata_response["data"]["current_version"])
            logger.debug(f"Available Secret Versions: {','.join(map(str, version_keys))}; Max Version: {max_version}; Current Version: {current_version}")
            secret_version = current_version

        return secret_version

    def vault_get_secret_metadata(self):
        pass

    @staticmethod
    def _is_json(response):
        """foo
        """
        try:
            json.loads(response)
        except ValueError:
            return False
        except TypeError as e:
            if str(e).find("dict") != -1:
                return True
        return True

    @staticmethod
    def _dump_response(response, secret: bool = True):
        """foo
        """
        if not secret or settings.GLOBAL.SHOW_SECRETS:
            if response:
                if watcherClient._is_json(response):
                    logger.debug(f"""{json.dumps(response,
                                                 indent=2,
                                                 sort_keys=True)}""")
                else:
                    logger.debug(f"{response}")
            else:
                logger.debug("No response")
        else:
            logger.debug("REDACTED")

    @staticmethod
    def read_epoch_file(filepath):
        """foo
        """
        # Ensure raw_bytes is defined
        raw_bytes = bytes()
        try:
            with open(filepath, "rb") as efh:
                raw_bytes = efh.read()
        except Exception as e:
            logger.error(f"Filename: {filepath}: Unexpected I/O read error: {e}")
            raise e
        else:
            logger.debug(f"Filename: {filepath}: Successfully read in")

        return raw_bytes

    @staticmethod
    def parse_raw_key_bytes(filepath, raw_file):
        """foo
        """
        # Header should be the first 16 bytes of type 7 epoch file
        # native byte order, int, unsigned int, unsigned int, int
        file_tag, start_epoch, num_epochs, num_valid_key_bits = \
            struct.unpack('=iIIi', raw_file[:16])
        assert file_tag == 7  # qcrypto local epoch
        assert filepath.find(f"{start_epoch:x}") != -1
        # Raw key is everything after the first 16 bytes
        # Drop the last 4-byte word that could have non-key zero padding
        # Files with lengths of 0 or 1 32-bit word should get a raw_key size of 0
        raw_key = raw_file[16:-4]
        assert len(raw_key) == max(0, ((num_valid_key_bits + 31) // 32) * 4 - 4)
        logger.debug(f"Filename: {filepath}; "
                     f"File Tag: {file_tag}; "
                     f"Start Epoch: {start_epoch:x}; "
                     f"Number of Epochs: {num_epochs}; "
                     f"Number of Key Bits: {num_valid_key_bits}; "
                     f"Trucated Raw Key Size: {len(raw_key)} bytes")

        return filepath.split("/")[-1], raw_key

    @staticmethod
    def delete_epoch_file(filepath):
        """foo
        """
        try:
            if settings.DELETE_EPOCH_FILES:
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
    def compute_hmac_hexdigest(message: bytes) -> str:
        """foo
        """
        # Compute the hash-based message authentication code of the
        # raw key using a SHA3 512-bit hash.
        mac = hmac.new(key=settings.GLOBAL.DIGEST_KEY,
                       digestmod=hashlib.sha3_512)
        mac.update(message)
        message_hexdigest = mac.hexdigest()
        logger.debug(f"Hex Digest: {message_hexdigest}")

        return message_hexdigest

    @staticmethod
    def write_hexdigest(hexdigest: str, filepath: str):
        """foo
        """
        logger.debug(f"Writing hexdigest to filepath: {filepath}")
        with open(filepath, "w") as f:
            f.write(hexdigest)

    @staticmethod
    def read_hexdigest(filepath: str) -> str:
        """foo
        """
        logger.debug(f"Reading hexdigest to filepath: {filepath}")
        hexdigest = open(filepath, "r").read()
        return hexdigest

    def vault_write_key(self, epoch: str, raw_key: bytes):
        """foo
        """
        cas_error = False
        mount_point = settings.GLOBAL.VAULT_KV_ENDPOINT
        qkey_path = f"{settings.GLOBAL.VAULT_QKDE_ID}/" \
            f"{settings.GLOBAL.VAULT_QCHANNEL_ID}/" \
            f"{epoch}"
        full_path = f"{mount_point}/data/{qkey_path}"

        # Query Vault to ensure we can create new keys at this path
        can_create_new_keys = \
            self.vault_can_create_new_keys(full_filepath=full_path)
        # Query Vault to check the version metadata at this path (should be none)
        qkey_version = \
            self.vault_get_current_secret_version(filepath=qkey_path,
                                                  mount_point=mount_point)

        # We do not have permission to create new keys at this vault path
        if not can_create_new_keys:
            logger.warning("Permission Denied to write new keys; "
                           f"Epoch: {epoch}; Vault Path: {full_path}; "
                           "Abondoning Creation Write Attempt")

        # There is (unexpectedly) already a key at this vault path
        elif qkey_version != 0:
            logger.warning("A version of keying material already exists "
                           f"for epoch: \"{epoch}\"; version: {qkey_version}; "
                           "Abandoning Key Creation Attempt")

        # We have permission to create new keys on this vault path
        # and there is no keying material as of the previous query.
        # Still use check-and-set = 0 to avoid race conditions.
        else:

            # Compute the HMAC hexdigest of the raw key
            logger.debug(f"Compute the HMAC hexdigest of epoch key: \"{epoch}\":")
            key_hexdigest = watcherClient.compute_hmac_hexdigest(raw_key)
            # Ensure the digest directory exists; make it if not
            pathlib.Path(f"{settings.GLOBAL.DIGEST_FILES_DIRPATH}").mkdir(parents=True, exist_ok=True)
            # Write out the hexdigest to a file for later comparison
            digest_filepath = f"{settings.GLOBAL.DIGEST_FILES_DIRPATH}/" \
                f"{epoch}.digest"
            watcherClient.write_hexdigest(key_hexdigest, digest_filepath)
            # Base64 encode the raw bytes and decode the resulting byte
            # stream into UTF-8 for safe transporting/storage
            secret_dict = {
                "key": base64.standard_b64encode(raw_key).decode("UTF-8"),
                "digest": key_hexdigest,
                "bytes": str(len(raw_key)),
                "epoch": str(epoch)
            }
            logger.debug(f"Attempt to write epoch \"{epoch}\" key to Vault")
            try:
                qkey_response = \
                    self.vclient.secrets.kv.v2.\
                    create_or_update_secret(path=qkey_path,
                                            secret=secret_dict,
                                            cas=0,  # Enforce only key creation
                                            mount_point=mount_point)
                logger.debug(f"Vault write epoch \"{epoch}\" key response:")
                self._dump_response(qkey_response, secret=False)
            except hvac.exceptions.InvalidRequest as e:
                # Possible but unlikely
               if "check-and-set parameter did not match the current version" in str(e):
                   logger.warning(f"InvalidRequest, Check-And-Set Error; Version Mismatch: {e}")
                   cas_error = True
                # Unexpected error has occurred; re-raise it
               else:
                   raise e

            if cas_error:
                # Query Vault again to check the version metadata at this path
                qkey_version_cas_error = \
                    self.vault_get_current_secret_version(filepath=qkey_path,
                                                          mount_point=mount_point)
                # Secret was updated under our noses between initial version
                # query and creation attempt with cas enforced
                if qkey_version_cas_error != qkey_version:
                    logger.warning(f"Epoch: \"{epoch}\"; A version update"
                                   " occurred while attempting key creation; "
                                   f"Old Version {qkey_version}; "
                                   f"Current Version: {qkey_version_cas_error}")

                # We shouldn't get here unless something unexpected has happened
                else:
                    logger.warning("Logical Error in attempting to create new "
                                   f"epoch key: \"{epoch}\"; "
                                   "Abandoning key creation attempt")

    def vault_read_secret_version(self, filepath: str, mount_point: str):
        """foo
        """
        secret_data = dict()
        secret_version = -1
        logger.debug(f"Attempt to query Vault secret version on "
                     f"filepath: {filepath}; mount_point: {mount_point}")
        try:
            data_response = \
                self.vclient.secrets.kv.v2.\
                read_secret_version(path=filepath,
                                    version=None,   # Latest version returned
                                    mount_point=mount_point)
        except hvac.exceptions.InvalidPath:
           logger.debug("There is no secret yet at filepath: "
                        f"{filepath}; mount_point: {mount_point}")
           secret_version = 0
        else:
            logger.debug(f"filepath: {filepath} version response:")
            self._dump_response(data_response, secret=False)
            current_version = int(data_response["data"]["metadata"]["version"])
            logger.debug(f"Current Version: {current_version}")
            secret_version = current_version
            secret_data = data_response["data"]["data"]

        return secret_version, secret_data

    def vault_commit_secret(self, path: str, secret: dict, version: int,
                            mount_point: str):
        """foo
        """
        cas_error = True
        try:
            qkey_response = \
                self.vclient.secrets.kv.v2.\
                create_or_update_secret(path=path,
                                        secret=secret,
                                        cas=version,
                                        mount_point=mount_point)
            logger.debug(f"Vault write \"{path}\" response:")
            self._dump_response(qkey_response, secret=False)
            cas_error = False
            logger.info(f"Vault write \"{path}\" version {version} successful")
        except hvac.exceptions.InvalidRequest as e:
            # Possible but unlikely
           if "check-and-set parameter did not match the current version" in str(e):
               logger.info(f"InvalidRequest, Check-And-Set Error; Version"
                           f"Mismatch: {version}; Exception {e}; Retrying...")
            # Unexpected error has occurred; re-raise it
           else:
               raise e

        return cas_error

    def vault_update_status(self, epoch: str, num_bytes: int):
        """foo
        """
        # Attempt to read status endpoint
        # if not present, set CAS to 0
        # else set CAS to received version
        # Attempt to update status endpoint with new epoch; use CAS
        # Iterate until successful
        cas_error = True
        while cas_error:
            # First attempt to read status endpoint
            mount_point = settings.GLOBAL.VAULT_KV_ENDPOINT
            status_path = f"{settings.GLOBAL.VAULT_QKDE_ID}/" \
                f"{settings.GLOBAL.VAULT_QCHANNEL_ID}/" \
                "status"
            status_version, status_data = \
                self.vault_read_secret_version(filepath=status_path,
                                               mount_point=mount_point
                                               )
            if epoch not in status_data:
                status_data[epoch] = num_bytes
            else:
                # Apparently there is already an epoch file in Vault by this name
                logger.error(f"Unexpected redundancy in status endpoint: {status_path}"
                             f"Epoch \"{epoch}\" already exists")
                raise KeyError(f"Unexpected redundancy in status endpoint: {status_path}"
                               f"Epoch \"{epoch}\" already exists")
            cas_error = self.\
                vault_commit_secret(path=status_path, secret=status_data,
                                    version=status_version, mount_point=mount_point)

    def process_epoch_file(self, filepath):
        """foo
        """
        logger.debug(f"Worker started on Filename: {filepath}")
        raw_bytes = watcherClient.read_epoch_file(filepath)
        epoch, raw_key = watcherClient.parse_raw_key_bytes(filepath, raw_bytes)
        self.vault_write_key(epoch, raw_key)
        self.vault_update_status(epoch, len(raw_key))
        watcherClient.delete_epoch_file(filepath)

        return {f"{filepath}": True}

    def mainloop(self):
        """foo
        """
        # Initialization
        self.backoff_factor: float = settings.GLOBAL.BACKOFF_FACTOR
        self.backoff_max: float = settings.GLOBAL.BACKOFF_MAX
        self.max_num_attempts: int = settings.NOTIFY_MAX_NUM_ATTEMPTS
        attempt_num: int = 0
        total_stall_time: float = 0.0
        total_notify_sleep_time: float = 0.0
        notify_sleep_iteration_count: int = 0
        # Worker pool
        workers = {}
        # Exception list
        self.exception_list = list()
        is_vault_sealed = True
        # Watch for notifications unless max attempts has been reached waiting
        # for the creation of the notify pipe or a signal was received to stop.
        # Only stop if the Vault instance has been unsealed giving a chance to
        # ingest the epoch files. Docker will send a SIGKILL after 10 seconds.
        while (not self.KILL_NOW or is_vault_sealed) and attempt_num < self.max_num_attempts:
            # Keep track of number of attemps to open notify pipe
            attempt_num = attempt_num + 1
            # Exponential backoff waiting for notificaiton pipe
            stall_time: float = self.backoff_factor * (2 ** (attempt_num - 1))
            # Don't exceed max backoff
            stall_time = min(self.backoff_max, stall_time)
            # Keep track of total stall time waiting on notify pipe creation
            total_stall_time = total_stall_time + stall_time
            try:
                # Authenticate with the vault server
                self.vault_client_auth()
                # If we're past auth, the Vault instance is not sealed any more
                is_vault_sealed = False
                # Attempt to open the notify pipe read-only, non-blocking
                with open(os.open(settings.GLOBAL.NOTIFY_PIPE_FILEPATH,
                                  os.O_NONBLOCK | os.O_RDONLY)) as FIFO:
                    logger.info(f"{settings.GLOBAL.NOTIFY_PIPE_FILEPATH} opened read-only, non-blocking")
                    # Notify pipe was successfully opened; iterate until otherwise
                    while not self.KILL_NOW:
                        # Break out of inner loop if notify pipe no longer exists
                        if not os.path.exists(settings.GLOBAL.NOTIFY_PIPE_FILEPATH):
                            logger.info(f"{settings.GLOBAL.NOTIFY_PIPE_FILEPATH} does not exist. Retrying...")
                            break
                        if total_notify_sleep_time > \
                           settings.NOTIFY_SLEEP_TIME_DELTA * \
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
                            epoch_filepath = f"{settings.GLOBAL.EPOCH_FILES_DIRPATH}/{data}"
                            # Check if token is about to be passed its leased time. If so, renew with renew-token. If fail, get new token with vault_client_auth()
                            if time.time() > self.vclient.lease_end - 10:
                                try:
                                    auth_response = self.vclient.renew_self_token()
                                    self.vclient.token = auth_response["auth"]["client_token"]
                                    TTL = auth_response["auth"]["lease_duration"]
                                    self.vclient.lease_end = TTL + time.time()
                                    logger.debug(f"Renewed token {self.vclient.token}. New TTL is {TTL:.1f} seconds")
                                except hvac.exceptions.Forbidden: #renew token didn't work. Re authenticate
                                    self.vault_client_auth()
                                    logger.debug(f"New token after reauthentication {self.vclient.token}")

                            # Name of thread worker callback function and argument filepath
                            args = (self.process_epoch_file,
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
                            notify_sleep_time = max(0, settings.NOTIFY_SLEEP_TIME - (end_time - start_time))
                            time.sleep(notify_sleep_time)
                            total_notify_sleep_time += notify_sleep_time

            except FileNotFoundError:
                logger.info(f"FIFO not found; Sleep time {stall_time}; Attempt Number: {attempt_num}/{self.max_num_attempts}; Total Stall Time: {total_stall_time} s")
                time.sleep(stall_time)
            except hvac.exceptions.VaultDown as e:
                logger.info(f"Vault instance is currently sealed: {e}; Attempt Number {attempt_num}/{self.max_num_attempts}; Total Stall Time: {total_stall_time} s")
                is_vault_sealed = True
                time.sleep(stall_time)


if __name__ == "__main__":
    watcher = watcherClient()
