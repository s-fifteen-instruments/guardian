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

import datetime
import docker
import json
import logging as logger
import hvac
import signal
import sys
import time
import requests

from unsealer_config import settings

logger.basicConfig(stream=sys.stdout, level=int(settings.UNSEALER_LOG_LEVEL))


class UnsealerClient:
    """foo
    """

    def __init__(self) -> None:
        """foo
        """
        self.create_client()
        # First, see if a Vault instance is already up
        try:
            logger.info("Attempt initial Vault instance unsealing")
            self.vault_unseal()
        except Exception as e:
            logger.info(f"Initial attempt exception occurred: {e}")

        # Continue on into docker event loop
        self.KILL_NOW = False
        # Shut down gracefully with a SIGINT or SIGTERM
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.dclient = docker.from_env()
        filter_dict = {
            "label": "unsealer=watch",
            "image": "hashicorp/vault"
        }
        since = datetime.datetime.now() - datetime.timedelta(seconds=settings.TIME_WINDOW)
        logger.info("Waiting for Vault instance start or restart events...")
        while not self.KILL_NOW:
            time.sleep(1)
            now = datetime.datetime.now()
            for event in self.dclient.events(since=since, until=now, decode=True, filters=filter_dict):
                since = now
                if event["status"] == "start" or event["status"] == "restart":
                    logger.info("Vault instance start or restart detected")
                    self.connection_loop(self.vault_unseal)

    def exit_gracefully(self, signum, frame):
        """foo
        """
        logger.info("Signal Caught...Shutting Down")
        self.KILL_NOW = True

    def create_client(self):
        """foo
        """
        self.vclient: hvac.Client = \
            hvac.Client(url=settings.GLOBAL.VAULT_SERVER_URL,
                        cert=(settings.CLIENT_CERT_FILEPATH,
                              settings.CLIENT_KEY_FILEPATH),
                        verify=settings.GLOBAL.SERVER_CERT_FILEPATH)

    def connection_loop(self, connection_callback, *args, **kwargs) -> None:
        """foo
        """
        self.max_attempts: int = settings.GLOBAL.VAULT_MAX_CONN_ATTEMPTS
        self.backoff_factor: float = settings.GLOBAL.BACKOFF_FACTOR
        self.backoff_max: float = settings.GLOBAL.BACKOFF_MAX

        attempt_num: int = 0
        total_stall_time: float = 0.0
        while attempt_num < self.max_attempts:
            attempt_num = attempt_num + 1
            logger.debug(f"Connection Attempt #: {attempt_num}")
            try:
                logger.debug("Read Vault instance health status")
                health_response = self.vclient.sys.read_health_status(method="GET")
                logger.debug("Vault server status:")
                logger.debug(f"Health response type {type(health_response)}")
                if isinstance(health_response, dict):
                    self._dump_response(health_response, secret=False)
                else:
                    self._dump_response(health_response.json(), secret=False)

                if callable(connection_callback):
                    logger.info(f"Attempting function callback: {connection_callback.__name__}()")
                    for arg in args:
                        logger.info(f"Arguments: \"{arg}\"")
                    for key, value in kwargs.items():
                        logger.info(f"Keyword Arguments: \"{key}\"=\"{value}\"")
                    connection_callback(*args, **kwargs)
                else:
                    logger.debug("No connection callback function given")

                logger.debug("At the end of the connection loop.")
                # Break out of connection attempt loop
                break
            except requests.exceptions.ConnectionError as e:
                logger.debug(f"Connection was refused: {str(e)}")
                stall_time: float = self.backoff_factor * (2 ** (attempt_num - 1))
                stall_time = min(self.backoff_max, stall_time)
                total_stall_time = total_stall_time + stall_time
                logger.debug(f"Sleeping for {stall_time} seconds")
                time.sleep(stall_time)
        else:
            logger.warning(f"Max {attempt_num} connection attempts over {total_stall_time} seconds")

    @staticmethod
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

    @staticmethod
    def _dump_response(response, secret: bool = True):
        """foo
        """
        if not secret or settings.GLOBAL.SHOW_SECRETS:
            if response:
                if UnsealerClient._is_json(response):
                    logger.debug(f"""{json.dumps(response,
                                                 indent=2,
                                                 sort_keys=True)}""")
                else:
                    logger.debug(f"{response}")
            else:
                logger.debug("No response")
        else:
            logger.debug("REDACTED")

    def vault_unseal(self):
        """foo
        """
        if self.vclient.sys.is_sealed():
            if not hasattr(self, "unseal_keys"):
                self.unseal_keys = \
                    json.loads(open(settings.GLOBAL.VAULT_SECRETS_FILEPATH,
                                    "r").read())["keys"]
            # TODO: Secret Exposure
            self.unseal_response = \
                self.vclient.sys.submit_unseal_keys(self.unseal_keys)
            if not self.vclient.sys.is_sealed():
                logger.info("Vault instance unsealing successful")
                self._dump_response(self.unseal_response, secret=False)
            else:
                logger.error("Vault instance unseal failed")
                self._dump_response(self.unseal_response, secret=False)
        else:
            logger.info("Vault instance already unsealed")


if __name__ == "__main__":
    vclient = UnsealerClient()
