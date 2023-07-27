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

from pydantic import conint, conlist, constr, Field

from app.core.rest_config import settings
from app.schemas.base import IgnoreBase, ForbidBase


class ExtensionMandatory(ForbidBase):
    pass


class ExtensionOptional(IgnoreBase):
    pass


class KeyRequest(ForbidBase):
    number: Optional[int] = Field(1,  # Default value of 1
                                  title="Number of Requested Keys",
                                  description="Number of Requested Keys (int >= 1) for the KME to Return to the SAE",
                                  le=settings.MAX_KEY_COUNT,  # Must be less than or equal to
                                  ge=1  # Must be greater than or equal to
                                  )
    size: Optional[conint(le=settings.MAX_KEY_SIZE,  # Less than or equal to
                          ge=settings.MIN_KEY_SIZE,  # Greater than or equal to
                          multiple_of=settings.MIN_KEY_SIZE  # Must be a multiple of this
                          )
                   ] = Field(settings.KEY_SIZE,  # Default value of KME key size
                             title="Requested Key Size in Bits",
                             description="Requested Key Size in Bits (min_key_size <= int <= max_key_size; multiple of 8 bits) for the KME to Return to the SAE",
                             )
    additional_slave_SAE_IDs: Optional[conlist(constr(min_length=settings.SAE_ID_MIN_LENGTH,  # Constrained list of constrained strings; min string length to SAE_ID_MIN_LENGTH
                                                      max_length=settings.SAE_ID_MAX_LENGTH,  # max string length to SAE_ID_MAX_LENGTH
                                                      pattern=f"{settings.VALID_HOSTNAME_REGEX}|{settings.VALID_IP_ADDRESS_REGEX}"  # Regex for each string # Ignore Pyflakes error: https://stackoverflow.com/questions/64909849/syntax-error-with-flake8-and-pydantic-constrained-types-constrregex
                                                      ),
                                               min_length=0,  # Minimum number of allowed items in list
                                               max_length=settings.MAX_SAE_ID_COUNT  # Maximum number of allowed items in list (potentially zero-inclusive)
                                               )
                                       ] = Field(None,  # Default value of nothing
                                                 title="List of Additional Slave SAE IDs",
                                                 description="List of Addtional Slave SAE IDs up to max_SAE_ID_count"
                                                 )
    extension_mandatory: Optional[conlist(ExtensionMandatory,  # Constrained list of ExtensionMandatory objects
                                          min_length=0,  # Min number of items in list
                                          max_length=settings.MAX_EX_MANADATORY_COUNT  # Max number of items in list
                                          )
                                  ] = Field(None,  # Default value of nothing
                                            title="List of Mandatory Extension Parameters",
                                            description="Array of extension parameters specified as name/value pairs that KME shall handle or return an error"
                                            )
    extension_optional: Optional[conlist(ExtensionOptional,  # Constrained list of ExtensionOptional objects
                                         min_length=0,  # Min number of items in list
                                         max_length=settings.MAX_EX_OPTIONAL_COUNT  # Max number of items in list
                                         )
                                 ] = Field(None,  # Default value of nothing
                                           title="List of Optional Extension Parameters",
                                           description="Array of extension parameters specified as name/value pairs that KME may ignore"
                                           )
