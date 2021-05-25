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

import json
from pydantic import BaseModel, BaseSettings, Field
from pydantic.env_settings import SettingsSourceCallable
from math import ceil
from typing import Tuple

import logging
from fastapi.logger import logger as logger

gunicorn_error_logger = logging.getLogger("gunicorn.error")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

logger.handlers = gunicorn_error_logger.handlers

if __name__ != "__main__":
    # Production operation
    # logger.setLevel(gunicorn_logger.level)
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.DEBUG)


def _is_json(response):
    """foo
    """
    try:
        json.loads(response)
    except ValueError:
        return False
    except TypeError as e:
        if str(e).find("dict") != -1:
            return True
    return True


def _dump_response(response, secret: bool = True):
    """foo
    """
    if not secret:
        if response:
            if _is_json(response):
                logger.debug(f"""{json.dumps(response,
                                             indent=2,
                                             sort_keys=True)}""")
            else:
                logger.debug(f"{response}")
        else:
            logger.debug("No response")
    else:
        logger.debug("REDACTED")


def padded_base64_length(num_bytes: int):
    """foo
    """
    blocks: int = ceil(num_bytes / 3)
    return blocks * 4


def bits2bytes(bits: int):
    """Using Floor Calculation
    """
    return bits // 8


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    DIGEST_KEY: bytes = b"TODO: Change me; no hard code"
    DIGEST_FILES_DIRPATH: str = "/digest_files"
    DIGEST_COMPARE_TO_FILE: bool = True
    DIGEST_COMPARE: bool = True
    KEY_ID_MAX_LENGTH: int = 128
    KEY_ID_MIN_LENGTH: int = 16
    KEY_SIZE: int = 32  # Bits
    KME_ID_MAX_LENGTH: int = 32
    KME_ID_MIN_LENGTH: int = 3
    MAX_EX_MANADATORY_COUNT: int = 2
    MAX_EX_OPTIONAL_COUNT: int = 2
    MAX_KEY_COUNT: int = 250000000
    MAX_KEY_PER_REQUEST: int = 4
    MAX_KEY_SIZE: int = 80000  # Bits
    MAX_SAE_ID_COUNT: int = 2
    MIN_KEY_SIZE: int = 8  # Bits
    SAE_ID_MAX_LENGTH: int = 32
    SAE_ID_MIN_LENGTH: int = 3
    STATUS_MIN_LENGTH: int = 8
    STATUS_MAX_LENGTH: int = 9
    LOCAL_KME_ID: str = "kme1"
    REMOTE_KME_ID: str = "kme2"
    VALID_HOSTNAME_REGEX: str = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
    VALID_IP_ADDRESS_REGEX: str = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    VALID_SAE_REGEX: str = f"{VALID_HOSTNAME_REGEX}|{VALID_IP_ADDRESS_REGEX}"  # Regex for each string # Ignore Pyflakes error: https://stackoverflow.com/questions/64909849/syntax-error-with-flake8-and-pydantic-constrained-types-constrregex
    VALID_KME_REGEX: str = f"{VALID_HOSTNAME_REGEX}|{VALID_IP_ADDRESS_REGEX}"  # Regex for each string # Ignore Pyflakes error: https://stackoverflow.com/questions/64909849/syntax-error-with-flake8-and-pydantic-constrained-types-constrregex
    VALID_STATUS_REGEX: str = r"^consumed$|^available$"
    VAULT_BACKOFF_FACTOR: float = 1.0
    VAULT_BACKOFF_MAX: float = 8.0
    VAULT_MAX_CONN_ATTEMPTS: int = 10
    MAX_NUM_RESERVE_ATTEMPTS: int = 10
    VAULT_CLIENT_CERT_FILEPATH: str = f"/certificates/{LOCAL_KME_ID}/rest/rest.ca-chain.cert.pem"
    VAULT_CLIENT_KEY_FILEPATH: str = f"/certificates/{LOCAL_KME_ID}/rest/rest.key.pem"
    VAULT_NAME: str = "vault"
    VAULT_SERVER_CERT_FILEPATH: str = f"/certificates/{LOCAL_KME_ID}/{VAULT_NAME}/{VAULT_NAME}.ca-chain.cert.pem"
    REMOTE_KME_CERT_FILEPATH: str = f"/certificates/{REMOTE_KME_ID}/{VAULT_NAME}/{VAULT_NAME}.ca-chain.cert.pem"
    VAULT_TLS_AUTH_MOUNT_POINT: str = "cert"
    VAULT_URI: str = f"https://{VAULT_NAME}:8200"
    REMOTE_KME_URI: str = f"https://{REMOTE_KME_ID}{API_V1_STR}/ledger/{LOCAL_KME_ID}/key_ids"
    VAULT_KV_ENDPOINT: str = "QKEYS"
    VAULT_QKDE_ID: str = "QKDE0001"
    VAULT_QCHANNEL_ID: str = "ALICEBOB"
    VAULT_LEDGER_ID: str = "LEDGER"

    # Make environment settings take precedence over __init__ and file
    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings


settings = Settings()
