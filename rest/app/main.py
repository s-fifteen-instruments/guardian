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

import hvac
import time
import typing
import urllib

from fastapi import FastAPI, Request

from app.api.api_v1.api import api_router
from app.core.config import logger, settings
from app.vault.interface import VaultClient


app = FastAPI()
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
def startup():
    """foo
    """
    max_attempts: int = 10
    backoff_factor: float = 1.0
    backoff_max: float = 8.0

    attempt_num: int = 0
    total_stall_time: float = 0.0
    while attempt_num < max_attempts:
        try:
            attempt_num += 1
            app.state.vclient = VaultClient()
            break
        except hvac.exceptions.VaultDown as e:
            logger.error(f"Vault Instance remains sealed at startup: {e}")
            stall_time: float = backoff_factor * (2 ** (attempt_num - 1))
            stall_time = min(backoff_max, stall_time)
            total_stall_time = total_stall_time + stall_time
            logger.debug(f"Sleeping for {stall_time} seconds")
            time.sleep(stall_time)
        except Exception as e:
            logger.error(f"Unhandled exception at startup: {e}")
            break
    else:
        logger.error(f"Max {attempt_num} connection attempts over {total_stall_time} seconds")


@app.on_event("shutdown")
def shutdown():
    """foo
    """
    try:
        app.state.vclient.vclient.logout()
    except Exception as e:
        logger.error(f"Unhandled exception at shutdown: {e}")


@app.middleware("http")
async def ensure_fresh_token(request: Request, call_next):
    """foo
    """
    start_time = time.time()
    # Ensure authentication token is still valid
    # If not, reauthorize with the Vault instance
    app.state.vclient.vault_reauth()
    request.state.vclient = app.state.vclient
    sae_response = parse_sae_client_info(request)
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["x-process-time"] = str(process_time)
    response.headers["x-sae-ip"] = str(sae_response["sae_ip"])
    response.headers["x-sae-hostname"] = str(sae_response["sae_hostname"])
    response.headers["x-sae-common-name"] = str(sae_response["sae_common_name"])

    return response


def parse_sae_client_info(request: Request) -> typing.Dict:
    """foo
    """
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