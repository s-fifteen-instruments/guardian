#!/usr/bin/env python3
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

import base64
import hashlib
import hmac
import hvac
import pydantic
import requests
import time
from typing import List
import uuid

from fastapi import HTTPException

from app.core.config import logger, settings, _dump_response
from app import schemas


class VaultClient:
    """foo
    """
    def __init__(self) -> None:
        """foo
        """
        self.hvc: hvac.Client = \
            hvac.Client(url=settings.VAULT_URI,
                        cert=(settings.VAULT_CLIENT_CERT_FILEPATH,
                              settings.VAULT_CLIENT_KEY_FILEPATH),
                        verify=settings.VAULT_SERVER_CERT_FILEPATH)

        self.is_vault_initialized = self.connection_loop(self.vault_check_init)
        if not self.is_vault_initialized:
            logger.error(f"Vault instance at {settings.VAULT_URI} is not initialized")
            raise hvac.exceptions.VaultNotInitialized("Vault is not initialized")

        self.is_vault_sealed = self.connection_loop(self.vault_check_seal)
        if self.is_vault_sealed:
            logger.error(f"Vault instance at {settings.VAULT_URI} is sealed")
            raise hvac.exceptions.VaultDown("Vault Instance is sealed")

        self.connection_loop(self.vault_tls_client_auth)
        self.is_vault_client_authenticated = self.connection_loop(self.vault_check_auth)
        if not self.is_vault_client_authenticated:
            logger.error(f"Attempt at Client Authentication with Vault Instance {settings.VAULT_URI} has failed")
            raise hvac.exceptions.Unauthorized("Reauthorization to Vault has failed.")
        else:
            logger.debug(f"Client authentication successful with Vault Instance at {settings.VAULT_URI}")

    def connection_loop(self, connection_callback, *args, **kwargs) -> None:
        """foo
        """
        self.max_attempts: int = settings.VAULT_MAX_CONN_ATTEMPTS
        self.backoff_factor: float = settings.VAULT_BACKOFF_FACTOR
        self.backoff_max: float = settings.VAULT_BACKOFF_MAX

        attempt_num: int = 0
        total_stall_time: float = 0.0
        while attempt_num < self.max_attempts:
            attempt_num = attempt_num + 1
            logger.debug(f"Vault Connection Attempt #: {attempt_num}")
            try:
                logger.debug("Vault Attempt Instance Health Status")
                health_response = self.hvc.sys.read_health_status(method="GET")
                logger.debug("Vault server status:")
                logger.debug(f"Health response type {type(health_response)}")
                if isinstance(health_response, dict):
                    _dump_response(health_response, secret=False)
                else:
                    _dump_response(health_response.json(), secret=False)

                if callable(connection_callback):
                    logger.info(f"Attempting function callback: {connection_callback.__name__}()")
                    for arg in args:
                        logger.info(f"Arguments: \"{arg}\"")
                    for key, value in kwargs.items():
                        logger.info(f"Keyword Arguments: \"{key}\"=\"{value}\"")
                    callback_result = connection_callback(*args, **kwargs)
                else:
                    logger.debug("No connection callback function given")

                logger.debug("At the end of the connection loop.")
                # Break out of connection attempt loop
                break
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection was refused: {str(e)}")
                stall_time: float = self.backoff_factor * (2 ** (attempt_num - 1))
                stall_time = min(self.backoff_max, stall_time)
                total_stall_time = total_stall_time + stall_time
                logger.debug(f"Sleeping for {stall_time} seconds")
                time.sleep(stall_time)
        else:
            logger.error(f"Max {attempt_num} connection attempts over {total_stall_time} seconds")

        return callback_result

    def vault_tls_client_auth(self) -> None:
        """foo
        """
        mount_point: str = settings.VAULT_TLS_AUTH_MOUNT_POINT
        logger.debug("Attempt Vault TLS client Authentication")
        auth_response = self.hvc.auth_tls(mount_point=mount_point,
                                          use_token=False)
        logger.debug("Vault auth response:")
        _dump_response(auth_response)
        self.hvc.token = auth_response["auth"]["client_token"]

    def vault_reauth(self) -> None:
        """foo
        """
        self.is_vault_client_authenticated = self.connection_loop(self.vault_check_auth)
        if not self.is_vault_client_authenticated:
            self.connection_loop(self.vault_tls_client_auth)
        self.is_vault_client_authenticated = self.connection_loop(self.vault_check_auth)
        if not self.is_vault_client_authenticated:
            logger.error(f"Attempt at Client Reauthentication with Vault Instance {settings.VAULT_URI} has failed")
            raise hvac.exceptions.Unauthorized("Reauthorization to Vault has failed.")
        else:
            logger.debug(f"Client Reauthentication successful with Vault Instance at {settings.VAULT_URI}")

    def vault_check_init(self) -> bool:
        """foo
        """
        return self.hvc.sys.is_initialized()

    def vault_check_seal(self) -> bool:
        """foo
        """
        return self.hvc.sys.is_sealed()

    def vault_check_auth(self) -> bool:
        """foo
        """
        return self.hvc.is_authenticated()

    def vault_get_key_byte_counts(self, byte_amount: int = -1) -> int:
        """foo
        """
        total_bytes = 0
        epoch_file_dict = dict()
        epoch_file_list = self.vault_directory_get_epoch_file_list()
        for epoch_filename in epoch_file_list:
            epoch_file = self.vault_get_epoch_file(epoch_filename)
            epoch_file_dict[epoch_filename] = epoch_file
            total_bytes += epoch_file.num_bytes
            if total_bytes > byte_amount and byte_amount != -1:
                break

        return epoch_file_dict, total_bytes

    def vault_directory_get_epoch_file_list(self) -> List[str]:
        """foo
        """
        mount_point = settings.VAULT_KV_ENDPOINT
        qkey_path = f"{settings.VAULT_QKDE_ID}/" \
            f"{settings.VAULT_QCHANNEL_ID}"
        try:
            epoch_file_list_response = \
                self.hvc.secrets.kv.v2.list_secrets(path=qkey_path,
                                                    mount_point=mount_point)
        except hvac.exceptions.InvalidPath as e:
            logger.error(f"No keying material found for Vault path: \"{qkey_path}\"; Exception: {e}")
            raise \
                HTTPException(status_code=400,
                              detail="No keying material at Vault path "
                                     f"'{qkey_path}' to satisfy "
                                     f"current request"
                              )

        logger.debug("Vault epoch file list response:")
        _dump_response(epoch_file_list_response, secret=False)
        return epoch_file_list_response["data"]["keys"]

    def vault_epoch_file_get_bytes(self, epoch_filename: str) -> int:
        epoch_file = self.vault_epoch_file_get_epoch_file(epoch_filename)
        return epoch_file.num_bytes

    def vault_get_epoch_file(self, epoch_filename) -> schemas.EpochFile:
        """foo
        """
        # TODO: need to handle locked scenario
        # TODO: handle as number of epoch files increases
        while True:
            mount_point = settings.VAULT_KV_ENDPOINT
            epoch_path = f"{settings.VAULT_QKDE_ID}/" \
                f"{settings.VAULT_QCHANNEL_ID}/" \
                f"{epoch_filename}"
            epoch_file_response = \
                self.hvc.secrets.kv.v2.read_secret(path=epoch_path,
                                                   mount_point=mount_point)
            logger.debug(f"Vault epoch file \"{epoch_filename}\" bytes response:")
            _dump_response(epoch_file_response, secret=True)
            key = epoch_file_response["data"]["data"]["key"]
            digest = epoch_file_response["data"]["data"]["digest"]
            num_bytes = int(epoch_file_response["data"]["data"]["bytes"])
            status = epoch_file_response["data"]["data"]["status"]
            version = epoch_file_response["data"]["metadata"]["version"]
            epoch_file_response = schemas.EpochFile(
                key=key,
                digest=digest,
                num_bytes=num_bytes,
                status=status,
                version=version,
                path=epoch_path
            )
            if status == "unlocked" or status == "consumed":
                break

        return epoch_file_response

    @staticmethod
    def compute_hmac_hexdigest(message: bytes, digestmod = hashlib.sha3_512) -> str:
        """foo
        """
        mac = hmac.new(key=settings.DIGEST_KEY,
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
        logger.debug(f"Reading hexdigest from filepath: {filepath}")
        hexdigest = open(filepath, "r").read()
        return hexdigest

    @staticmethod
    def check_key_hmac(raw_key: bytes, epoch_file: schemas.EpochFile):
        """foo
        """
        is_key_intact = False
        computed_key_hexdigest = VaultClient.compute_hmac_hexdigest(raw_key)
        logger.debug(f"Computed Hex Digest: {computed_key_hexdigest}")
        digest_filepath = f"{settings.DIGEST_FILES_DIRPATH}/" \
                          f"{epoch_file.path.split('/')[-1]}.digest"
        file_store_key_hexdigest = \
            VaultClient.read_hexdigest(filepath=digest_filepath)
        logger.debug(f"Filestore Hex Digest: {file_store_key_hexdigest}")
        if (hmac.compare_digest(computed_key_hexdigest, epoch_file.digest) and
                hmac.compare_digest(computed_key_hexdigest, file_store_key_hexdigest) and
                epoch_file.num_bytes == len(raw_key)):
            is_key_intact = True
        return is_key_intact

    @staticmethod
    def decode_key_from_epoch_file(epoch_file: schemas.EpochFile):
        """foo
        """
        return VaultClient.b64_decode_key(encoded_key=epoch_file.key)

    @staticmethod
    def b64_decode_key(encoded_key: bytes):
        """foo
        """
        return base64.standard_b64decode((encoded_key.encode("UTF-8")))

    @staticmethod
    def b64_encode_key(raw_key: bytes):
        """foo
        """
        return (base64.standard_b64encode(raw_key)).decode("UTF-8")

    @staticmethod
    def extract_key(epoch_file: schemas.EpochFile):
        raw_key = VaultClient.decode_key_from_epoch_file(epoch_file=epoch_file)
        if not VaultClient.check_key_hmac(raw_key=raw_key,
                                          epoch_file=epoch_file):
            raise \
                HTTPException(status_code=503,
                              detail="Key HMACs are inconsistent for epoch "
                                     f"file: {epoch_file.path.split('/')[-1]}"
                              )
        return raw_key

    @staticmethod
    def compute_status(num_bytes: int):
        """foo
        """
        status = "unlocked"
        if num_bytes == 0:
            status = "consumed"
        return status

    def vault_commit_secret(self, epoch_file: schemas.EpochFile):
        """foo
        """
        digest_filepath = f"{settings.DIGEST_FILES_DIRPATH}/" \
                          f"{epoch_file.path.split('/')[-1]}.digest"
        VaultClient.write_hexdigest(epoch_file.digest, digest_filepath)
        # Attempt to update Vault
        mount_point = settings.VAULT_KV_ENDPOINT
        epoch_path = f"{settings.VAULT_QKDE_ID}/" \
            f"{settings.VAULT_QCHANNEL_ID}/" \
            f"{epoch_file.path.split('/')[-1]}"
        secret_dict = {
            "key": epoch_file.key,
            "digest": epoch_file.digest,
            "bytes": str(epoch_file.num_bytes),
            "status": epoch_file.status
        }
        epoch_file_response = \
            self.hvc.secrets.kv.v2.create_or_update_secret(path=epoch_path,
                                                           secret=secret_dict,
                                                           cas=epoch_file.version,
                                                           mount_point=mount_point)
        logger.debug(f"Vault epoch file \"{epoch_file.path.split('/')[-1]}\" update response:")
        _dump_response(epoch_file_response, secret=True)

    def vault_get_key(self, size_bytes: int):
        """foo
        """
        key_id_input_str = ""
        key_buffer = bytes()
        epoch_file_dict, total_bytes = self.vault_get_key_byte_counts(byte_amount=size_bytes)
        epoch_filename_list = \
            sorted([epoch_filename for epoch_filename, epoch_file in epoch_file_dict.items()])
        logger.debug("Epoch Filename List:")
        _dump_response(epoch_filename_list, secret=False)
        # Exclude the last epoch_filename; handle separately below
        for epoch_filename in epoch_filename_list[:-1] or []:
            epoch_file = epoch_file_dict[epoch_filename]
            key_id_input_str += epoch_file.path + str(epoch_file.num_bytes)
            logger.debug(f"Vault Epoch File \"{epoch_filename}\" Num Bytes: {epoch_file.num_bytes}")
            key_buffer += VaultClient.extract_key(epoch_file=epoch_file)

        # Add only from the end of the last epoch_file
        epoch_filename = epoch_filename_list[-1]
        epoch_file = epoch_file_dict[epoch_filename]
        remaining_bytes: int = size_bytes - len(key_buffer)
        key_id_input_str += epoch_file.path + str(remaining_bytes) + str(len(epoch_file.key))
        logger.debug(f"Remaining Num Bytes: {remaining_bytes}")
        logger.debug(f"Vault Epoch File \"{epoch_filename}\" Num Bytes: {epoch_file.num_bytes}")
        logger.debug(f"Key ID Input String: {key_id_input_str}")
        raw_key = VaultClient.extract_key(epoch_file=epoch_file)
        # Take bytes from the end of the raw key
        key_buffer += raw_key[-remaining_bytes:]

        # All the raw materials are gathered...we are ready
        key_id = str(uuid.uuid5(namespace=uuid.NAMESPACE_URL,
                                name=key_id_input_str))
        key = VaultClient.b64_encode_key(raw_key=key_buffer)

        # What is left comes from the beginning of the raw key
        remaining_key = raw_key[:-remaining_bytes]
        remaining_key_hexdigest = VaultClient.compute_hmac_hexdigest(remaining_key)
        updated_epoch_file = schemas.EpochFile(
            key=VaultClient.b64_encode_key(raw_key=remaining_key),
            digest=remaining_key_hexdigest,
            num_bytes=len(remaining_key),
            status=VaultClient.compute_status(len(remaining_key)),
            version=epoch_file.version,
            path=epoch_file.path
        )
        self.vault_commit_secret(epoch_file=updated_epoch_file)
        consumed_epoch_filename_list = epoch_filename_list[:-1]
        # All keys have been consumed; delete the last epoch file
        if len(raw_key) == 0:
            consumed_epoch_filename_list = epoch_filename_list
        # Iterate through the consumed files and delete them
        for epoch_filename in consumed_epoch_filename_list or []:
            epoch_file = epoch_file_dict[epoch_filename]
            # Write out a hexdigest of an empty byte string
            new_key = bytes()
            new_key_hexdigest = VaultClient.compute_hmac_hexdigest(message=new_key)
            digest_filepath = f"{settings.DIGEST_FILES_DIRPATH}/" \
                              f"{epoch_filename}.digest"
            VaultClient.write_hexdigest(hexdigest=new_key_hexdigest,
                                        filepath=digest_filepath)
            mount_point = settings.VAULT_KV_ENDPOINT
            epoch_path = f"{settings.VAULT_QKDE_ID}/" \
                f"{settings.VAULT_QCHANNEL_ID}/" \
                f"{epoch_filename}"
            epoch_file_response = \
                self.hvc.secrets.kv.v2.\
                delete_metadata_and_all_versions(path=epoch_path,
                                                 mount_point=mount_point)
            logger.debug(f"Vault epoch file \"{epoch_filename}\" delete response:")
            _dump_response(epoch_file_response, secret=True)

        # We couldn't gather enough keying material
        if len(key_buffer) < size_bytes:
            logger.error("Not enough keying material to satisfy request.")
            raise \
                HTTPException(status_code=400,
                              detail="Not enough keying material "
                                     f"({len(key_buffer)} bytes) to satisfy "
                                     f"request of {size_bytes} bytes"
                              )

        return schemas.KeyPair(key_ID=key_id, key=key)
