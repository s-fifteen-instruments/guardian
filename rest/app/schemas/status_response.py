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

from typing import Dict, Optional

from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: str
    # source_kme_id: str
    # target_kme_id: str
    # master_sae_id: str
    # slave_sae_id: str
    # key_size: int
    # stored_key_count: int
    # max_key_count: int
    # may_key_per_request: int
    # may_key_size: int
    # min_key_size: int
    # max_sae_id_count: int
    # status_extension: Optional[Dict]
