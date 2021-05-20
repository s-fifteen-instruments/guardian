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

from typing import Optional

from fastapi import APIRouter, Body, Path, Query, Request
from fastapi.encoders import jsonable_encoder

from pydantic import conint

from app.utils import calculator, client
from app import schemas
from app import models
from app.core.config import logger, settings, _dump_response, bits2bytes


router = APIRouter()


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


master_sae_path = \
    Path(...,  # Required value; no default
         title="Master SAE ID",
         description="Unique Master Security Application Entity (SAE) String",
         min_length=settings.SAE_ID_MIN_LENGTH,
         max_length=settings.SAE_ID_MAX_LENGTH,
         regex=f"{settings.VALID_HOSTNAME_REGEX}|{settings.VALID_IP_ADDRESS_REGEX}"
         )

# ------------------------------------------------------------------------------

slave_sae_path = \
    Path(...,  # Required value, no default
         title="Slave SAE ID",
         description="Unique Slave Security Application Entity (SAE) String",
         min_length=settings.SAE_ID_MIN_LENGTH,
         max_length=settings.SAE_ID_MAX_LENGTH,
         regex=f"{settings.VALID_HOSTNAME_REGEX}|{settings.VALID_IP_ADDRESS_REGEX}"
         )

# ------------------------------------------------------------------------------

number_query = \
    Query(1,  # Default value of 1
          title="Number of Requested Keys",
          description="Number of Requested Keys (int >= 1) for the KME to Return to the SAE",
          le=settings.MAX_KEY_PER_REQUEST,  # Must be less than or equal to
          ge=1  # Must be greater than or equal to
          )

# ------------------------------------------------------------------------------

key_size_query = \
    Query(settings.KEY_SIZE,  # Default value
          title="Requested Key Size in Bits",
          description="Requested Key Size in Bits (min_key_size <= int <= max_key_size; multiple of 8 bits) for the KME to Return to the SAE",
          )

# ------------------------------------------------------------------------------

key_id_query = \
    Query(...,  # Required value, no default
          title="ID of the Requested Key",
          description="ID of the requested key in UUID format as a string",
          min_length=settings.KEY_ID_MIN_LENGTH,
          max_length=settings.KEY_ID_MAX_LENGTH,
          )

# ------------------------------------------------------------------------------

response_model_settings_dict = {
    "response_model": schemas.KeyContainer,
    "response_model_exclude_none": True,
    "response_model_exclude_unset": True
}


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

@router.get("/{slave_SAE_ID}/status",
            response_model=models.StatusRequest,
            response_model_exclude_none=True,
            response_model_exclude_unset=False,
            response_model_exclude_defaults=False,
            tags=["Status"])
def get_status(slave_SAE_ID: str = slave_sae_path,
               request: Request = Body(...)):
    logger.debug(f"slave_SAE_ID: {slave_SAE_ID}")
    stat_req = models.StatusRequest(
        master_SAE_ID=client.parse_sae_client_info(request)["sae_hostname"],
        slave_SAE_ID=slave_SAE_ID,
        stored_key_count=calculator.calculate_num_keys(request)
    )
    return stat_req


# ------------------------------------------------------------------------------


@router.get("/{slave_SAE_ID}/enc_keys",
            **response_model_settings_dict)
async def get_key(slave_SAE_ID: str = slave_sae_path,
                  number: Optional[int] = number_query,
                  size: Optional[conint(le=settings.MAX_KEY_SIZE,
                                        ge=settings.MIN_KEY_SIZE,
                                        multiple_of=settings.MIN_KEY_SIZE
                                        )
                                 ] = key_size_query,
                  request: Request = Body(...)):
    logger.debug(f"slave_SAE_ID: {slave_SAE_ID}")
    logger.debug(f"number: {number}")
    logger.debug(f"size: {size}")
    key_con = await request.app.state.vclient.\
        fetch_keys(num_keys=number, key_size_bytes=bits2bytes(size),
                   master_SAE_ID=request.state.sae_hostname,
                   slave_SAE_ID=slave_SAE_ID)
    logger.debug(f"key_con: {_dump_response(jsonable_encoder(key_con), secret=False)}")
    return key_con


# ------------------------------------------------------------------------------


@router.get("/{master_SAE_ID}/dec_keys",
            **response_model_settings_dict)
def get_key_with_key_ids(master_SAE_ID: str = master_sae_path,
                         key_ID: str = key_id_query):
    logger.debug(f"master_SAE_ID: {master_SAE_ID}")
    logger.debug(f"key_ID: {key_ID}")
    # TODO: Query Target KME for Key IDs
    # TODO: If good, Query Vault for Key IDs
    key_con = schemas.KeyContainer(
        keys=[
            schemas.KeyPair(
                key_ID=key_ID,
                key="Nice_Key"
            ),
        ],
        key_container_extension={"foo": 1, "bar": "two", "baz": ["A", 3.14]}
    )
    logger.debug(f"key_con: {_dump_response(jsonable_encoder(key_con), secret=False)}")
    return key_con


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


@router.post("/{slave_SAE_ID}/enc_keys",
             **response_model_settings_dict)
async def post_key(slave_SAE_ID: str = slave_sae_path,
                   key_req: models.KeyRequest = Body(...),
                   request: Request = Body(...)):
    logger.debug(f"slave_SAE_ID: {slave_SAE_ID}")
    logger.debug(f"key_req: {_dump_response(jsonable_encoder(key_req), secret=False)}")
    key_con = await request.app.state.vclient.\
        fetch_keys(num_keys=key_req.number,
                   key_size_bytes=bits2bytes(key_req.size))
    logger.debug(f"key_con: {_dump_response(jsonable_encoder(key_con), secret=False)}")
    return key_con


# ------------------------------------------------------------------------------


@router.post("/{master_SAE_ID}/dec_keys",
             **response_model_settings_dict)
def post_key_with_key_ids(master_SAE_ID: str = master_sae_path,
                          key_req: models.KeyRequest = Body(...)):
    logger.debug(f"master_SAE_ID: {master_SAE_ID}")
    logger.debug(f"key_req: {_dump_response(jsonable_encoder(key_req), secret=False)}")
    # TODO: Query Target KME for Key IDs
    # TODO: If good, Query Vault for Key IDs
    key_con = schemas.KeyContainer(
        keys=[
            schemas.KeyPair(
                key_ID="A_Key_ID01234567890123456",
                key="A_Key"
            ),
            schemas.KeyPair(
                key_ID="B_Key_ID01234567890123456",
                key="B_Key"
            )
        ],
        key_container_extension={"foo": 1, "bar": "two", "baz": ["A", 3.14]}
    )
    logger.debug(f"key_con: {_dump_response(jsonable_encoder(key_con), secret=False)}")
    return key_con
