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

from typing import Dict

from fastapi import APIRouter
from fastapi import Request

from app import schemas
from app.core.rest_config import logger


router = APIRouter()


@router.get("/", response_model=schemas.Vconn)
def check_vconn(request: Request) -> Dict:
    is_inited = request.app.state.vclient.vault_check_init()
    is_sealed = request.app.state.vclient.vault_check_seal()
    is_authed = request.app.state.vclient.vault_check_auth()
    logger.debug(f"Is the vault instance initialized: {is_inited}")
    logger.debug(f"Is the vault instance sealed: {is_sealed}")
    logger.debug(f"Is the vault client authenticated: {is_authed}")
    check_dict = {
        "is_initialized": is_inited,
        "is_sealed": is_sealed,
        "is_authenticated": is_authed
    }
    return check_dict
