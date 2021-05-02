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

from fastapi import APIRouter, Path, Query
from fastapi.encoders import jsonable_encoder

from app import schemas
from app import models
from app.core.config import logger, settings, _dump_response


router = APIRouter()


@router.get("/{slave_SAE_ID}/enc_keys",
            response_model=schemas.KeyContainer,
            response_model_exclude_none=True,
            response_model_exclude_unset=True)
def get_key(slave_SAE_ID: str = Path(...,
                                     title="Slave SAE ID",
                                     description="Unique Slave Security Application Entity (SAE) String",
                                     min_length=3,
                                     max_length=32,
                                     regex=f"{settings.VALID_HOSTNAME_REGEX}|{settings.VALID_IP_ADDRESS_REGEX}"
                                     ),
            number: Optional[int] = Query(1,
                                          title="Number of Requested Keys",
                                          description="Number of Requested Keys (int >= 1) for the KME to Return to the SAE",
                                          le=settings.MAX_KEY_COUNT,
                                          ge=1
                                          ),
            size: Optional[int] = Query(settings.KEY_SIZE,
                                        title="Requested Key Size in Bits",
                                        description="Requested Key Size in Bits (min_key_size <= int <= max_key_size; multiple of 8 bits) for the KME to Return to the SAE",
                                        le=settings.MAX_KEY_SIZE,
                                        ge=settings.MIN_KEY_SIZE)):
    logger.debug(f"slave_SAE_ID: {slave_SAE_ID}")
    logger.debug(f"number: {number}")
    logger.debug(f"size: {size}")
    # TODO: key_list = construct_key_list(number, size)
    key_con = schemas.KeyContainer(
        keys=[
            schemas.KeyPair(
                key_ID="A_Key_ID",
                key="A_Key"
            ),
            schemas.KeyPair(
                key_ID="B_Key_ID",
                key="B_Key"
            )
        ],
        key_container_extension={"foo": 1, "bar": "two", "baz": ["A", 3.14]}
    )
    logger.debug(f"key_con: {_dump_response(jsonable_encoder(key_con), secret=False)}")
    return key_con


@router.post("/{slave_SAE_ID}/enc_keys",
             response_model=schemas.KeyContainer,
             response_model_exclude_none=True,
             response_model_exclude_unset=True)
def post_key(slave_SAE_ID: str,
             key_req: models.KeyRequest):
    logger.debug(f"slave_SAE_ID: {slave_SAE_ID}")
    logger.debug(f"key_req: {_dump_response(jsonable_encoder(key_req), secret=False)}")
    # TODO: key_list = construct_key_list(number, size)
    key_con = schemas.KeyContainer(
        keys=[
            schemas.KeyPair(
                key_ID="A_Key_ID",
                key="A_Key"
            ),
            schemas.KeyPair(
                key_ID="B_Key_ID",
                key="B_Key"
            )
        ],
        key_container_extension={"foo": 1, "bar": "two", "baz": ["A", 3.14]}
    )
    logger.debug(f"key_con: {_dump_response(jsonable_encoder(key_con), secret=False)}")
    return key_con
