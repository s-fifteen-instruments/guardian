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

from typing import Any, List, Optional

from pydantic import BaseModel


class KeyIDExtension(BaseModel):
    key_ID_extension: Optional[Any] = None


class KeyID(KeyIDExtension):
    key_ID: str


class KeyIDsExtension(BaseModel):
    key_IDs_extension: Optional[Any] = None


class KeyIDs(KeyIDsExtension):
    key_IDs: List[KeyID]


# -----------------------------------------------------------------------------


class KeyExtension(BaseModel):
    key_extension: Optional[Any] = None


class Key(KeyExtension):
    key: str


class KeyPair(KeyID, Key):
    pass


class KeyContainerExtension(BaseModel):
    key_container_extension: Optional[Any] = None


class KeyContainer(KeyContainerExtension):
    keys: List[KeyPair]


# -----------------------------------------------------------------------------


class KeyRequest(BaseModel):
    number: Optional[int] = None
    size: Optional[int] = None
    additional_slave_SAE_IDs: Optional[List[str]] = None
    extension_mandatory: Optional[List[Any]] = None
    extension_optional: Optional[List[Any]] = None
