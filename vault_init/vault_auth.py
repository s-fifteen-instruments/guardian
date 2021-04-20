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
#


import argparse
import json
import logging as logger
import hvac
import os
import pathlib
import sys
import time
import requests

logger.basicConfig(stream=sys.stdout, level=logger.DEBUG)


class vaultClient:
    """foo
    """
    VAULT_URI: str = "https://vault:8200"
    CERT_DIRPATH: str = "/certificates/production"
    CLIENT_CERT_FILEPATH: str = f"{CERT_DIRPATH}/vault_init/vault_init.ca-chain.cert.pem"
    CLIENT_KEY_FILEPATH: str = f"{CERT_DIRPATH}/vault_init/vault_init.key.pem"
    SERVER_CERT_FILEPATH: str = f"{CERT_DIRPATH}/vault_init/vault.ca-chain.cert.pem"
    REST_DIRPATH: str = f"{CERT_DIRPATH}/rest"
    REST_CLIENT_CA_CHAIN_FILEPATH: str = f"{REST_DIRPATH}/rest.ca-chain.cert.pem"
    REST_CLIENT_KEY_FILEPATH: str = f"{REST_DIRPATH}/rest.key.pem"
    ADMIN_DIRPATH: str = f"{CERT_DIRPATH}/admin"
    ADMIN_REST_DIRPATH: str = f"{ADMIN_DIRPATH}/rest"
    ADMIN_REST_CLIENT_CA_CHAIN_FILEPATH: str = f"{ADMIN_REST_DIRPATH}/rest.ca-chain.cert.pem"
    ADMIN_REST_CLIENT_KEY_FILEPATH: str = f"{ADMIN_REST_DIRPATH}/rest.key.pem"
    VAULT_SECRETS_FILEPATH: str = f"{ADMIN_DIRPATH}/vault/SECRETS"
    PKI_INT_CSR_PEM_FILEPATH: str = f"{CERT_DIRPATH}/vault_init/pki_int.csr.pem"
    PKI_INT_CERT_PEM_FILEPATH: str = f"{CERT_DIRPATH}/vault_init/pki_int.ca-chain.cert.pem"
    CERT_GEN_DIRPATH: str = "/certificates/generation"
    LOG_DIRPATH: str = "/vault/logs"
    SECRET_SHARES: int = 5
    SECRET_THRESHOLD: int = 3
    MAX_CONN_ATTEMPTS: int = 10
    BACKOFF_FACTOR: float = 1.0
    BACKOFF_MAX: float = 64.0

    def __init__(self) -> None:
        """foo
        """
        self.parse_args()
        self.start_connection()

    def parse_args(self):
        """foo
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("--first", action="store_true", help="First stage of initialization")
        parser.add_argument("--second", action="store_true", help="Second stage of initialization")
        self.args = parser.parse_args()

    def start_connection(self):
        """foo
        """
        self.vclient: hvac.Client = \
            hvac.Client(url=vaultClient.VAULT_URI,
                        cert=(vaultClient.REST_CLIENT_CA_CHAIN_FILEPATH,
                              vaultClient.REST_CLIENT_KEY_FILEPATH),
                        verify=vaultClient.SERVER_CERT_FILEPATH)
        mount_point = "cert"
        logger.debug("Attempt TLS client login")
        auth_response = self.vclient.auth_tls(mount_point=mount_point,
                                              use_token=False)
        logger.debug("Vault auth response:")
        self._dump_response(auth_response)

    @classmethod
    def _is_json(cls, response):
        try:
            json.loads(response)
        except ValueError:
            return False
        except TypeError as e:
            if str(e).find("dict") != -1:
                return True
        return True

    @classmethod
    def _dump_response(cls, response):
        """foo
        """
        if response:
            if cls._is_json(response):
                logger.debug(f"""{json.dumps(response,
                                             indent=2,
                                             sort_keys=True)}""")
            else:
                logger.debug(f"{response}")
        else:
            logger.debug("No response")


if __name__ == "__main__":
    # init_vault()
    vclient = vaultClient()
