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

from fastapi import HTTPException, Request

from app.core.config import logger, settings, bits2bytes
from app.schemas.keys import KeyContainer


def calculate_num_keys(request: Request) -> int:
    """foo
    """
    # Negative one for retreiving a total byte count for all epoch files
    _, vault_total_key_bytes = request.app.state.vclient.vault_get_key_byte_counts(byte_amount=-1)
    logger.debug(f"Vault Total Keying Material (bytes): {vault_total_key_bytes}")
    total_num_keys: int = 0
    if settings.KEY_SIZE > 0:
        total_num_keys: int = vault_total_key_bytes // bits2bytes(settings.KEY_SIZE)
    logger.debug(f"Calculated Number of Keys in Vault: {total_num_keys}")
    return total_num_keys


def generate_key_container(number: int, size_bytes: int, request: Request) -> KeyContainer:
    """foo
    """
    if number > settings.MAX_KEY_PER_REQUEST:
        raise \
            HTTPException(status_code=400,
                          detail=f"Too many keys requested ({number}) for this "
                                 "transaction. Configuration maximum set to: "
                                 f"{settings.MAX_KEY_PER_REQUEST}"
                          )
    key_list = list()
    for key_index in range(number):
        key_list.append(request.app.state.vclient.vault_get_key(size_bytes=size_bytes))
    key_con = KeyContainer(
        keys=key_list,
        key_container_extension={}
    )
    return key_con
