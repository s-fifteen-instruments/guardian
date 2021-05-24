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

from fastapi import HTTPException
from pydantic import conlist, constr, Field, root_validator
from typing import Any, Dict, Optional

from app.core.config import logger, settings, bits2bytes, padded_base64_length
from app.schemas.base import ForbidBase


class KeyIDExtension(ForbidBase):
    key_ID_extension: Optional[Any] = Field(None,  # Default to nothing
                                            title="Additional Key ID Information",
                                            description="Addtional Information About the Key ID"
                                            )


class KeyID(KeyIDExtension):
    key_ID: str = Field(...,  # Required value; no default
                        title="Key ID String",
                        description="ID of the key: UUID format (example: \"550e8400-e29b-41d4-a716-446655440000\")",
                        min_length=settings.KEY_ID_MIN_LENGTH,
                        max_length=settings.KEY_ID_MAX_LENGTH
                        )


class KeyIDsExtension(ForbidBase):
    key_IDs_extension: Optional[Any] = Field(None,  # Default to nothing
                                             title="Key IDs Additional Information",
                                             description="Addtional Information for Key IDs Array"
                                             )


class KeyIDs(KeyIDsExtension):
    key_IDs: conlist(KeyID,  # Constrained list of KeyIDs
                     min_items=1,  # Min number of KeyIDs
                     max_items=settings.MAX_KEY_PER_REQUEST  # Max number of KeyIDs
                     ) = Field(...,  # Required value; no default
                               title="Array of key IDs",
                               description="Array of key IDs"
                               )


# -----------------------------------------------------------------------------


class KeyExtension(ForbidBase):
    key_extension: Optional[Any] = Field(None,  # Default to nothing
                                         title="Additional Key Information",
                                         description="Addtional Information About the Key"
                                         )


class Key(KeyExtension):
    key: str = Field(...,  # Required value; no default
                     title="Base64 Key Data",
                     description="Key Data Encoded by Base64; Size Limits in Base64 Encoded Bytes",
                     min_length=padded_base64_length(bits2bytes(settings.MIN_KEY_SIZE)),
                     max_length=padded_base64_length(bits2bytes(settings.MAX_KEY_SIZE))
                     )


class KeyPair(KeyID, Key):
    pass


class KeyContainerExtension(ForbidBase):
    key_container_extension: Optional[Any] = Field(None,  # Default to nothing
                                                   title="Addtional Key Container Information",
                                                   description="Addtional Key Container Information"
                                                   )


class KeyContainer(KeyContainerExtension):
    keys: conlist(KeyPair,  # Constrained list of KeyPairs
                  min_items=1,  # Min number of KeyPairs
                  max_items=settings.MAX_KEY_PER_REQUEST  # Max number of KeyPairs
                  ) = Field(...,  # Required value; no default
                            title="Key Container",
                            description="Response Data Model of API \"Get key\" Method and \"Get key with key IDs\" Method"
                            )


# -----------------------------------------------------------------------------


class ByteRange(ForbidBase):
    start: int = Field(...,  # Required value; no default
                       title="Starting Index of Keying Material in Epoch File",
                       description="Inclusive Starting Index of Keying Material in Epoch File",
                       ge=0  # Must be greater than or equal to
                       )
    end: int = Field(...,  # Required value; no default
                     title="Starting Index of Keying Material in Epoch File",
                     description="Inclusive Starting Index of Keying Material in Epoch File",
                     ge=0  # Must be greater than or equal to
                     )

    @root_validator(pre=False, skip_on_failure=True)
    def check_start_before_end(cls, values):
        start, end = values.get('start'), values.get('end')
        if start > end:
            logger.error(f"End Byte Index \"{end}\" Cannot be "
                         f"Less Than Start Byte Index \"{start}\"")
            raise \
                HTTPException(status_code=400,
                              detail=f"End Byte Index \"{end}\" Cannot be "
                                     f"Less Than Start Byte Index \"{start}\""
                              )
        return values


class KeyIDLedger(KeyID):
    master_SAE_ID: constr(min_length=settings.SAE_ID_MIN_LENGTH,  # Constrained string; min string length to SAE_ID_MIN_LENGTH
                          max_length=settings.SAE_ID_MAX_LENGTH,  # max string length to SAE_ID_MAX_LENGTH
                          regex=settings.VALID_SAE_REGEX  # Constrained to hostnames and IP addresses
                          ) = Field(...,  # Required value; no default
                                    title="Master SAE ID",
                                    description="Master SAE ID Creating this Ledger"
                                    )
    slave_SAE_ID: constr(min_length=settings.SAE_ID_MIN_LENGTH,  # Constrained string; min string length to SAE_ID_MIN_LENGTH
                         max_length=settings.SAE_ID_MAX_LENGTH,  # max string length to SAE_ID_MAX_LENGTH
                         regex=settings.VALID_SAE_REGEX  # Constrained to hostnames and IP addresses
                         ) = Field(...,  # Required value; no default
                                   title="Slave SAE ID",
                                   description="Slave SAE ID Receiving this Ledger"
                                   )
    num_bytes: int = Field(...,  # Required value; no default
                           title="Total Byte Count of Keying Material",
                           description="Total Byte Count of Keying Material",
                           le=settings.MAX_KEY_SIZE,  # Less than or equal to
                           ge=0  # Greater than or equal to
                           )
    ledger_dict: Dict[str, ByteRange] = Field(...,  # Required value; no default
                                              title="Dictionary of ByteRanges",
                                              description="Epoch Filename (key) and ByteRange (value) Pairs to Specify Where Keying Material is to be Taken From"
                                              )


class KeyIDLedgerContainerExtension(ForbidBase):
    key_id_ledger_extension: Optional[Any] = Field(None,  # Default to nothing
                                                   title="Addtional Key ID Ledger Container Information",
                                                   description="Addtional Key ID Ledger Container Information"
                                                   )


# TODO: Can probably enforce uniqueness if hash is well defined:
# https://github.com/samuelcolvin/pydantic/issues/2011
class KeyIDLedgerContainer(KeyIDLedgerContainerExtension):
    ledgers: conlist(KeyIDLedger,  # Constrained list of KeyIDLedgers
                     min_items=1,  # Min number of KeyIDLedgers
                     max_items=settings.MAX_KEY_PER_REQUEST  # Max number of KeyIDLedgers
                     ) = Field(...,  # Required value; no default
                               title="KeyIDLedger Container",
                               description="Data Model of API \"ledger\" Method"
                               )
