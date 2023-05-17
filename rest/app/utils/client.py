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

import typing
import urllib

from fastapi import Request

from app.core.rest_config import logger


def parse_sae_client_info(request: Request) -> typing.Dict:
    """foo
    """
    sae_ip = request.client.host
    sae_hostname = request.url.hostname
    sae_common_name = ""
    sae_san = ""
    sae_id = ""
    logger.debug(f"Headers: {request.headers}")
    #  logger.debug(f"Headers: {request.headers['x-forwarded-tls-client-cert-info']}")
    try:
        # Header should be forwarded by Traefik
        sae_id = request.headers["x-forwarded-tls-client-cert-info"]
        # sae Common Name should be forwarded specifically
        sae_id = urllib.parse.unquote(sae_id)
        # Find the first CN - later ones are for CAs
        sae_id = sae_id.split("sae-id:")[1]
        # split on a colon to remove SAN information first
        sae_id = sae_id.split(";")[0]
        # Split on a comma if there are more CNs
        sae_id = sae_id.split(",")[0]
        # Remove backslashes and double quotes
        sae_id = sae_id.strip('\\"')
        # logger.debug(f"Got {sae_id} as sae ID")
    except IndexError:
        #No sae-id: in cert
        sae_id = ""
    except Exception as err:
        logger.warn(f"Unparsable sae ID in sae certificate:\n{sae_id}")
        logger.exception(err)
    try:
        # Header should be forwarded by Traefik
        sae_common_name = request.headers["x-forwarded-tls-client-cert-info"]
        # sae Common Name should be forwarded specifically
        sae_common_name = urllib.parse.unquote(sae_common_name)
        # Find the first CN - later ones are for CAs
        sae_common_name = sae_common_name.split("CN=")[1]
        # split on a colon to remove SAN information first
        sae_common_name = sae_common_name.split(";")[0]
        # Split on a comma if there are more CNs
        sae_common_name = sae_common_name.split(",")[0]
        # Remove backslashes and double quotes
        sae_common_name = sae_common_name.strip('\\"')
    except Exception as err:
        logger.warn(f"Unparsable sae common name in sae certificate:\n{sae_common_name}")
        logger.exception(err)
    try:
        # Header should be forwarded by Traefik
        sae_san = request.headers["x-forwarded-tls-client-cert-info"]
        # sae SAN should be forwarded specifically
        sae_san = urllib.parse.unquote(sae_san)
        # Find the first Subject - later ones are for CAs
        sae_san = sae_san.split("Subject=")[1]
        # split SAN to remove additional information first
        sae_san = sae_san.split("SAN=")[1]
        # Remove backslashes and double quotes and trailing comma
        sae_san = sae_san.replace('"', '').replace('\\', '').rstrip(",")
    except Exception as err:
        logger.warn(f"Unparsable sae SAN in sae certificate:\n{sae_san}")
        logger.exception(err)

    return {"sae_ip": sae_ip,
            "sae_hostname": sae_hostname,
            "sae_common_name": sae_common_name,
            "sae_san": sae_san,
            "sae_id": sae_id,
            }
