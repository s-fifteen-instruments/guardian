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
import time
from typing import Dict, List, Tuple, Union
import uuid

from fastapi import BackgroundTasks, HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.core.rest_config import logger, settings, _dump_response
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
        KME_direction_path = self.get_sae_connection(SAE = 'slave')
        mount_point = settings.GLOBAL.VAULT_KV_ENDPOINT
        vault_qkde_id = self.get_connected_qkde_from_sae(slave_SAE_ID)
        status_path =  vault_qkde_id + f"/" + \
                        KME_direction_path + f"/status"
        remote_kme = self.get_connected_kme_from_sae(slave_SAE_ID)
        worker_uid, epoch_status_dict = \
            self.vault_claim_epoch_files(requested_num_bytes=(num_keys * key_size_bytes),
                                         mount_point = mount_point, status_path = status_path )
        
        qchannel_path = vault_qkde_id + f"/" + \
                        KME_direction_path + f"/"
        
        sorted_epoch_file_list = await \
            self.fetch_keying_material(epoch_dict=epoch_status_dict,
                                       mount_point = mount_point, 
                                       qchannel_path = qchannel_path )

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

        # Local Tasks to complete
        task_list = list()
        for epoch in fully_consumed_epoch_list:
            task_list.append(self.vault_destroy_epoch_file(epoch=epoch,
                                                           mount_point = mount_point, 
                                                           qchannel_path = qchannel_path))
        for epoch, epoch_file in partially_consumed_epoch_dict.items():
            task_list.append(self.vault_update_epoch_file(epoch_file=epoch_file,
                                                          mount_point = mount_point, 
                                                          qchannel_path = qchannel_path))
        for ledger in key_id_ledger_con.ledgers:
            task_list.append(self.vault_commit_local_key_id_ledger(ledger,
                                                                   mount_point = mount_point, 
                                                                   qchannel_path = qchannel_path))
        await asyncio.gather(*task_list)

        # Remote tasks to complete
        remote_task_list = list()
        remote_task_list.append(self.send_remote_key_id_ledger_container(key_id_ledger_con=
                                                                         key_id_ledger_con,
                                                                         remote_kme=remote_kme))
        remote_kme_status_code = await asyncio.gather(*remote_task_list)

        # Release any epoch files held before processing remote KME status codes
        self.vault_release_epoch_files(worker_uid=worker_uid,
                                       epoch_dict=updated_epoch_status_dict,
                                       mount_point=mount_point,
                                       status_path=status_path)

        if remote_kme_status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            logger.error("Remote KME Response Status Code: 503 SERVICE UNAVAILABLE; "
                         f"Epoch files just released in status: {updated_epoch_status_dict}; "
                         f"Worker UID just released in status: {worker_uid}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Remote KME Response Status Code: 503 SERVICE UNAVAILABLE"
                                )
        elif remote_kme_status_code == status.HTTP_504_GATEWAY_TIMEOUT:
            logger.error("Remote KME Response Status Code: 504 GATEWAY TIMEOUT; "
                         f"Epoch files just released in status: {updated_epoch_status_dict}; "
                         f"Worker UID just released in status: {worker_uid}")
            raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                                detail="Remote KME Response Status Code: 504 GATEWAY TIMEOUT"
                                )
        else:
            logger.debug(f"Remote KME response status code: {remote_kme_status_code}")

        return key_con

    async def ledger_fetch_keys(self, key_id_ledger_con:
                                schemas.KeyIDLedgerContainer):
        """foo
        """

        # Determine ledger statuses before epoch file reservation
        ledger_status_dict = dict()
        err_msg = "Not all Key IDs are available for consumption: "
        for ledger in key_id_ledger_con.ledgers:
            if ledger.status != "available":
                ledger_status_dict[ledger.key_ID] = False
                err_msg += f"Key ID: \"{ledger.key_ID}\"; Key Status: \"{ledger.status}\"; "
            else:
                ledger_status_dict[ledger.key_ID] = True
                SAE = ledger.master_SAE_ID

        # Ensure all keys are available before continuing
        if not all(ledger_status_dict.values()):
            logger.error(err_msg)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=err_msg
                                )

        #TODO: Use actual SAE ID 
        KME_direction_path = self.get_sae_connection(SAE = 'master')
        mount_point = settings.GLOBAL.VAULT_KV_ENDPOINT
        vault_qkde_id = self.get_connected_qkde_from_sae(ledger.master_SAE_ID)
        status_path = vault_qkde_id + f"/" + \
                      KME_direction_path + f"/status"
        # Use Vault status file to reserve epoch files for manipulation
        worker_uid, epoch_status_dict = await self.\
            vault_ledger_claim_epoch_files(key_id_ledger_con=key_id_ledger_con,
                                           mount_point=mount_point,
                                           status_path=status_path)
        
        qchannel_path = vault_qkde_id + f"/" + \
                        KME_direction_path + f"/"
        # Query Vault for each epoch file's keying material
        sorted_epoch_file_list = await \
            self.fetch_keying_material(epoch_dict=epoch_status_dict,
                                       mount_point = mount_point, 
                                       qchannel_path = qchannel_path )

        # Constructing key container based on ledger container instructions
        key_con, updated_epoch_file_list, updated_key_id_ledger_con = await self.\
            build_ledger_key_container(key_id_ledger_con=key_id_ledger_con,
                                       sorted_epoch_file_list=sorted_epoch_file_list)

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
           task_list.append(self.vault_destroy_epoch_file(epoch=epoch,
                                                          mount_point = mount_point, 
                                                          qchannel_path = qchannel_path))
        for epoch, epoch_file in partially_consumed_epoch_dict.items():
            task_list.append(self.vault_update_epoch_file(epoch_file=epoch_file,
                                                          mount_point = mount_point, 
                                                          qchannel_path = qchannel_path))
        ledger_vault_qkde_id = self.get_connected_qkde_from_sae(ledger.slave_SAE_ID)
        ledger_qchannel_path = ledger_vault_qkde_id + f"/" + \
                        KME_direction_path + f"/"
        for ledger in updated_key_id_ledger_con.ledgers:
            task_list.append(self.vault_commit_local_key_id_ledger(ledger,
                                                                   mount_point = mount_point, 
                                                                   qchannel_path = ledger_qchannel_path))

        await asyncio.gather(*task_list)

        # Critical End
        self.vault_release_epoch_files(worker_uid=worker_uid,
                                       epoch_dict=epoch_status_dict,
                                       mount_point=mount_point,
                                       status_path=status_path)

        return key_con

    async def vault_ledger_claim_epoch_files(self, key_id_ledger_con:
                                             schemas.KeyIDLedgerContainer,
                                             mount_point: str = settings.GLOBAL.VAULT_KV_ENDPOINT,
                                             status_path: str = f"{settings.GLOBAL.VAULT_QKDE_ID}/" \
                                             f"{settings.GLOBAL.VAULT_QCHANNEL_ID}/" \
                                             "status"):
        """foo
        """
        epoch_list = await self.\
            extract_epoch_names_from_ledger_con(key_id_ledger_con=key_id_ledger_con)

        attempt_count = 0
        cas_error = True
        while cas_error:
            attempt_count += 1
            # First, attempt to read status endpoint
           
            status_version, status_data = \
                self.vault_read_secret_version(filepath=status_path,
                                               mount_point=mount_point
                                               )
            # Next, determine if all epoch files are
            # present and available for reservation
            missing_files_list, reserved_files_list, epoch_dict = await VaultManager.\
                check_epoch_status(requested_epoch_list=epoch_list,
                                   current_status_dict=status_data)
            if missing_files_list:
                logger.error("Ledger Requested Epoch Files are Missing "
                             f"in Vault Status; Req Epochs: {epoch_list}")
                raise \
                    HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                  detail="Ledger Requested Epoch Files are Missing "
                                         f"in Vault Status; Req Epochs: {epoch_list}; "
                                         f"Missing Epochs: {missing_files_list}"
                                  )

            if reserved_files_list:
                logger.debug(f"Awaiting Epoch Files to Become Available: "
                             f"Req Epochs: {epoch_list}; "
                             f"Reserved Epochs: {reserved_files_list}")

                # Service is becoming significantly loaded; serve a 503 status code
                if attempt_count > settings.MAX_NUM_RESERVE_ATTEMPTS:
                    logger.error("Reached Maximum number of Reservation Attempts: "
                                 f"{settings.MAX_NUM_RESERVE_ATTEMPTS} while attempting "
                                 f"to reserve epoch files: {epoch_list}")
                    raise \
                        HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                      detail="Reached Maximum number of Reservation Attempts: "
                                             f"{settings.MAX_NUM_RESERVE_ATTEMPTS} while attempting "
                                             f"to reserve epoch files: {epoch_list}"
                                      )
                else:
                    time.sleep(settings.RESERVE_SLEEP_TIME)
                    continue  # Attempt another read and see

            # All epoch files are present and available by this point

            # Build the updated version of the secret to be committed
            worker_uid, updated_status_data = VaultManager.\
                construct_claimed_status(data_index=status_data,
                                         epoch_dict=epoch_dict)

            # Commit the status back to Vault to claim the epoch_dict
            cas_error = self.\
                vault_commit_secret(path=status_path, secret=updated_status_data,
                                    version=status_version, mount_point=mount_point)

        return worker_uid, epoch_dict

    @staticmethod
    async def check_epoch_status(requested_epoch_list: List[str],
                                 current_status_dict: Dict[str, Union[str, int]]):
       """foo
       """
       present_files_list = list()
       missing_files_list = list()
       available_files_list = list()
       reserved_files_list = list()
       epoch_dict = dict()
       for req_epoch in requested_epoch_list:
           if req_epoch in current_status_dict:
               present_files_list.append(req_epoch)
               # This epoch file is free and displaying number of bytes for consuming
               # Worker UIDs should be strings
               if isinstance(current_status_dict[req_epoch], int):
                   available_files_list.append(req_epoch)
                   epoch_dict[req_epoch] = current_status_dict[req_epoch]
               else:
                   reserved_files_list.append(req_epoch)
           else:
               missing_files_list.append(req_epoch)

       return missing_files_list, reserved_files_list, epoch_dict

    async def \
        extract_epoch_names_from_ledger_con(self, key_id_ledger_con:
                                            schemas.KeyIDLedgerContainer) -> List[str]:
        """foo
        """
        epoch_list = list()
        for ledger in key_id_ledger_con.ledgers:
            for epoch in ledger.ledger_dict.keys():
                epoch_list.append(epoch)

        epoch_list = sorted(list(set(epoch_list)))
        return epoch_list

    async def query_ledger(self,
                           key_IDs: schemas.KeyIDs,
                           master_SAE_ID: str,
                           slave_SAE_ID: str) -> schemas.KeyIDLedgerContainer:
        """foo
        """
        # Find Key ID request duplicates
        KME_direction_path = self.get_sae_connection(SAE = 'master')
        mount_point = settings.GLOBAL.VAULT_KV_ENDPOINT
        vault_qkde_id = self.get_connected_qkde_from_sae(slave_SAE_ID)
        qchannel_path = vault_qkde_id + f"/" + \
                        KME_direction_path + f"/"
        key_id_list = list()
        duplicate_key_id_list = list()
        err_msg = "Duplicate key IDs in Request; Key IDs must be unique: "
        for key_id in key_IDs.key_IDs:
            if key_id.key_ID not in key_id_list:
                key_id_list.append(key_id.key_ID)
            else:
                duplicate_key_id_list.append(key_id.key_ID)
                err_msg += f"Key ID: {key_id.key_ID}; "

        # Check for key ID duplicates
        if duplicate_key_id_list:
            logger.error(err_msg)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=err_msg
                                )

        key_id_ledger_con = None
        # Local query for each Key ID in key_ids
        task_list = list()
        for key_ID in key_IDs.key_IDs:
            task_list.\
                append(self.vault_fetch_ledger_entry(key_ID=key_ID,
                                                     master_SAE_ID=master_SAE_ID,
                                                     slave_SAE_ID=slave_SAE_ID,
                                                     mount_point=mount_point,
                                                     qchannel_path=qchannel_path
                                                     )
                       )
        local_query_results = await asyncio.gather(*task_list)
        key_id_list, is_valid_list, key_id_ledger_list, ledger_version_list = \
            map(list, zip(*local_query_results))
        logger.debug(f"Ledger Entry Results: {local_query_results}")
        logger.debug(f"Ledger Key ID List: {key_id_list}")
        logger.debug(f"Ledger Valid List: {is_valid_list}")
        logger.debug(f"Ledger Version List: {ledger_version_list}")

        # Check for missing keys
        missing_keys = False
        err_msg = "One or more keys specified are not found on local KME: "
        for index, version in enumerate(ledger_version_list):
            if version == 0:
                err_msg += f"Key ID: {key_id_list[index]}; "
                missing_keys = True

        # Some keys are not present
        if missing_keys:
            logger.error(err_msg)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=err_msg
                                )

        # Some keys did not pass validation
        if not all(is_valid_list):
            logger.error("Unathorized. SAE ID of the requestor is "
                         "not an SAE ID supplied to the \"Get key\" "
                         "method each time it was called.")
            raise \
                HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                              detail="Unathorized. SAE ID of the requestor is "
                                     "not an SAE ID supplied to the \"Get key\" "
                                     "method each time it was called."
                              )

        # Only construct after validation
        key_id_ledger_con = schemas.KeyIDLedgerContainer(ledgers=key_id_ledger_list)
        logger.debug(f"KeyIDLedgerCon: {key_id_ledger_con}")

        return key_id_ledger_con

    async def vault_fetch_ledger_entry(self, key_ID: schemas.KeyID,
                                       master_SAE_ID: str,
                                       slave_SAE_ID: str,
                                       mount_point:str = settings.GLOBAL.VAULT_KV_ENDPOINT,
                                       qchannel_path:str = f"{settings.GLOBAL.VAULT_QKDE_ID}/" \
                                       f"{settings.GLOBAL.VAULT_QCHANNEL_ID}/" 
                                       ) -> Tuple[bool,
                                                                   schemas.KeyIDLedger,
                                                                   int]:
        """foo
        """
        key_id_valid = False
        ledger_entry = None
        try:
            ledger_path = qchannel_path + \
                f"{settings.GLOBAL.VAULT_LEDGER_ID}/" \
                f"{key_ID.key_ID}"
            key_id_ledger_response = self.hvc.secrets.kv.v2.\
                read_secret_version(path=ledger_path,
                                    version=None,   # Latest version returned
                                    mount_point=mount_point)
        except hvac.exceptions.InvalidPath:
            logger.debug("There is no information yet at ledger filepath: "
                         f"{ledger_path}; mount_point: {mount_point}")
            ledger_version = 0
        else:
            logger.debug(f"ledger_path: {ledger_path} version response:")
            _dump_response(key_id_ledger_response, secret=False)
            ledger_version = int(key_id_ledger_response["data"]["metadata"]["version"])
            flat_ledger_dict = key_id_ledger_response["data"]["data"]
            ledger_entry = await VaultManager.\
                parse_vault_ledger_entry(key_ID=key_ID.key_ID,
                                         flat_ledger_dict=flat_ledger_dict)
            logger.debug(f"Ledger Current Version: {ledger_version}")
            logger.debug(f"Ledger Entry: {ledger_entry}")
            if ledger_entry.master_SAE_ID == master_SAE_ID and \
               ledger_entry.slave_SAE_ID == slave_SAE_ID:
                key_id_valid = True
                logger.debug(f"Key ID Valid: \"{ledger_entry.key_ID}\"")

        return key_ID.key_ID, key_id_valid, ledger_entry, ledger_version

    @staticmethod
    async def parse_vault_ledger_entry(key_ID: str,
                                       flat_ledger_dict: Dict[str, Union[int, str]]):
        """foo
        """
        valid_ledger_entry = False
        key_id_ledger = None
        try:
            ledger_key_ID = flat_ledger_dict.pop("key_ID")
            ledger_status = flat_ledger_dict.pop("status")
            ledger_master_SAE_ID = flat_ledger_dict.pop("master_SAE_ID")
            ledger_slave_SAE_ID = flat_ledger_dict.pop("slave_SAE_ID")
            ledger_num_bytes = int(flat_ledger_dict.pop("num_bytes"))
        except Exception as e:
            logger.exception(f"Key ID: {key_ID}; Unparsable Vault Ledger Entry Metadata: {e}")

        try:
            ledger_dict = dict()
            complete_byte_ranges_list = list()
            # All entries that are left should be a
            # start or end index of a particular epoch
            for key, value in flat_ledger_dict.items():
                epoch, location, _ = key.split("_")
                logger.debug(f"Parse: Epoch: {epoch}; Location: {location}; ledger_dict: {ledger_dict}")
                if epoch not in ledger_dict:
                    logger.debug(f"New Key: Epoch: {epoch}; Location: {location}")
                    if location == "start" or location == "end":
                        # NOTE: One of the entries is incorrect;
                        # this is a placeholder for data validation
                        # until we encounter the next index
                        ledger_dict[epoch] = schemas.ByteRange(start=value,
                                                               end=value)
                    else:
                        logger.error("Unparsable key entries in flat_ledger_dict; "
                                     "Malformed start/end index labels (New)")
                else:
                    logger.debug(f"Existing Key: Epoch: {epoch}; Location: {location}")
                    if location == "start":
                        # Leave end index alone
                        ledger_dict[epoch] = schemas.\
                            ByteRange(start=value, end=ledger_dict[epoch].end)
                    elif location == "end":
                        # Leave start index alone
                        ledger_dict[epoch] = schemas.\
                            ByteRange(start=ledger_dict[epoch].start,
                                      end=value)
                    else:
                        logger.error("Unparsable key entries in flat_ledger_dict; "
                                     "Malformed start/end index labels (Existing)")
                    complete_byte_ranges_list.append(epoch)

            # Ensure all ByteRanges are completed and no residual keys left
            # Use set notation; order matters here
            if ledger_dict.keys() - set(complete_byte_ranges_list):
                raise KeyError("Unparsable key entries in flat_ledger_dict: "
                               f"Ledger Keys: {ledger_dict.keys()}; "
                               f"Completed Byte Ranges: {complete_byte_ranges_list}"
                               )

        except Exception as e:
            logger.exception(f"Key ID: {key_ID}; Unparsable Vault Ledger Entry Byte Ranges: {e}")

        try:
            key_id_ledger = schemas.KeyIDLedger(
                key_ID=ledger_key_ID,
                status=ledger_status,
                master_SAE_ID=ledger_master_SAE_ID,
                slave_SAE_ID=ledger_slave_SAE_ID,
                num_bytes=ledger_num_bytes,
                ledger_dict=ledger_dict
            )
            valid_ledger_entry = True
        except Exception as e:
            logger.exception(f"Key ID: {key_ID}; Unparsable Vault Ledger Entry Build Ledger: {e}")

        if not valid_ledger_entry:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Key ID: {key_ID}; Unparsable Vault Ledger Entry"
                                )

        return key_id_ledger

    async def \
        vault_commit_local_key_id_ledger_container(self, key_id_ledger_con:
                                                   schemas.KeyIDLedgerContainer,
                                                   calling_kme_id: str,
                                                   receiving_kme_id: str,
                                                   reset_status: bool = False) -> schemas.KeyIDs:
        """foo
        """
        logger.debug("Received Key ID Ledger Container:")
        _dump_response(key_id_ledger_con.dict(), secret=False)
        KME_direction_path = self.get_kme_connection(KME=calling_kme_id)
        mount_point = settings.GLOBAL.VAULT_KV_ENDPOINT
        vault_qkde_id = self.get_connected_qkde_from_kme(receiving_kme_id)
        qchannel_path = vault_qkde_id + f"/" + \
                        KME_direction_path + f"/"
        task_list = list()
        key_id_list = list()
        for ledger in key_id_ledger_con.ledgers:
            logger.debug(f"Adding Local Ledger Commit Task Key ID: {ledger.key_ID}")
            task_list.append(self.vault_commit_local_key_id_ledger(ledger,
                                                                   mount_point = mount_point, 
                                                                   qchannel_path = qchannel_path,
                                                                   reset_status=
                                                                   reset_status
                                                                   )
                             )
            key_id_list.append(schemas.KeyID(key_ID=ledger.key_ID))

        await asyncio.gather(*task_list)

        logger.debug(f"Key ID List: {key_id_list}")
        logger.debug(f"Key IDs: {schemas.KeyIDs(key_IDs=key_id_list)}")
        key_ids_req = schemas.KeyIDs(key_IDs=key_id_list)
        logger.debug(f"Key IDs Request: {key_ids_req}")
        return key_ids_req

    @staticmethod
    async def build_vault_ledger_entry(key_id_ledger: schemas.KeyIDLedger,
                                       reset_status: bool = False):
        """foo
        """
        if reset_status:
            logger.debug(f"Resetting KeyIDLedger \"{key_id_ledger.key_ID}\" Status to \"available\"")
            key_id_ledger.status = "available"

        secret_dict = {
            "status": f"{key_id_ledger.status}",
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
                                                  schemas.KeyIDLedgerContainer,
                                                  remote_kme: str):
        """foo
        """
        ledger_send_status_code = 0
        cert_tuple = (settings.VAULT_CLIENT_CERT_FILEPATH,
                      settings.VAULT_CLIENT_KEY_FILEPATH)
        remote_url = self.get_kme_url_from_kme(remote_kme)
        remote_req_url = f"https://{remote_url}{settings.API_V1_STR}/ledger/{settings.GLOBAL.LOCAL_KME_ID}/key_ids"
        verify_path = f"{settings.GLOBAL.CERT_DIRPATH}/{remote_kme}/{settings.CLIENT_NAME}/{settings.CLIENT_NAME}{settings.GLOBAL.CA_CHAIN_SUFFIX}"
        logger.debug(f"Sending Key ID Ledger Container to Remote KME: {remote_url}")
        logger.debug(f"As a dict: {key_id_ledger_con.dict()}")
        try:
            async with httpx.AsyncClient(cert=cert_tuple,
                                         verify=verify_path,
                                         trust_env=False,
                                         timeout=settings.REMOTE_KME_RESPONSE_TIMEOUT,
                                         ) as client:
                remote_kme_response = \
                    await client.put(url=remote_req_url,
                                     json=jsonable_encoder(key_id_ledger_con.dict()),
                                     follow_redirects=False
                                     )
        except httpx.ReadTimeout:
            logger.error(f"Remote KME Response Timeout after "
                         f"{settings.REMOTE_KME_RESPONSE_TIMEOUT} seconds; "
                         "Setting Local Status Code to 504 GATEWAY TIMEOUT")
            ledger_send_status_code = status.HTTP_504_GATEWAY_TIMEOUT
            return ledger_send_status_code

        logger.debug("Remote KME response:")
        _dump_response(remote_kme_response.json(), secret=False)
        logger.debug(f"Remote KME response status code: {remote_kme_response.status_code}")

        # TODO: Implement backoff loop if client is busy or down?
        ledger_send_status_code = remote_kme_response.status_code
        # Return early if remote side is busy
        if ledger_send_status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            logger.error("Remote KME Response Status Code: 503 SERVICE UNAVAILABLE")
            return ledger_send_status_code

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

        return ledger_send_status_code

    async def vault_commit_local_key_id_ledger(self, key_id_ledger:
                                               schemas.KeyIDLedger,
                                               mount_point: str = f"{settings.GLOBAL.VAULT_KV_ENDPOINT}",
                                               qchannel_path: str = f"{settings.GLOBAL.VAULT_QKDE_ID}/" \
                                                                    f"{settings.GLOBAL.VAULT_QCHANNEL_ID}/" ,
                                               reset_status: bool = False,
                                               ) -> None:
        """foo
        """

        key_id, key_id_valid, ledger_entry, ledger_version = await self.\
            vault_fetch_ledger_entry(key_ID=key_id_ledger,  # Works b/c KeyIDLedger inherits from KeyID
                                     master_SAE_ID=key_id_ledger.master_SAE_ID,
                                     slave_SAE_ID=key_id_ledger.slave_SAE_ID,
                                     mount_point = mount_point,
                                     qchannel_path = qchannel_path)

        # NOTE: Status updates to a ledger should only be requested upon first
        # creation. If this is true, this is outside of the intended design.
        # If we continue, likely no harm comes but it could be a mechanism
        # to further spam the server waiting for Vault commits. So, since this
        # should be coming from a PUT, we ignore this ledger commit (b/c it is
        # already in the Vault), log it, and still get to claim idempotency.
        # This should also prevent an initial ledger commit, a consumption of
        # the keying material in the ledger, a subsequent ledger commit resetting
        # the ledger status from consumed to available, and an erroneous
        # consumption of zeroed out keying material.
        if reset_status and ledger_version != 0:
            logger.warning("Unexpected Ledger Status Reset on Existing Ledger: "
                           f"key_ID: {key_id_ledger.key_ID}; "
                           f"Version: {ledger_version}; Ignoring Update")
            return

        try:
            epoch_path = qchannel_path + \
                f"{settings.GLOBAL.VAULT_LEDGER_ID}/" \
                f"{key_id_ledger.key_ID}"
            key_id_ledger_response = self.hvc.secrets.kv.v2.\
                create_or_update_secret(path=epoch_path,
                                        secret=await VaultManager.
                                        build_vault_ledger_entry(key_id_ledger,
                                                                 reset_status=
                                                                 reset_status),
                                        cas=ledger_version,
                                        mount_point=mount_point
                                        )
            logger.debug(f"Vault Key ID \"{key_id_ledger.key_ID}\" Ledger update response:")
            _dump_response(key_id_ledger_response, secret=False)
        except hvac.exceptions.InvalidRequest as e:
            # Possible only if another request is attempting to update ledger at
            # the same time. Maybe TODO: Put into cas while loop?
            if "check-and-set parameter" in str(e):
                logger.error(f"InvalidRequest, Key ID: \"{key_id_ledger.key_ID}\" "
                             f"Ledger Check-And-Set Error; Version Mismatch: {e}")
                raise \
                    HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                  detail=f"Key ID: \"{key_id_ledger.key_ID}\" "
                                         "Ledger Check-And-Set Error; "
                                         f"Expecting Version {ledger_version}; "
                                         f"Version Mismatch: {e}"
                                  )
            else:
                raise \
                    HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                  detail=f"Unexpected Error: {e}"
                                  )

    async def vault_update_epoch_file(self, epoch_file: schemas.EpochFile,
                                            mount_point: str,
                                            qchannel_path: str):
        """foo
        """
        cas_error = True
        while cas_error:
            cas_error = await self.vault_update_secret(epoch_file=epoch_file,
                                                       mount_point = mount_point,
                                                       qchannel_path = qchannel_path)

    async def vault_update_secret(self, epoch_file: schemas.EpochFile,
                                        mount_point:str = settings.GLOBAL.VAULT_KV_ENDPOINT,
                                        qchannel_path:str = f"{settings.GLOBAL.VAULT_QKDE_ID}/" \
                                        f"{settings.GLOBAL.VAULT_QCHANNEL_ID}/" ) -> bool:
        """foo
        """
        cas_error = True
        try:
            epoch_path = qchannel_path + f"{epoch_file.epoch}"

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
                    HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            if "check-and-set parameter" in str(e):
                logger.warning(f"InvalidRequest, Check-And-Set Error; Version Mismatch: {e}")
            # Unexpected error has occurred; re-raise it
            else:
                raise \
                    HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                  detail=f"Unexpected Error: {e}"
                                  )

        return cas_error

    async def vault_destroy_epoch_file(self, epoch: str,
                                    mount_point:str = settings.GLOBAL.VAULT_KV_ENDPOINT,
                                    qchannel_path:str = f"{settings.GLOBAL.VAULT_QKDE_ID}/" \
                                    f"{settings.GLOBAL.VAULT_QCHANNEL_ID}/" ):
        """foo
        """
        epoch_path = qchannel_path + f"{epoch}"
        epoch_file_response = \
            self.hvc.secrets.kv.v2.\
            delete_metadata_and_all_versions(path=epoch_path,
                                             mount_point=mount_point)
        logger.debug(f"Vault epoch file \"{epoch}\" delete response:")
        _dump_response(epoch_file_response.ok, secret=False)

    async def \
        build_ledger_key_pair(self, key_id_ledger:
                              schemas.KeyIDLedger,
                              sorted_epoch_file_list:
                              List[schemas.EpochFile]) -> Tuple[schemas.KeyPair,
                                                                List[schemas.EpochFile],
                                                                schemas.KeyIDLedger]:
        """foo
        """
        key_buffer = bytes()
        for epoch, byte_range in sorted(key_id_ledger.ledger_dict.items()):
            for index, epoch_file in enumerate(sorted_epoch_file_list):
                if epoch == epoch_file.epoch:
                    key_buffer += epoch_file.key[byte_range.start:
                                                 byte_range.end]
                    # Fill consumed section with NULL character "\0"
                    null_replacement = b"\0" * (byte_range.end - byte_range.start)
                    epoch_file.key = epoch_file.key[:byte_range.start] + \
                        null_replacement + epoch_file.key[byte_range.end:]
                    epoch_file.num_bytes -= len(null_replacement)
                    epoch_file = await self.recompute_digest(epoch_file=epoch_file)
                    break  # out of inner loop
            # Write epoch_file back
            sorted_epoch_file_list[index] = epoch_file

        # Update ledger status to consumed
        key_id_ledger.status = "consumed"

        key_pair = \
            schemas.KeyPair(
                key_ID=key_id_ledger.key_ID,
                key=await VaultManager.b64_encode_key(raw_key=key_buffer)
            )

        return key_pair, sorted_epoch_file_list, key_id_ledger

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
            if remaining_bytes > computed_num_bytes:
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
            # Also potentially entire epoch file consumed if exact size match
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
                                status="consumed",
                                master_SAE_ID="UPDATETHIS",
                                slave_SAE_ID="UPDATETHIS",
                                num_bytes=key_size_bytes,
                                ledger_dict=key_id_ledger_dict
                                )

        return key_pair, key_id_ledger, sorted_epoch_file_list

    async def \
        build_ledger_key_container(self, key_id_ledger_con:
                                   schemas.KeyIDLedgerContainer,
                                   sorted_epoch_file_list:
                                   List[schemas.EpochFile]) -> Tuple[schemas.KeyContainer,
                                                                     List[schemas.EpochFile],
                                                                     schemas.KeyIDLedgerContainer]:
        """foo
        """
        key_list = list()
        updated_ledger_list = list()
        for ledger in key_id_ledger_con.ledgers:
            key_pair, sorted_epoch_file_list, updated_ledger = await \
                self.build_ledger_key_pair(key_id_ledger=ledger,
                                           sorted_epoch_file_list=
                                           sorted_epoch_file_list)
            key_list.append(key_pair)

        # Update each ledger's status to reflect "consumed"
        for updated_ledger in updated_ledger_list:
            key_id_ledger_con.ledgers[updated_ledger.key_ID] = updated_ledger

        key_con = schemas.KeyContainer(keys=key_list)

        return key_con, sorted_epoch_file_list, key_id_ledger_con

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
                                    Dict[str, int],
                                    mount_point: str,
                                    qchannel_path: str) -> List[schemas.EpochFile]:
        """foo
        """
        task_list = list()
        for epoch, num_bytes in sorted(epoch_dict.items()):
            task_list.append(self.vault_fetch_epoch_file(epoch=epoch,
                                                         mount_point = mount_point,
                                                         qchannel_path = qchannel_path))

        epoch_file_list = sorted(list(await asyncio.gather(*task_list)),
                                 key=lambda x: x.epoch)

        return epoch_file_list

    async def vault_fetch_epoch_file(self, epoch,
                                    mount_point:str = settings.GLOBAL.VAULT_KV_ENDPOINT,
                                    qchannel_path:str = f"{settings.GLOBAL.VAULT_QKDE_ID}/" \
                                    f"{settings.GLOBAL.VAULT_QCHANNEL_ID}/" 
                                    ) -> schemas.EpochFile:
        """foo
        """
        epoch_path = qchannel_path + f"{epoch}"
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
                logger.error("Key HMACs are inconsistent for epoch "
                             f"file: {epoch_file.epoch}")

                raise \
                    HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
            digest_filepath = f"{settings.GLOBAL.DIGEST_FILES_DIRPATH}/" \
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
            digest_filepath = f"{settings.GLOBAL.DIGEST_FILES_DIRPATH}/" \
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
        mac = hmac.new(key=settings.GLOBAL.DIGEST_KEY,
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


    def get_sae_connection(self, SAE: str) -> str:
        """
        To implement a proper lookup here.
        Right now, this function is only called by fetch_keys from enc_keys 
        which is the master kme looking for the kme the slave sae is connected to
        and from query_ledger from post/get_key_with_key_ids which is the
        slave kme looking for the kme which the master sae is connected to.
        """
        if SAE == 'slave':
            KME = 'masterslave'
        elif SAE == 'master':
            KME = 'slavemaster'
        return KME

    def get_kme_connection(self, KME: str) -> str:
        """
        May need to implement proper translation from calling_kme_id
        to paths mounted in vault. For 2 nodes, slavemaster is fine.
        """
        KME = 'slavemaster'
        return KME
