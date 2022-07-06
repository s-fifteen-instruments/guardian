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
import requests
import time

from app.core.rest_config import logger, settings, _dump_response


class VaultClient:
    """VaultClient class for handling rest connection to vault
    """
    def __init__(self) -> None:
        """ Check for initialization, sealed status and authorize with vault_client_key (rest)
        """
        self.hvc: hvac.Client = \
            hvac.Client(url=settings.GLOBAL.VAULT_SERVER_URL,
                        cert=(settings.VAULT_CLIENT_CERT_FILEPATH,
                              settings.VAULT_CLIENT_KEY_FILEPATH),
                        verify=settings.VAULT_SERVER_CERT_FILEPATH)

        self.is_vault_initialized = self.connection_loop(self.vault_check_init)
        if not self.is_vault_initialized:
            logger.error(f"Vault instance at {settings.GLOBAL.VAULT_SERVER_URL} is not initialized")
            raise hvac.exceptions.VaultNotInitialized("Vault is not initialized")

        self.is_vault_sealed = self.connection_loop(self.vault_check_seal)
        if self.is_vault_sealed:
            # Treat this as a warning as the unsealer service should be able
            # to unseal the vault shortly.
            logger.warning(f"Vault instance at {settings.GLOBAL.VAULT_SERVER_URL} is sealed")
            raise hvac.exceptions.VaultDown("Vault Instance is sealed")

        logger.info(f"Vault instance at {settings.GLOBAL.VAULT_SERVER_URL} is now unsealed")
        self.connection_loop(self.vault_tls_client_auth)
        self.is_vault_client_authenticated = self.connection_loop(self.vault_check_auth)
        if not self.is_vault_client_authenticated:
            logger.error(f"Attempt at Client Authentication with Vault"
                         f"Instance {settings.GLOBAL.VAULT_SERVER_URL} has failed")
            raise hvac.exceptions.Unauthorized("Reauthorization to Vault has failed.")

        logger.debug(f"Client authentication successful with Vault"
                     f"Instance at {settings.GLOBAL.VAULT_SERVER_URL}")

    def connection_loop(self, connection_callback, *args, **kwargs) -> None:
        """
        Makes connection to vault the function connection_callback in a loop.
        Returns the callback_result 
        """
        self.max_attempts: int = settings.GLOBAL.VAULT_MAX_CONN_ATTEMPTS
        self.backoff_factor: float = settings.GLOBAL.BACKOFF_FACTOR
        self.backoff_max: float = settings.GLOBAL.BACKOFF_MAX

        attempt_num: int = 0
        total_stall_time: float = 0.0
        while attempt_num < self.max_attempts:
            attempt_num = attempt_num + 1
            logger.debug(f"Vault Connection Attempt #: {attempt_num}")
            try:
                logger.debug("Vault Attempt Instance Health Status")
                health_response = self.hvc.sys.read_health_status(method="GET")
                logger.debug("Vault server status:")
                logger.debug(f"Health response type {type(health_response)}")
                if isinstance(health_response, dict):
                    _dump_response(health_response, secret=False)
                else:
                    _dump_response(health_response.json(), secret=False)

                if callable(connection_callback):
                    logger.debug(f"Attempting function callback: {connection_callback.__name__}()")
                    for arg in args:
                        logger.info(f"Arguments: \"{arg}\"")
                    for key, value in kwargs.items():
                        logger.info(f"Keyword Arguments: \"{key}\"=\"{value}\"")
                    callback_result = connection_callback(*args, **kwargs)
                else:
                    logger.debug("No connection callback function given")

                logger.debug("At the end of the connection loop.")
                # Break out of connection attempt loop
                break
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection was refused: {str(e)}")
                stall_time: float = self.backoff_factor * (2 ** (attempt_num - 1))
                stall_time = min(self.backoff_max, stall_time)
                total_stall_time = total_stall_time + stall_time
                logger.debug(f"Sleeping for {stall_time} seconds")
                time.sleep(stall_time)
        else:
            logger.error(f"Max {attempt_num} connection attempts over {total_stall_time} seconds")

        return callback_result

    def vault_tls_client_auth(self) -> None:
        """
        Authentication to vault via auth_tls (To be deprecated in 0.13)
        Replace with hvac.api.auth_methods.cert moving forward
        """
        mount_point: str = settings.VAULT_TLS_AUTH_MOUNT_POINT
        logger.debug("Attempt Vault TLS client Authentication")
        #auth_response = self.hvc.auth_tls(mount_point=mount_point,
        #                                  use_token=False)
        auth_response = self.hvc.auth.cert.login()
        logger.debug("Vault auth response:")
        _dump_response(auth_response, secret=True)
        #self.hvc.token = auth_response["auth"]["client_token"]

    def vault_reauth(self) -> None:
        """foo
        """
        self.is_vault_client_authenticated = self.connection_loop(self.vault_check_auth)
        if not self.is_vault_client_authenticated:
            self.connection_loop(self.vault_tls_client_auth)
            self.is_vault_client_authenticated = self.connection_loop(self.vault_check_auth)
        if not self.is_vault_client_authenticated:
            logger.error(f"Attempt at Client Reauthentication with Vault"
                         f"Instance {settings.GLOBAL.VAULT_SERVER_URL} has failed")
            raise hvac.exceptions.Unauthorized("Reauthorization to Vault has failed.")

        logger.debug(f"Client Reauthentication successful with Vault"
                     f"Instance at {settings.GLOBAL.VAULT_SERVER_URL}")

    def vault_check_init(self) -> bool:
        """foo
        """
        return self.hvc.sys.is_initialized()

    def vault_check_seal(self) -> bool:
        """foo
        """
        return self.hvc.sys.is_sealed()

    def vault_check_auth(self) -> bool:
        """foo
        """
        return self.hvc.is_authenticated()
