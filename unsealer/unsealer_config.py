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
    VAULT_NAME: str = "vault"
    VAULT_INIT_NAME: str = "vault_init"
    VAULT_URI: str = f"https://{VAULT_NAME}:8200"
    CERT_DIRPATH: str = "/certificates"
    ADMIN_DIRPATH: str = f"{CERT_DIRPATH}/admin"
    POLICIES_DIRPATH: str = "/vault/policies"
    LOG_DIRPATH: str = "/vault/logs"
    CA_CHAIN_SUFFIX: str = ".ca-chain.cert.pem"
    KEY_SUFFIX: str = ".key.pem"
    CSR_SUFFIX: str = ".csr.pem"
    VAULT_SECRETS_FILEPATH: str = f"{ADMIN_DIRPATH}/{VAULT_NAME}/SECRETS"
    CLIENT_CERT_FILEPATH: str = f"{CERT_DIRPATH}/{VAULT_INIT_NAME}/{VAULT_INIT_NAME}{CA_CHAIN_SUFFIX}"
    CLIENT_KEY_FILEPATH: str = f"{CERT_DIRPATH}/{VAULT_INIT_NAME}/{VAULT_INIT_NAME}{KEY_SUFFIX}"
    SERVER_CERT_FILEPATH: str = f"{CERT_DIRPATH}/{VAULT_INIT_NAME}/{VAULT_NAME}{CA_CHAIN_SUFFIX}"
    PKI_INT_CSR_PEM_FILEPATH: str = f"{CERT_DIRPATH}/{VAULT_INIT_NAME}/pki_int{CSR_SUFFIX}"
    PKI_INT_CERT_PEM_FILEPATH: str = f"{CERT_DIRPATH}/{VAULT_INIT_NAME}/pki_int{CA_CHAIN_SUFFIX}"
    SECRET_SHARES: int = 5
    SECRET_THRESHOLD: int = 3
    MAX_CONN_ATTEMPTS: int = 10
    BACKOFF_FACTOR: float = 1.0
    BACKOFF_MAX: float = 64.0  # seconds
    TIME_WINDOW: float = 30.0  # seconds

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
