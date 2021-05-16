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
from typing import Any, Dict, List
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
            logger.error(f"Attempt at Client Authentication with Vault"
                         f"Instance {settings.VAULT_URI} has failed")
            raise hvac.exceptions.Unauthorized("Reauthorization to Vault has failed.")

        logger.debug(f"Client authentication successful with Vault"
                     f"Instance at {settings.VAULT_URI}")

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
            logger.error(f"Attempt at Client Reauthentication with Vault"
                         f"Instance {settings.VAULT_URI} has failed")
            raise hvac.exceptions.Unauthorized("Reauthorization to Vault has failed.")

        logger.debug(f"Client Reauthentication successful with Vault"
                     f"Instance at {settings.VAULT_URI}")

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

    def vault_read_secret_version(self, filepath: str, mount_point: str):
        """foo
        """
        secret_data = dict()
        secret_version = -1
        logger.debug(f"Attempt to query Vault secret version on "
                     f"filepath: {filepath}; mount_point: {mount_point}")
        try:
            data_response = \
                self.hvc.secrets.kv.v2.\
                read_secret_version(path=filepath,
                                    version=None,   # Latest version returned
                                    mount_point=mount_point)
        except hvac.exceptions.InvalidPath:
            logger.debug("There is no secret yet at filepath: "
                         f"{filepath}; mount_point: {mount_point}")
            secret_version = 0
        else:
            logger.debug(f"filepath: {filepath} version response:")
            _dump_response(data_response, secret=False)
            current_version = int(data_response["data"]["metadata"]["version"])
            logger.debug(f"Current Version: {current_version}")
            secret_version = current_version
            secret_data = data_response["data"]["data"]

        return secret_version, secret_data

    def vault_commit_secret(self, path: str, secret: Dict[str, Any],
                            version: int, mount_point: str):
        """foo
        """
        cas_error = True
        try:
            qkey_response = \
                self.hvc.secrets.kv.v2.\
                create_or_update_secret(path=path,
                                        secret=secret,
                                        cas=version,
                                        mount_point=mount_point)
            logger.debug(f"Vault write \"{path}\" response:")
            _dump_response(qkey_response, secret=False)
            cas_error = False
        except hvac.exceptions.InvalidRequest as e:
            # Possible but unlikely
            if "check-and-set parameter did not match the current version" in str(e):
                logger.warning(f"InvalidRequest, Check-And-Set Error; Version Mismatch: {e}")
            # Unexpected error has occurred; re-raise it
            else:
                raise \
                    HTTPException(status_code=503,
                                  detail=f"Uexpected Error: {e}"
                                  )

        return cas_error

    @staticmethod
    def check_byte_counts(data_index: Dict[str, Any], requested_num_bytes: int):
        """foo
        """
        current_byte_count = 0
        epoch_dict = dict()
        for epoch, worker_uid_or_num_bytes in sorted(data_index.items()):
            # This epoch file is free and displaying number of bytes for consuming
            # Worker UIDs should be strings
            if isinstance(worker_uid_or_num_bytes, int):
                num_bytes = worker_uid_or_num_bytes
                epoch_dict[epoch] = num_bytes
                current_byte_count += num_bytes
            if current_byte_count >= requested_num_bytes:
                break
        # We have iterated through all epoch files and not
        # found enough bytes for the request
        else:
            logger.error("Not enough keying material "
                         f"({current_byte_count} bytes) to satisfy "
                         f"request of {requested_num_bytes} bytes"
                         )
            raise \
                HTTPException(status_code=400,
                              detail="Not enough keying material "
                                     f"({current_byte_count} bytes) to satisfy "
                                     f"request of {requested_num_bytes} bytes"
                              )

        return epoch_dict

    @staticmethod
    def construct_claimed_status(data_index: Dict[str, Any], epoch_dict: Dict[str, int]):
        """foo
        """
        worker_uid = str(uuid.uuid4())
        for epoch, num_bytes in epoch_dict.items():
            if epoch in data_index:
                if data_index[epoch] == num_bytes:
                    data_index[epoch] = worker_uid
                else:
                    # Should not be here if no other worker has modified this entry
                    logger.error(f"Unexpected modified epoch in data index: {epoch}; "
                                 f"Expected num_bytes: {num_bytes}; Got: {data_index[epoch]}")
                    raise \
                        HTTPException(status_code=503,
                                      detail=f"Unexpected modified epoch in data index: {epoch}; "
                                      f"Expected num_bytes: {num_bytes}; Got: {data_index[epoch]}"
                                      )
            else:
                # Should not be here if epoch_dict was generated off data_index
                logger.error(f"Unexpected missing epoch in data index: {epoch}")
                raise \
                    HTTPException(status_code=503,
                                  detail=f"Unexpected missing epoch in data index: {epoch}"
                                  )

        return worker_uid, data_index

    @staticmethod
    def construct_released_status(data_index: Dict[str, Any], worker_uid: str,
                                  epoch_dict: Dict[str, int]):
        """foo
        """
        for epoch, num_bytes in epoch_dict.items():
            if epoch in data_index:
                if data_index[epoch] == worker_uid:
                    data_index[epoch] = num_bytes
                else:
                    # Should not be here if no other worker has modified this entry
                    logger.error(f"Unexpected modified epoch in data index: {epoch}; "
                                 f"Expected worker_uid: {worker_uid}; Got: {data_index[epoch]}")
                    raise \
                        HTTPException(status_code=503,
                                      detail=f"Unexpected modfied epoch in data index: {epoch}; "
                                             f"Expected worker_uid: {worker_uid}; Got: {data_index[epoch]}"
                                      )
            else:
                # Should not be here if epoch_dict was generated off data_index
                logger.error(f"Unexpected missing epoch in data index: {epoch}")
                raise \
                    HTTPException(status_code=503,
                                  detail=f"Unexpected missing epoch in data index: {epoch}"
                                  )

        return data_index

    def vault_claim_epoch_files(self, requested_num_bytes: int):
        """foo
        """
        cas_error = True
        while cas_error:
            # First, attempt to read status endpoint
            mount_point = settings.VAULT_KV_ENDPOINT
            status_path = f"{settings.VAULT_QKDE_ID}/" \
                f"{settings.VAULT_QCHANNEL_ID}/" \
                "status"
            status_version, status_data = \
                self.vault_read_secret_version(filepath=status_path,
                                               mount_point=mount_point
                                               )
            # Next, determine if enough keying material is currently free to
            # fulfill requested_num_bytes
            epoch_dict = VaultClient.\
                check_byte_counts(data_index=status_data,
                                  requested_num_bytes=requested_num_bytes)
            # Build the updated version of the secret to be committed
            worker_uid, updated_status_data = VaultClient.\
                construct_claimed_status(data_index=status_data,
                                         epoch_dict=epoch_dict)
            # Commit the status back to Vault to claim the epoch_dict
            cas_error = self.\
                vault_commit_secret(path=status_path, secret=updated_status_data,
                                    version=status_version, mount_point=mount_point)

        return worker_uid, epoch_dict

    def vault_release_epoch_files(self, worker_uid: str,
                                  epoch_dict: Dict[str, int]):
        """foo
        """
        cas_error = True
        while cas_error:
            # First, attempt to read status endpoint
            mount_point = settings.VAULT_KV_ENDPOINT
            status_path = f"{settings.VAULT_QKDE_ID}/" \
                f"{settings.VAULT_QCHANNEL_ID}/" \
                "status"
            status_version, status_data = \
                self.vault_read_secret_version(filepath=status_path,
                                               mount_point=mount_point
                                               )
            # Build the updated version of the secret to be committed
            updated_status_data = VaultClient.\
                construct_released_status(data_index=status_data,
                                          worker_uid=worker_uid,
                                          epoch_dict=epoch_dict)
            # Commit the status back to Vault to release the epoch_dict
            cas_error = self.\
                vault_commit_secret(path=status_path, secret=updated_status_data,
                                    version=status_version, mount_point=mount_point)
