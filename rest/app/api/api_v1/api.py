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

from fastapi import APIRouter

from app.api.api_v1.endpoints import status  # , enc_keys, dec_keys

api_router = APIRouter()
api_router.include_router(status.router, prefix="/status", tags=["status"])
# api_router.include_router(enc_keys.router, prefix="/enc_keys", tags=["enc_keys"])
# api_router.include_router(dec_keys.router, prefix="/dec_keys", tags=["dec_keys"])
