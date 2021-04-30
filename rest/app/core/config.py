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
from pydantic import BaseSettings

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


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    VAULT_URI: str = "https://vault:8200"
    VAULT_TLS_AUTH_MOUNT_POINT: str = "cert"
    VAULT_CLIENT_CERT_FILEPATH: str = "/certificates/rest/rest.ca-chain.cert.pem"
    VAULT_CLIENT_KEY_FILEPATH: str = "/certificates/rest/rest.key.pem"
    VAULT_SERVER_CERT_FILEPATH: str = "/certificates/vault/vault.ca-chain.cert.pem"
    VAULT_MAX_CONN_ATTEMPTS: int = 3
    VAULT_BACKOFF_FACTOR: float = 1.0
    VAULT_BACKOFF_MAX: float = 8.0


settings = Settings()
