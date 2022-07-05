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

import hvac
from typing import Any, Dict
import uuid

from fastapi import HTTPException, status

from app.core.rest_config import logger, settings, _dump_response, bits2bytes

from .client import VaultClient


class VaultSemaphore(VaultClient):
    """
    Class of vault calls to do useful stuff in the QKEYS kv secret engine
    Most defaults to settings.GLOBAL.VAULT_KV_ENDPOINT,
                     settings.GLOBAL.VAULT_QKDE_ID,
                     settings.GLOBAL.VAULT_QCHANNEL_ID
                  
    """
    def __init__(self) -> None:
        """foo
        """
        super().__init__()

    def vault_read_secret_version(self, filepath: str, mount_point: str):
        """
        Reads /secrets/mount_point/filepath from vault.
        Returns secret_version, secret_data
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
            _dump_response(data_response, secret=True)
            current_version = int(data_response["data"]["metadata"]["version"])
            logger.debug(f"Current Version: {current_version}")
            secret_version = current_version
            secret_data = data_response["data"]["data"]

        return secret_version, secret_data

    def vault_commit_secret(self, path: str, secret: Dict[str, Any],
                            version: int, mount_point: str):
        """
        Commit a secret on /secret/mount_point/path
        Used to claim and release epochs.
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
            if "check-and-set parameter" in str(e):
                logger.warning(f"InvalidRequest, Check-And-Set Error; Version Mismatch: {e}")
            # Unexpected error has occurred; re-raise it
            else:
                raise \
                    HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                  detail=f"Uexpected Error: {e}"
                                  )

        return cas_error

    @staticmethod
    def total_byte_count(data_index: Dict[str, Any]):
        """foo
        """
        total_byte_count = 0
        for epoch, worker_uid_or_num_bytes in sorted(data_index.items()):
            # This epoch file is free and displaying number of bytes for consuming
            # Worker UIDs should be strings
            if isinstance(worker_uid_or_num_bytes, int):
                num_bytes = worker_uid_or_num_bytes
                total_byte_count += num_bytes

        return total_byte_count

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
                HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
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
                        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                      detail=f"Unexpected modified epoch in data index: {epoch}; "
                                      f"Expected num_bytes: {num_bytes}; Got: {data_index[epoch]}"
                                      )
            else:
                # Should not be here if epoch_dict was generated off data_index
                logger.error(f"Unexpected missing epoch in data index: {epoch}")
                raise \
                    HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
                    if num_bytes > 0:
                        data_index[epoch] = num_bytes
                    else:
                        del data_index[epoch]
                else:
                    # Should not be here if no other worker has modified this entry
                    logger.error(f"Unexpected modified epoch in data index: {epoch}; "
                                 f"Expected worker_uid: {worker_uid}; Got: {data_index[epoch]}")
                    raise \
                        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                      detail=f"Unexpected modfied epoch in data index: {epoch}; "
                                             f"Expected worker_uid: {worker_uid}; Got: {data_index[epoch]}"
                                      )
            else:
                # Should not be here if epoch_dict was generated off data_index
                logger.error(f"Unexpected missing epoch in data index: {epoch}")
                raise \
                    HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                  detail=f"Unexpected missing epoch in data index: {epoch}"
                                  )

        return data_index

    def vault_calculate_total_bytes(self) -> int:
        """foo
        """
        mount_point = settings.GLOBAL.VAULT_KV_ENDPOINT
        status_path = f"{settings.GLOBAL.VAULT_QKDE_ID}/" \
            f"{settings.GLOBAL.VAULT_QCHANNEL_ID}/" \
            "status"
        status_version, status_data = \
            self.vault_read_secret_version(filepath=status_path,
                                           mount_point=mount_point
                                           )
        # Next, determine if enough keying material is currently free to
        # fulfill requested_num_bytes
        total_byte_count = VaultSemaphore.\
            total_byte_count(data_index=status_data)

        return total_byte_count

    def vault_calculate_total_num_keys(self) -> int:
        """foo
        """
        total_key_bytes = self.vault_calculate_total_bytes()
        logger.debug(f"Vault Total Keying Material (bytes): {total_key_bytes}")
        total_num_keys: int = 0
        if settings.KEY_SIZE > 0:
            total_num_keys: int = total_key_bytes // bits2bytes(settings.KEY_SIZE)
        logger.debug(f"Calculated Number of Keys in Local Vault: {total_num_keys}")

        return total_num_keys

    def vault_claim_epoch_files(self, requested_num_bytes: int,
                                mount_point: str  = settings.GLOBAL.VAULT_KV_ENDPOINT,
                                status_path: str = f"{settings.GLOBAL.VAULT_QKDE_ID}/" \
                                f"{settings.GLOBAL.VAULT_QCHANNEL_ID}/" \
                                "status"
                                ):
        """foo
        """
        cas_error = True
        while cas_error:
            # First, attempt to read status endpoint
            status_version, status_data = \
                self.vault_read_secret_version(filepath=status_path,
                                               mount_point=mount_point
                                               )
            # Next, determine if enough keying material is currently free to
            # fulfill requested_num_bytes
            epoch_dict = VaultSemaphore.\
                check_byte_counts(data_index=status_data,
                                  requested_num_bytes=requested_num_bytes)
            # Build the updated version of the secret to be committed
            worker_uid, updated_status_data = VaultSemaphore.\
                construct_claimed_status(data_index=status_data,
                                         epoch_dict=epoch_dict)
            # Commit the status back to Vault to claim the epoch_dict
            cas_error = self.\
                vault_commit_secret(path=status_path, secret=updated_status_data,
                                    version=status_version, mount_point=mount_point)

        return worker_uid, epoch_dict

    def vault_release_epoch_files(self, worker_uid: str,
                                  epoch_dict: Dict[str, int],
                                  mount_point: str  = settings.GLOBAL.VAULT_KV_ENDPOINT,
                                  status_path: str = f"{settings.GLOBAL.VAULT_QKDE_ID}/" \
                                  f"{settings.GLOBAL.VAULT_QCHANNEL_ID}/" \
                                  "status"):
        """foo
        """
        cas_error = True
        while cas_error:
            # First, attempt to read status endpoint
            status_version, status_data = \
                self.vault_read_secret_version(filepath=status_path,
                                               mount_point=mount_point
                                               )
            # Build the updated version of the secret to be committed
            updated_status_data = VaultSemaphore.\
                construct_released_status(data_index=status_data,
                                          worker_uid=worker_uid,
                                          epoch_dict=epoch_dict)
            # Commit the status back to Vault to release the epoch_dict
            cas_error = self.\
                vault_commit_secret(path=status_path, secret=updated_status_data,
                                    version=status_version, mount_point=mount_point)
