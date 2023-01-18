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

import os
from pydantic import BaseSettings


class GlobalSettings(BaseSettings):
    """foo
    """
    LOCAL_KME_ID: str = os.environ.get("LOCAL_KME_ID", "kme1")
    LOCAL_KME_ALT_ID: str = os.environ.get("LOCAL_KME_ALT_ID", "kme1")
    REMOTE_KME_ID: str = os.environ.get("REMOTE_KME_ID", "kme2")
    REMOTE_KME_ALT_ID: str = os.environ.get("REMOTE_KME_ALT_ID", "kme2")
    LOCAL_SAE_ID: str = os.environ.get("LOCAL_SAE_ID", "sae1")
    #REMOTE_SAE_ID: str = os.environ.get("REMOTE_SAE_ID", "sae2")
    LOCAL_KME_ADDRESS: str = os.environ.get("LOCAL_KME_ADDRESS", "SETMEINMAKEFILE")
    REMOTE_KME_ADDRESS: str = os.environ.get("REMOTE_KME_ADDRESS", "SETMEINMAKEFILE")
    LOCAL_KME_ADD_SSH: str = os.environ.get("LOCAL_KME_ADD_SSH", "SETMEINMAKEFILE")
    SHOW_SECRETS: bool = True
    VAULT_NAME: str = "vault"
    VAULT_SERVER_URL: str = f"https://{VAULT_NAME}:8200"
    VAULT_CRL_URL: str = f"https://{VAULT_NAME}.{LOCAL_KME_ADDRESS}:8200"
    CA_CHAIN_SUFFIX: str = ".ca-chain.cert.pem"
    CERT_SUFFIX: str = ".cert.pem"
    KEY_SUFFIX: str = ".key.pem"
    CSR_SUFFIX: str = ".csr.pem"
    DIGEST_KEY: bytes = b"TODO: Change me; no hard code"
    EPOCH_FILES_DIRPATH: str = "/epoch_files"
    NOTIFY_PIPE_FILEPATH: str = f"{EPOCH_FILES_DIRPATH}/notify.pipe"
    DIGEST_FILES_DIRPATH: str = "/digest_files"
    CERT_DIRPATH: str = "/certificates/production"
    ADMIN_DIRPATH: str = f"{CERT_DIRPATH}/admin"
    POLICIES_DIRPATH: str = "/vault/policies"
    LOG_DIRPATH: str = "/vault/logs"
    VAULT_SECRETS_FILEPATH: str = f"{ADMIN_DIRPATH}/{VAULT_NAME}/SECRETS"
    VAULT_INIT_NAME: str = "vault_init"
    SERVER_CERT_FILEPATH: str = f"{CERT_DIRPATH}/{VAULT_INIT_NAME}/{VAULT_NAME}{CA_CHAIN_SUFFIX}"
    PKI_INT_CSR_PEM_FILEPATH: str = f"{CERT_DIRPATH}/{VAULT_INIT_NAME}/pki_int{CSR_SUFFIX}"
    PKI_INT_CERT_PEM_FILEPATH: str = f"{CERT_DIRPATH}/{VAULT_INIT_NAME}/pki_int{CA_CHAIN_SUFFIX}"
    VAULT_MAX_CONN_ATTEMPTS: int = 10
    BACKOFF_FACTOR: float = 1.0
    BACKOFF_MAX: float = 64.0  # seconds
    VAULT_KV_ENDPOINT: str = "QKEYS"
    VAULT_QKDE_ID: str = "QKDE0001"
    VAULT_QCHANNEL_ID: str = "masterslave"
    VAULT_REV_QCHANNEL_ID: str = "slavemaster"
    VAULT_LEDGER_ID: str = "LEDGER"
