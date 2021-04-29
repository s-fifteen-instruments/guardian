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
import logging as logger
import urllib
import typing
import sys

from fastapi import FastAPI, Request
#from fastapi.logger import logger

from app.api.api_v1.api import api_router
from app.core.config import settings

# from app.vault.interface import vclient
import hvac

# Attach to the Gunicorn logger, if it exists
# gunicorn_logger = logging.getLogger('gunicorn.error')
# logger.handlers = gunicorn_logger.handlers
# if __name__ != "main":
#     logger.setLevel(logging.DEBUG)
# else:
#     logger.setLevel(logging.DEBUG)

logger.basicConfig(stream=sys.stdout, level=logger.DEBUG)

app = FastAPI()
app.include_router(api_router, prefix=settings.API_V1_STR)


def _is_json(response):
    try:
        json.loads(response)
    except ValueError:
        return False
    except TypeError as e:
        if str(e).find("dict") != -1:
            return True
    return True


def _dump_response(response):
   """foo
   """
   if response:
       if _is_json(response):
           logger.debug(f"""{json.dumps(response,
                                        indent=2,
                                        sort_keys=True)}""")
       else:
           logger.debug(f"{response}")
   else:
       logger.debug("No response")


@app.get("/init")
async def init_vault():
    VAULT_URI: str = "https://vault:8200"
    CLIENT_CERT_PATH: str = "/certificates/rest/rest.ca-chain.cert.pem"
    CLIENT_KEY_PATH: str = "/certificates/rest/rest.key.pem"
    SERVER_CERT_PATH: str = "/certificates/vault/vault.ca-chain.cert.pem"
    vclient: hvac.Client = hvac.Client(url=VAULT_URI,
                                       cert=(CLIENT_CERT_PATH, CLIENT_KEY_PATH),
                                       verify=SERVER_CERT_PATH)

    mount_point = "cert"
    logger.debug("Attempt TLS client login")
    auth_response = vclient.auth_tls(mount_point=mount_point,
                                     use_token=False)
    logger.debug("Vault auth response:")
    _dump_response(auth_response)
    vclient.token = auth_response["auth"]["client_token"]
    logger.info("Hello from hvac!")
    logger.info(f"Is the vault client authenticated: {vclient.is_authenticated()}")
    logger.info(f"Is the vault client initialized: {vclient.sys.is_initialized()}")
    logger.info(f"Is the vault client sealed: {vclient.sys.is_sealed()}")


@app.get("/")
def read_root(request: Request):
    sae_dict = parse_sae_client_info(request)
    return sae_dict


def parse_sae_client_info(request: Request) -> typing.Dict:
    sae_ip = request.client.host
    sae_hostname = request.url.hostname
    sae_common_name = ""
    try:
        # Header should be forwarded by Traefik
        sae_common_name = request.headers["x-forwarded-tls-client-cert-info"]
        # sae Common Name should be forwarded specifically
        sae_common_name = urllib.parse.unquote(sae_common_name)
        # Find the first CN - later ones are for CAs
        sae_common_name = sae_common_name.split("CN=")[1]
        # Split on a comma if there are more CNs
        sae_common_name = sae_common_name.split(",")[0]
        # Remove backslashes and double quotes
        sae_common_name = sae_common_name.strip('\\"')
    except Exception as err:
        logger.warn(f"Unparsable sae common name in sae certificate:\n{sae_common_name}")
        logger.exception(err)

    return {"sae_ip": sae_ip,
            "sae_hostname": sae_hostname,
            "sae_common_name": sae_common_name}
