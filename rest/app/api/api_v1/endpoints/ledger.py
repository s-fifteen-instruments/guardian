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


from fastapi import APIRouter, Body, Path, Request, status


from app import schemas
from app.core.rest_config import logger, settings


router = APIRouter()


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


local_kme_id_path = \
    Path(...,  # Required value; no default
         title="Local KME ID",
         description="Unique Local Key Management Entity (KME) ID String",
         min_length=settings.KME_ID_MIN_LENGTH,
         max_length=settings.KME_ID_MAX_LENGTH,
         regex=settings.VALID_KME_REGEX
         )

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


@router.put("/{local_KME_ID}/key_ids",
            response_model=schemas.KeyIDs,
            response_model_exclude_none=True,
            response_model_exclude_unset=True,
            status_code=status.HTTP_201_CREATED)
async def put_key_id_ledger(request: Request,
                            local_KME_ID: str = local_kme_id_path,
                            key_id_ledger_con: schemas.KeyIDLedgerContainer = Body(...),
                            ):
    logger.debug(f"local_KME_ID: {local_KME_ID}")
    key_ids_req = await request.app.state.vclient.\
        vault_commit_local_key_id_ledger_container(key_id_ledger_con=key_id_ledger_con,
                                                   calling_kme_id=local_KME_ID,
                                                   receiving_kme_id=settings.GLOBAL.LOCAL_KME_ID,
                                                   reset_status=True)
    logger.debug(f"Committed the following Key IDs to the local ledger: {key_ids_req}")
    return key_ids_req
