#!/usr/bin/env python
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

from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable
from typing import Tuple


class Settings(BaseSettings):
    DIGEST_KEY: bytes = b"TODO: Change me; no hard code"
    DELETE_EPOCH_FILES: bool = True
    EPOCH_FILES_DIRPATH: str = "/epoch_files"
    DIGEST_FILES_DIRPATH: str = "/digest_files"
    NOTIFY_PIPE_FILEPATH: str = f"{EPOCH_FILES_DIRPATH}/notify.pipe"
    VAULT_SERVER_NAME: str = "vault"
    VAULT_SERVER_URI: str = f"https://{VAULT_SERVER_NAME}:8200"
    CLIENT_NAME: str = "watcher"
    CERT_DIRPATH: str = "/certificates/production"
    CLIENT_DIRPATH: str = f"{CERT_DIRPATH}/{CLIENT_NAME}"
    CA_CHAIN_SUFFIX: str = ".ca-chain.cert.pem"
    KEY_SUFFIX: str = ".key.pem"
    CLIENT_CERT_FILEPATH: str = f"{CLIENT_DIRPATH}/{CLIENT_NAME}{CA_CHAIN_SUFFIX}"
    CLIENT_KEY_FILEPATH: str = f"{CLIENT_DIRPATH}/{CLIENT_NAME}{KEY_SUFFIX}"
    SERVER_CERT_FILEPATH: str = f"{CERT_DIRPATH}/{VAULT_SERVER_NAME}/{VAULT_SERVER_NAME}{CA_CHAIN_SUFFIX}"
    BACKOFF_FACTOR: float = 1.0
    BACKOFF_MAX: float = 8.0
    MAX_NUM_ATTEMPTS: int = 100
    NOTIFY_SLEEP_TIME: float = 0.5  # seconds
    NOTIFY_SLEEP_TIME_DELTA: float = 30.0  # seconds
    VAULT_KEY_CHUNK_SIZE: int = 32  # bytes
    VAULT_KV_ENDPOINT: str = "QKEYS"
    VAULT_QKDE_ID: str = "QKDE0001"
    VAULT_QCHANNEL_ID: str = "ALICEBOB"

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
