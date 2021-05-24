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

import aiofiles
import asyncio
import base64
import hashlib
import httpx
import hmac
import hvac
from pydantic import parse_obj_as
from typing import Dict, List, Tuple
import uuid

from fastapi import BackgroundTasks, HTTPException
from fastapi.encoders import jsonable_encoder

from app.core.config import logger, settings, _dump_response
from app import schemas

from .semaphore import VaultSemaphore


class VaultManager(VaultSemaphore):
    """foo
    """
    def __init__(self) -> None:
        """foo
        """
        super().__init__()

    async def fetch_keys(self, num_keys: int, key_size_bytes: int,
                         master_SAE_ID: str, slave_SAE_ID: str,
                         background_tasks: BackgroundTasks):
        """Critical Region
        """
        # Critical Start
        worker_uid, epoch_status_dict = \
            self.vault_claim_epoch_files(requested_num_bytes=(num_keys * key_size_bytes))

        sorted_epoch_file_list = await \
            self.fetch_keying_material(epoch_dict=epoch_status_dict)

        key_con, key_id_ledger_con, updated_epoch_file_list = await self.\
            build_key_container(num_keys=num_keys,
                                key_size_bytes=key_size_bytes,
                                sorted_epoch_file_list=sorted_epoch_file_list)

        for key_id_ledger in key_id_ledger_con.ledgers:
            key_id_ledger.master_SAE_ID = master_SAE_ID
            key_id_ledger.slave_SAE_ID = slave_SAE_ID
            _dump_response(jsonable_encoder(key_id_ledger), secret=False)

        updated_epoch_status_dict = dict()
        fully_consumed_epoch_list = list()
        partially_consumed_epoch_dict = dict()
        for epoch, num_bytes in epoch_status_dict.items():
            for epoch_file in updated_epoch_file_list:
                if epoch == epoch_file.epoch:
                    updated_epoch_status_dict[epoch] = epoch_file.num_bytes
                    if epoch_file.num_bytes == 0:
                        fully_consumed_epoch_list.append(epoch)
                    else:
                        partially_consumed_epoch_dict[epoch] = epoch_file
                    break

        task_list = list()
        for epoch in fully_consumed_epoch_list:
            task_list.append(self.vault_destroy_epoch_file(epoch=epoch))
        for epoch, epoch_file in partially_consumed_epoch_dict.items():
            task_list.append(self.vault_update_epoch_file(epoch_file=epoch_file))
        for ledger in key_id_ledger_con.ledgers:
            task_list.append(self.vault_commit_local_key_id_ledger(ledger))

        # This creates the potential for a race condition if the slave SAE
        # gets Key IDs from the master SAE and then queries the remote KME
        # before this local KME gets around to this task. Small chance,
        # remote KME should then run a query back to this local KME for the
        # ledger as it will be synchronously submitted before the master
        # SAE even has keying material.
        background_tasks.add_task(self.send_remote_key_id_ledger_container,
                                  key_id_ledger_con)

        await asyncio.gather(*task_list)

        # Critical End
        self.vault_release_epoch_files(worker_uid=worker_uid,
                                       epoch_dict=updated_epoch_status_dict)

        return key_con

    async def \
        vault_commit_local_key_id_ledger_container(self, key_id_ledger_con:
                                                   schemas.KeyIDLedgerContainer) -> schemas.KeyIDs:
        """foo
        """
        logger.debug("Received Key ID Ledger Container:")
        _dump_response(key_id_ledger_con.dict(), secret=False)
        task_list = list()
        key_id_list = list()
        for ledger in key_id_ledger_con.ledgers:
            logger.debug(f"Adding Local Ledger Commit Task Key ID: {ledger.key_ID}")
            task_list.append(self.vault_commit_local_key_id_ledger(ledger))
            key_id_list.append(schemas.KeyID(key_ID=ledger.key_ID))

        await asyncio.gather(*task_list)

        logger.debug(f"Key ID List: {key_id_list}")
        logger.debug(f"Key IDs: {schemas.KeyIDs(key_IDs=key_id_list)}")
        key_ids_req = schemas.KeyIDs(key_IDs=key_id_list)
        logger.debug(f"Key IDs Request: {key_ids_req}")
        return key_ids_req

    @staticmethod
    async def build_vault_ledger_entry(key_id_ledger: schemas.KeyIDLedger):
        """foo
        """
        secret_dict = {
            "key_ID": f"{key_id_ledger.key_ID}",
            "master_SAE_ID": f"{key_id_ledger.master_SAE_ID}",
            "slave_SAE_ID": f"{key_id_ledger.slave_SAE_ID}",
            "num_bytes": key_id_ledger.num_bytes,
        }

        for epoch, byte_range in sorted(key_id_ledger.ledger_dict.items()):
            secret_dict[f"{epoch}_start_index"] = byte_range.start
            secret_dict[f"{epoch}_end_index"] = byte_range.end

        return secret_dict

    async def send_remote_key_id_ledger_container(self, key_id_ledger_con:
                                                  schemas.KeyIDLedgerContainer):
        """foo
        """
        cert_tuple = (settings.VAULT_CLIENT_CERT_FILEPATH,
                      settings.VAULT_CLIENT_KEY_FILEPATH)
        logger.debug(f"Sending Key ID Ledger Container to Remote KME: {settings.REMOTE_KME_URI}")
        logger.debug(f"As a dict: {key_id_ledger_con.dict()}")
        async with httpx.AsyncClient(cert=cert_tuple,
                                     verify=settings.REMOTE_KME_CERT_FILEPATH,
                                     trust_env=False) as client:
            remote_kme_response = \
                await client.put(url=settings.REMOTE_KME_URI,
                                 json=jsonable_encoder(key_id_ledger_con.dict()),
                                 allow_redirects=False
                                 )
            logger.debug("Remote KME response:")
            _dump_response(remote_kme_response.json(), secret=False)

            # Verify KeyIDs that came back the same
            key_id_request = schemas.KeyIDs(
                key_IDs=[schemas.KeyID(key_ID=ledger.key_ID) for ledger in key_id_ledger_con.ledgers]
            )
            if key_id_request != parse_obj_as(schemas.KeyIDs, remote_kme_response.json()):
                logger.error("Key ID mismatch between local request and remote response; "
                             f"Local Request: {key_id_request}; "
                             f"Remote Response: {remote_kme_response}"
                             )
            else:
                logger.debug("Key IDs match between local request and remote ledger response")

    async def vault_commit_local_key_id_ledger(self, key_id_ledger:
                                               schemas.KeyIDLedger) -> None:
        """foo
        """
        try:
            mount_point = settings.VAULT_KV_ENDPOINT
            epoch_path = f"{settings.VAULT_QKDE_ID}/" \
                f"{settings.VAULT_QCHANNEL_ID}/" \
                f"{settings.VAULT_LEDGER_ID}/" \
                f"{key_id_ledger.key_ID}"
            key_id_ledger_response = self.hvc.secrets.kv.v2.\
                create_or_update_secret(path=epoch_path,
                                        secret=await VaultManager.
                                        build_vault_ledger_entry(key_id_ledger),
                                        cas=0,  # This should be the first entry for this Key ID
                                        mount_point=mount_point
                                        )
            logger.debug(f"Vault Key ID \"{key_id_ledger.key_ID}\" Ledger update response:")
            _dump_response(key_id_ledger_response, secret=False)
        except hvac.exceptions.InvalidRequest as e:
            # Possible but unlikely
            if "check-and-set parameter did not match the current version" in str(e):
                logger.error(f"InvalidRequest, Key ID: \"{key_id_ledger.key_ID}\" "
                             f"Ledger Check-And-Set Error; Version Mismatch: {e}")
                raise \
                    HTTPException(status_code=503,
                                  detail=f"Key ID: \"{key_id_ledger.key_ID}\" "
                                         "Ledger Check-And-Set Error; "
                                         "Expecting Version 0; "
                                         f"Version Mismatch: {e}"
                                  )
            else:
                raise \
                    HTTPException(status_code=503,
                                  detail=f"Uexpected Error: {e}"
                                  )

    async def vault_update_epoch_file(self, epoch_file: schemas.EpochFile):
        """foo
        """
        cas_error = True
        while cas_error:
            cas_error = await self.vault_update_secret(epoch_file=epoch_file)

    async def vault_update_secret(self, epoch_file: schemas.EpochFile) -> bool:
        """foo
        """
        cas_error = True
        try:
            mount_point = settings.VAULT_KV_ENDPOINT
            epoch_path = f"{settings.VAULT_QKDE_ID}/" \
                f"{settings.VAULT_QCHANNEL_ID}/" \
                f"{epoch_file.epoch}"

            epoch_file_metadata_response = \
                self.hvc.secrets.kv.v2.read_secret_metadata(path=epoch_path,
                                                            mount_point=mount_point)
            logger.debug(f"Vault epoch file \"{epoch_file.epoch}\" metadata response:")
            _dump_response(epoch_file_metadata_response, secret=False)
            current_version = epoch_file_metadata_response["data"]["current_version"]
            if current_version != epoch_file.version:
                logger.error(f"Unexpected Epoch File Version: {epoch_file.epoch}; "
                             f"Stored Version: {epoch_file.version}; "
                             f"Current Version: {current_version}"
                             )
                raise \
                    HTTPException(status_code=503,
                                  detail=f"Unexpected Epoch File Version: {epoch_file.epoch}; "
                                         f"Stored Version: {epoch_file.version}; "
                                         f"Current Version: {current_version}"
                                  )

            secret_dict = {
                "key": await VaultManager.b64_encode_key(epoch_file.key),
                "digest": epoch_file.digest,
                "bytes": str(epoch_file.num_bytes),
                "epoch": epoch_file.epoch
            }
            epoch_file_response = self.hvc.secrets.kv.v2.\
                create_or_update_secret(path=epoch_path,
                                        secret=secret_dict,
                                        cas=epoch_file.version,
                                        mount_point=mount_point
                                        )
            logger.debug(f"Vault epoch file \"{epoch_file.epoch}\" update response:")
            _dump_response(epoch_file_response, secret=True)
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

    async def vault_destroy_epoch_file(self, epoch: str):
        """foo
        """
        mount_point = settings.VAULT_KV_ENDPOINT
        epoch_path = f"{settings.VAULT_QKDE_ID}/" \
            f"{settings.VAULT_QCHANNEL_ID}/" \
            f"{epoch}"
        epoch_file_response = \
            self.hvc.secrets.kv.v2.\
            delete_metadata_and_all_versions(path=epoch_path,
                                             mount_point=mount_point)
        logger.debug(f"Vault epoch file \"{epoch}\" delete response:")
        _dump_response(epoch_file_response, secret=True)

    async def build_key_pair(self,
                             key_size_bytes: int,
                             sorted_epoch_file_list:
                             List[schemas.EpochFile]) -> Tuple[schemas.KeyPair,
                                                               schemas.KeyIDLedger,
                                                               List[schemas.EpochFile]]:
        """foo
        """
        key_id_input_str = ""
        key_buffer = bytes()
        key_id_ledger_dict = dict()
        remaining_bytes = key_size_bytes
        for epoch_file in sorted_epoch_file_list:
            key_id_input_str += f"{epoch_file.path}/" \
                                f"{epoch_file.num_bytes}/"
            # Assume epoch_file.num_bytes could be
            # incorrect; use key length directly just in case
            computed_num_bytes = len(epoch_file.key)
            # Entire epoch file is being consumed
            if remaining_bytes >= computed_num_bytes:
                key_id_input_str += f"{computed_num_bytes}"
                key_buffer += epoch_file.key
                epoch_file.key = bytes()
                epoch_file = await self.recompute_digest(epoch_file=epoch_file)
                # Adjust the amount left to
                # consume from other epoch files
                remaining_bytes -= computed_num_bytes
                epoch_file.num_bytes = 0
                byte_range = schemas.ByteRange(start=0, end=computed_num_bytes)
                key_id_ledger_dict[epoch_file.epoch] = byte_range
            # Only part of an epoch file is being consumed
            else:
                key_id_input_str += f"{remaining_bytes}"
                # Take bytes from the end of the raw key
                key_buffer += epoch_file.key[-remaining_bytes:]
                # What is left comes from the beginning of the key
                epoch_file.key = epoch_file.key[:-remaining_bytes]
                epoch_file = await self.recompute_digest(epoch_file=epoch_file)
                # Adjust the number of epoch_file bytes
                epoch_file.num_bytes -= remaining_bytes
                # No more keying material needed
                remaining_bytes = 0
                byte_range = schemas.ByteRange(start=epoch_file.num_bytes,
                                               end=computed_num_bytes)
                key_id_ledger_dict[epoch_file.epoch] = byte_range
                # Quit the loop early
                break

        # Ensured to be a unique URL-like
        # path for UUID generation for each key
        key_id = str(uuid.uuid5(namespace=uuid.NAMESPACE_URL,
                                name=key_id_input_str))
        key_pair = schemas.KeyPair(key_ID=key_id,
                                   key=await VaultManager.b64_encode_key(raw_key=key_buffer)
                                   )
        key_id_ledger = \
            schemas.KeyIDLedger(key_ID=key_id,
                                master_SAE_ID="UPDATETHIS",
                                slave_SAE_ID="UPDATETHIS",
                                num_bytes=key_size_bytes,
                                ledger_dict=key_id_ledger_dict
                                )

        return key_pair, key_id_ledger, sorted_epoch_file_list

    async def build_key_container(self, num_keys: int,
                                  key_size_bytes: int,
                                  sorted_epoch_file_list:
                                  List[schemas.EpochFile]) -> Tuple[schemas.KeyContainer,
                                                                    schemas.KeyIDLedgerContainer,
                                                                    List[schemas.EpochFile]]:
        """foo
        """
        key_list = list()
        key_id_ledger_list = list()
        for key_index in range(num_keys):
            key_pair, key_id_ledger, sorted_epoch_file_list = await \
                self.build_key_pair(key_size_bytes=key_size_bytes,
                                    sorted_epoch_file_list=
                                    sorted_epoch_file_list
                                    )
            key_list.append(key_pair)
            key_id_ledger_list.append(key_id_ledger)

        key_con = schemas.KeyContainer(keys=key_list)
        key_id_ledger_con = schemas.KeyIDLedgerContainer(ledgers=key_id_ledger_list)
        return key_con, key_id_ledger_con, sorted_epoch_file_list

    async def fetch_keying_material(self, epoch_dict:
                                    Dict[str, int]) -> List[schemas.EpochFile]:
        """foo
        """
        task_list = list()
        for epoch, num_bytes in sorted(epoch_dict.items()):
            task_list.append(self.vault_fetch_epoch_file(epoch=epoch))

        epoch_file_list = sorted(list(await asyncio.gather(*task_list)),
                                 key=lambda x: x.epoch)

        return epoch_file_list

    async def vault_fetch_epoch_file(self, epoch) -> schemas.EpochFile:
        """foo
        """
        mount_point = settings.VAULT_KV_ENDPOINT
        epoch_path = f"{settings.VAULT_QKDE_ID}/" \
            f"{settings.VAULT_QCHANNEL_ID}/" \
            f"{epoch}"
        epoch_file_response = \
            self.hvc.secrets.kv.v2.read_secret(path=epoch_path,
                                               mount_point=mount_point)
        logger.debug(f"Vault epoch file \"{epoch}\" bytes response:")
        _dump_response(epoch_file_response, secret=True)

        raw_key = await VaultManager.\
            b64_decode_key(b64_encoded_key=epoch_file_response["data"]["data"]["key"])
        vault_hmac_digest = epoch_file_response["data"]["data"]["digest"]
        num_bytes = int(epoch_file_response["data"]["data"]["bytes"])
        vault_epoch = epoch_file_response["data"]["data"]["epoch"]
        version = epoch_file_response["data"]["metadata"]["version"]

        epoch_file = schemas.EpochFile(
            key=raw_key,
            digest=vault_hmac_digest,
            num_bytes=num_bytes,
            version=version,
            path=epoch_path,
            epoch=vault_epoch
        )

        if settings.DIGEST_COMPARE:
            is_key_intact = await VaultManager.check_key_hmac(epoch_file=epoch_file)
            logger.debug(f"Is Epoch File Key Intact: {is_key_intact}")
            if not is_key_intact:
                raise \
                    HTTPException(status_code=503,
                                  detail="Key HMACs are inconsistent for epoch "
                                         f"file: {epoch_file.epoch}"
                                  )

        return epoch_file

    @staticmethod
    async def b64_decode_key(b64_encoded_key: str) -> bytes:
        """foo
        """
        return base64.standard_b64decode((b64_encoded_key.encode("UTF-8")))

    @staticmethod
    async def b64_encode_key(raw_key: bytes) -> str:
        """foo
        """
        return (base64.standard_b64encode(raw_key)).decode("UTF-8")

    @staticmethod
    async def recompute_digest(epoch_file: schemas.EpochFile) -> schemas.EpochFile:
        """foo
        """
        epoch_file.digest = await VaultManager.compute_hmac_hexdigest(message=epoch_file.key)
        if settings.DIGEST_COMPARE_TO_FILE and settings.DIGEST_COMPARE:
            digest_filepath = f"{settings.DIGEST_FILES_DIRPATH}/" \
                              f"{epoch_file.epoch}.digest"
            await VaultManager.write_hexdigest(hexdigest=epoch_file.digest,
                                               filepath=digest_filepath
                                               )
        return epoch_file

    @staticmethod
    async def check_key_hmac(epoch_file: schemas.EpochFile) -> bool:
        """foo
        """
        # Set to True in case it is configured not to be checked
        compute_vs_file_intact = True

        computed_key_hexdigest = await \
            VaultManager.compute_hmac_hexdigest(epoch_file.key)
        logger.debug(f"Computed Hex Digest: {computed_key_hexdigest}")
        compute_vs_vault_intact = \
            hmac.compare_digest(computed_key_hexdigest, epoch_file.digest)

        if settings.DIGEST_COMPARE_TO_FILE:
            digest_filepath = f"{settings.DIGEST_FILES_DIRPATH}/" \
                              f"{epoch_file.epoch}.digest"
            file_store_key_hexdigest = await \
                VaultManager.read_hexdigest(filepath=digest_filepath)
            logger.debug(f"Filestore Hex Digest: {file_store_key_hexdigest}")
            compute_vs_file_intact = \
                hmac.compare_digest(computed_key_hexdigest,
                                    file_store_key_hexdigest)

        return compute_vs_file_intact and compute_vs_vault_intact

    @staticmethod
    async def compute_hmac_hexdigest(message: bytes, digestmod = hashlib.sha3_512) -> str:
        """foo
        """
        mac = hmac.new(key=settings.DIGEST_KEY,
                       digestmod=hashlib.sha3_512)
        mac.update(message)
        message_hexdigest = mac.hexdigest()
        logger.debug(f"Hex Digest: {message_hexdigest}")

        return message_hexdigest

    @staticmethod
    async def read_hexdigest(filepath: str) -> str:
        """foo
        """
        logger.debug(f"Reading hexdigest from filepath: {filepath}")
        async with aiofiles.open(filepath, "r") as f:
            hexdigest = await f.read()
        return hexdigest

    @staticmethod
    async def write_hexdigest(hexdigest: str, filepath: str):
        """foo
        """
        logger.debug(f"Writing hexdigest to filepath: {filepath}")
        async with aiofiles.open(filepath, "w") as f:
            await f.write(hexdigest)
