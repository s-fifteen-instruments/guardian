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

from typing import Any, Optional

from pydantic import conint, Field

from app.core.rest_config import settings
from app.schemas.base import ForbidBase


class StatusExtention(ForbidBase):
    status_extension: Optional[Any] = Field(None,  # Default to nothing
                                            title="Additional Status Information",
                                            description="Additional Information about the KME Status"
                                            )


class StatusRequest(ForbidBase):
    source_KME_ID: str = Field(settings.GLOBAL.LOCAL_KME_ID,
                               title="KME ID of the Local KME",
                               description="KME ID of the Local KME",
                               min_length=settings.KME_ID_MIN_LENGTH,
                               max_length=settings.KME_ID_MAX_LENGTH,
                               regex=f"{settings.VALID_HOSTNAME_REGEX}|{settings.VALID_IP_ADDRESS_REGEX}"
                               )
    target_KME_ID: str = Field(..., # Required value; no default
                               title="KME ID of the Target KME",
                               description="KME ID of the Target KME",
                               min_length=settings.KME_ID_MIN_LENGTH,
                               max_length=settings.KME_ID_MAX_LENGTH,
                               regex=f"{settings.VALID_HOSTNAME_REGEX}|{settings.VALID_IP_ADDRESS_REGEX}"
                               )
    master_SAE_ID: str = Field(...,  # Required value; no default
                               title="Master SAE ID",
                               description="Unique Master Security Application Entity (SAE) String",
                               min_length=settings.SAE_ID_MIN_LENGTH,
                               max_length=settings.SAE_ID_MAX_LENGTH,
                               regex=f"{settings.VALID_HOSTNAME_REGEX}|{settings.VALID_IP_ADDRESS_REGEX}"
                               )
    slave_SAE_ID: str = Field(...,  # Required value; no default
                              title="Slave SAE ID",
                              description="Unique Slave Security Application Entity (SAE) String",
                              min_length=settings.SAE_ID_MIN_LENGTH,
                              max_length=settings.SAE_ID_MAX_LENGTH,
                              regex=f"{settings.VALID_HOSTNAME_REGEX}|{settings.VALID_IP_ADDRESS_REGEX}"
                              )
    key_size: conint(le=settings.MAX_KEY_SIZE,
                     ge=settings.MIN_KEY_SIZE,
                     multiple_of=settings.MIN_KEY_SIZE
                     ) = Field(settings.KEY_SIZE,
                               title="Default Size of KME Key (in bits)",
                               description="Default size of key the KME can deliver to the SAE (in bit)"
                               )
    stored_key_count: int = Field(...,  # Required value; no default
                                  title="Number of Stored Keys",
                                  description="Number of stored keys KME can deliver to the SAE ",
                                  le=settings.MAX_KEY_COUNT,
                                  ge=0
                                  )
    max_key_count: int = Field(settings.MAX_KEY_COUNT,
                               title="Maximum Number of Stored Keys",
                               description="Maximum number of stored_key_count",
                               le=settings.MAX_KEY_COUNT,
                               ge=0
                               )
    max_key_per_request: int = Field(settings.MAX_KEY_PER_REQUEST,
                                     title="Maximum Number of Keys per Request",
                                     description="Maximum Number of Keys per Request",
                                     le=settings.MAX_KEY_PER_REQUEST,
                                     ge=0
                                     )
    max_key_size: conint(le=settings.MAX_KEY_SIZE,
                         ge=settings.MIN_KEY_SIZE,
                         multiple_of=settings.MIN_KEY_SIZE
                         ) = Field(settings.MAX_KEY_SIZE,
                                   title="Maximum Size of Key (in bits)",
                                   description="Maximum size of key the KME can deliver to the SAE  (in bits)",
                                   )
    min_key_size: conint(le=settings.MAX_KEY_SIZE,
                         ge=settings.MIN_KEY_SIZE,
                         multiple_of=settings.MIN_KEY_SIZE
                         ) = Field(settings.MIN_KEY_SIZE,
                                   title="Minimum Size of Key (in bits)",
                                   description="Minimum size of key the KME can deliver to the SAE  (in bit) "
                                   )
    max_SAE_ID_count: int = Field(settings.MAX_SAE_ID_COUNT,
                                  title="Maximum Additional Slave SAE IDs Allowed",
                                  description="Maximum number of additional_slave_SAE_IDs the KME allows",
                                  le=settings.MAX_SAE_ID_COUNT,
                                  ge=0
                                  )
    status_extension: Optional[StatusExtention] = Field(None,  # Default to nothing
                                                        title="Additional Status Information",
                                                        description="Additional Status Information"
                                                        )
