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
import stat
import sys
import time
import requests

from vault_init_config import settings

logger.basicConfig(stream=sys.stdout, level=logger.DEBUG)


class VaultClient:
    def __init__(self) -> None:
        """foo
        """
        self.parse_args()
        self.start_connection()
        if self.args.first:
            self.phase_1_startup()
        if self.args.second:
            self.phase_2_startup()

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
            hvac.Client(url=settings.GLOBAL.VAULT_SERVER_URL,
                        cert=(settings.CLIENT_CERT_FILEPATH,
                              settings.CLIENT_KEY_FILEPATH),
                        verify=settings.GLOBAL.SERVER_CERT_FILEPATH)
        self.connection_loop(self.vault_init)
        self.connection_loop(self.vault_unseal)
        self.connection_loop(self.vault_root_token_auth)

    def phase_1_startup(self):
        """foo
        """
        logger.debug("Begin first phase initialization")
        self.connection_loop(self.vault_enable_audit_file)
        self.connection_loop(self.vault_enable_cert_auth_method)
        self.connection_loop(self.vault_enable_pki_int_secrets_engine)
        self.connection_loop(self.vault_write_int_ca_csr)

    def phase_2_startup(self):
        """foo
        """
        logger.info("Begin second phase initialization")
        self.connection_loop(self.vault_setup_int_ca_certs)
        self.connection_loop(self.vault_create_acl_policy,
                             policy_name_str="int_ca_cert_issuer")
        self.connection_loop(self.vault_enable_kv_secrets_engine)
        self.connection_loop(self.vault_create_watcher_service_acl)
        self.connection_loop(self.vault_create_rest_service_acl)
        self.connection_loop(self.vault_generate_client_cert,
                             common_name="watcher")
        self.connection_loop(self.vault_generate_client_cert,
                             common_name="rest")
        # NOTE: The SAE client will not interact directly with the
        # Vault instance. Therefore, no need to create an ACL policy.
        # NOTE: An SAE CSR may need to be signed instead of using this
        # cert and key combination. This is for convenience.
        self.connection_loop(self.vault_generate_client_cert,
                             common_name="sae")

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
        if not secret:
            if response:
                if VaultClient._is_json(response):
                    logger.debug(f"""{json.dumps(response,
                                                 indent=2,
                                                 sort_keys=True)}""")
                else:
                    logger.debug(f"{response}")
            else:
                logger.debug("No response")
        else:
            logger.debug("REDACTED")

    def write_secrets(self):
        """foo
        """
        json_output_str = json.dumps({"keys": self.unseal_keys,
                                      "root_token": self.root_token},
                                     indent=2,
                                     sort_keys=True)
        logger.info(f"Writing Vault secrets to: {settings.GLOBAL.VAULT_SECRETS_FILEPATH}")
        with open(settings.GLOBAL.VAULT_SECRETS_FILEPATH, "w") as f:
            f.write(json_output_str)

    def vault_init(self):
        """foo
        """
        if not self.vclient.sys.is_initialized():
            self.secret_shares: int = settings.SECRET_SHARES
            self.secret_threshold: int = settings.SECRET_THRESHOLD
            assert self.secret_threshold <= self.secret_shares
            self.init_response = \
                self.vclient.sys.initialize(secret_shares=self.secret_shares,
                                            secret_threshold=self.secret_threshold)
            if self.vclient.sys.is_initialized():
                # TODO: needs response checking
                # TODO: Secret Exposure
                self.root_token = self.init_response["root_token"]
                self.unseal_keys = self.init_response["keys"]
                self.write_secrets()
                logger.info("Vault instance initialization successful")
                self._dump_response(self.init_response, secret=True)
            else:
                logger.error("Vault instance initialization failed")
                self._dump_response(self.init_response, secret=False)
        else:
            logger.info("Vault instance already initialized")

    def vault_unseal(self):
        """foo
        """
        if self.vclient.sys.is_sealed():
            # TODO: handle when init has already happened
            assert self.init_response is not None
            assert len(self.unseal_keys) >= self.secret_threshold
            # TODO: Secret Exposure
            self.unseal_response = \
                self.vclient.sys.submit_unseal_keys(self.unseal_keys)
            if not self.vclient.sys.is_sealed():
                logger.debug("Vault instance unsealing successful")
                self._dump_response(self.unseal_response, secret=False)
            else:
                logger.error("Vault instance unseal failed")
                self._dump_response(self.unseal_response, secret=False)
        else:
            logger.info("Vault instance already unsealed")

    def vault_root_token_auth(self):
        """foo
        """
        if not self.vclient.is_authenticated():
            # TODO: Secret Exposure
            if not hasattr(self, "root_token"):
                self.root_token = \
                    json.loads(open(settings.GLOBAL.VAULT_SECRETS_FILEPATH,
                                    "r").read())["root_token"]

            self.vclient.token = self.root_token
            if self.vclient.is_authenticated():
                logger.debug("Client has authenticated with Vault instance")
            else:
                logger.error("Client failed to authenticate")
        else:
            logger.info("Client is already authenticated")

    def vault_enable_audit_file(self):
        """foo
        """
        audit_devices = self.vclient.sys.list_enabled_audit_devices()
        logger.debug("Currently enabled audit devices:")
        self._dump_response(audit_devices, secret=False)
        logger.debug("Attempt to enable file audit device")
        device_type_str = "file"
        description_str = "File to hold audit events"
        options_dict = {"file_path": f"{settings.GLOBAL.LOG_DIRPATH}/audit.log"}
        self.enable_audit_response = \
            self.vclient.sys.enable_audit_device(device_type_str,
                                                 description=description_str,
                                                 options=options_dict)
        logger.debug("Enable audit response okay:")
        self._dump_response(self.enable_audit_response.ok, secret=False)
        audit_devices = self.vclient.sys.list_enabled_audit_devices()
        logger.debug("Currently enabled audit devices:")
        self._dump_response(audit_devices, secret=False)

    def vault_enable_cert_auth_method(self):
        """foo
        """
        auth_methods = self.vclient.sys.list_auth_methods()
        logger.debug("Currently enabled auth methods:")
        self._dump_response(auth_methods, secret=False)
        method_type_str = "cert"
        description_str = "TLS Authentication"
        logger.debug("Attempt to enable cert auth method")
        self.enable_cert_response = \
            self.vclient.sys.enable_auth_method(method_type=method_type_str,
                                                description=description_str)
        logger.debug("Enable cert response okay:")
        self._dump_response(self.enable_cert_response.ok, secret=False)
        auth_methods = self.vclient.sys.list_auth_methods()
        logger.debug("Currently enabled auth methods:")

    def vault_enable_pki_int_secrets_engine(self):
        """foo
        """
        secrets_backends = self.vclient.sys.list_mounted_secrets_engines()
        logger.debug("Currently enabled secrets engines:")
        self._dump_response(secrets_backends, secret=False)
        backend_type_str = "pki"
        mount_point = "pki_int"
        description_str = "Intermediate CA Certificate Store to be used in Authenication"
        config_dict = {
            "default_lease_ttl": "8760h",
            "max_lease_ttl": "87600h"
        }
        logger.debug("Attempt to enable pki_int secrets engine")
        self.enable_pki_response = \
            self.vclient.sys.enable_secrets_engine(backend_type_str,
                                                   path=mount_point,
                                                   description=description_str,
                                                   config=config_dict)
        logger.debug("Enable pki_int secrets egine response okay:")
        self._dump_response(self.enable_pki_response.ok, secret=False)
        secrets_backends = self.vclient.sys.list_mounted_secrets_engines()
        logger.debug("Currently enabled secrets engines:")
        self._dump_response(secrets_backends, secret=False)

    def write_pki_int_csr_pem_file(self):
        """foo
        """
        logger.info(f"Writing Vault intermediate PKI CSR to: {settings.GLOBAL.PKI_INT_CSR_PEM_FILEPATH}")
        with open(settings.GLOBAL.PKI_INT_CSR_PEM_FILEPATH, "w") as f:
            f.write(self.int_ca_csr)

    def vault_write_int_ca_csr(self):
        """foo
        """
        mount_point = "pki_int"
        type_str = "exported"
        common_name = "Vault Intermediate CA pki_int mount point"
        extra_param_dict = {
            "format": "pem",
            "key_type": "rsa",
            "key_bits": "4096",
            "ou": "Quantum Hacking",
            "organization": "Quantum Internet Technologies LLC",
            "country": "US",
            "province": "Texas",
            "locality": "Austin",
            "ttl": "87600h"
        }
        logger.debug("Attempting to generate intermediate CA certificate/private key")
        # TODO: Secret Exposure
        self.gen_int_ca_response = \
            self.vclient.secrets.pki.\
            generate_intermediate(type_str,
                                  common_name=common_name,
                                  mount_point=mount_point,
                                  extra_params=extra_param_dict)
        logger.debug("Generate intermediate CA response:")
        self._dump_response(self.gen_int_ca_response, secret=True)
        self.int_ca_csr = self.gen_int_ca_response["data"]["csr"]
        logger.debug("Intermediate CA Certificate Signing Request (CSR):")
        self._dump_response(self.int_ca_csr, secret=False)
        self.write_pki_int_csr_pem_file()

    def vault_setup_int_ca_certs(self):
        """foo
        """
        logger.debug("Attempt to read in signed intermediate CA CSR")
        # TODO: handle FileNotFoundError exception
        self.int_ca_cert = \
            open(settings.GLOBAL.PKI_INT_CERT_PEM_FILEPATH, "r").read()
        mount_point = "pki_int"
        self.set_int_ca_cert_response = self.vclient.secrets.pki.\
            set_signed_intermediate(certificate=self.int_ca_cert,
                                    mount_point=mount_point)
        logger.debug("Intermediate CA cert response:")
        self._dump_response(self.set_int_ca_cert_response.ok, secret=False)
        params_dict = {
            "issuing_certificates": f"{settings.GLOBAL.VAULT_SERVER_URL}/v1/{mount_point}/ca",
            "crl_distribution_points": f"{settings.GLOBAL.VAULT_SERVER_URL}/v1/{mount_point}/crl",
            "ocsp_servers": ""
        }
        logger.debug("Attempting to set intermediate CA URLs")
        url_response = \
            self.vclient.secrets.pki.set_urls(params=params_dict,
                                              mount_point=mount_point)
        logger.debug("Set intermediate CA URLs response okay:")
        self._dump_response(url_response.ok, secret=False)
        role_name_str = "role_int_ca_cert_issuer"
        role_param_dict = {
            "allow_localhost": "true",
            "allow_subdomains": "true",
            "allow_glob_domains": "true",
            "enforce_hostnames": "false",
            "allow_any_name": "true",
            "allow_ip_sans": "true",
            "server_flag": "true",
            "client_flag": "true",
            "key_type": "rsa",
            "key_bits": "2048",
            "generate_lease": "true",
            "ou": "Quantum Hacking",
            "organization": "Quantum Internet Technologies LLC",
            "country": "US",
            "province": "Texas",
            "locality": "Austin",
            "ttl": "8760h",
            "max_ttl": "87600h",
        }
        logger.debug("Attempting to create intermediate CA role for cert issuing")
        create_role_response = \
            self.vclient.secrets.pki.\
            create_or_update_role(name=role_name_str,
                                  extra_params=role_param_dict,
                                  mount_point=mount_point)
        logger.debug("Create intermediate CA role response okay:")
        self._dump_response(create_role_response.ok, secret=False)
        logger.debug("Attempt to read newly created role")
        read_role_resposne = \
            self.vclient.secrets.pki.read_role(name=role_name_str,
                                               mount_point=mount_point)
        logger.debug("Read newly created role:")
        self._dump_response(read_role_resposne, secret=False)

    @staticmethod
    def vault_read_hcl_file(policy_name_str, is_template=False):
        """foo
        """
        template_dir = ""
        template_str = ""
        if is_template:
            template_dir = "templates/"
            template_str = ".template"
        filepath = f"{settings.GLOBAL.POLICIES_DIRPATH}/{template_dir}" \
            f"{policy_name_str}.policy{template_str}.hcl"
        logger.debug(f"Attempting to read file: {filepath}")
        return open(filepath, "r").read()

    def vault_create_acl_policy(self, policy_name_str):
        """foo
        """
        policy_hcl = VaultClient.vault_read_hcl_file(policy_name_str,
                                                     is_template=False)
        logger.debug("Attempt to add ACL for \"{policy_name_str}\"")
        policy_response = \
            self.vclient.sys.create_or_update_policy(name=policy_name_str,
                                                     policy=policy_hcl)
        logger.debug("Add ACL policy response okay:")
        self._dump_response(policy_response.ok, secret=False)
        logger.debug("Attemp to read back policy")
        read_policy_response = \
            self.vclient.get_policy(name=policy_name_str, parse=True)
        logger.debug("Read policy response:")
        self._dump_response(read_policy_response, secret=False)

    def vault_generate_client_cert(self, common_name: str):
        """foo
        """
        role_str = "role_int_ca_cert_issuer"
        mount_point = "pki_int"
        extra_param_dict = {
            "alt_names": settings.CLIENT_ALT_NAMES,
            "format_str": "pem",
            "private_key_format_str": "pem",
            "exclude_cn_from_sans": "false"
        }
        logger.debug(f"Attempt to issue \"{common_name}\" client certificate")
        logger.debug(f"Adding SAN: \"{settings.CLIENT_ALT_NAMES}\" to client certificate")
        gen_cert_response = \
            self.vclient.secrets.pki.\
            generate_certificate(name=role_str,
                                 common_name=common_name,
                                 mount_point=mount_point,
                                 extra_params=extra_param_dict)
        logger.debug(f"\"{common_name}\" client cert response:")
        self._dump_response(gen_cert_response, secret=True)
        ca_chain_pem_str = gen_cert_response["data"]["ca_chain"]
        cert_pem_str = gen_cert_response["data"]["certificate"]
        private_key_pem_str = gen_cert_response["data"]["private_key"]
        client_dirpath = f"{settings.GLOBAL.CERT_DIRPATH}/{common_name}"
        # Client dir private key read-only
        client_perms: oct = stat.S_IRUSR
        client_admin_dirpath = f"{settings.GLOBAL.ADMIN_DIRPATH}/{common_name}"
        # Admin dir private key world-readable
        client_admin_perms: oct = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        VaultClient.\
            write_client_credentials(dirpath=client_dirpath,
                                     common_name=common_name,
                                     permissions=client_perms,
                                     client_cert=cert_pem_str,
                                     client_private_key=private_key_pem_str,
                                     ca_chain=ca_chain_pem_str)
        VaultClient.\
            write_client_credentials(dirpath=client_admin_dirpath,
                                     common_name=common_name,
                                     permissions=client_admin_perms,
                                     client_cert=cert_pem_str,
                                     client_private_key=private_key_pem_str,
                                     ca_chain=ca_chain_pem_str)

    @staticmethod
    def write_client_credentials(dirpath: str, common_name: str,
                                 permissions: oct, client_cert: str,
                                 client_private_key: str, ca_chain: str):
        """foo
        """
        # Ensure the directory exists
        pathlib.Path(dirpath).mkdir(parents=True, exist_ok=True)
        # Write CA cert chain as 0o644
        with open(os.open(f"{dirpath}/"
                          f"{common_name}{settings.GLOBAL.CA_CHAIN_SUFFIX}",
                          os.O_CREAT | os.O_WRONLY,
                          stat.S_IRUSR | stat.S_IWUSR |
                          stat.S_IRGRP | stat.S_IROTH), "w") as f:
            # Write client cert first
            f.write(client_cert + "\n")
            # Then, each link in the CA chain up to the root CA
            for ca_cert in ca_chain:
                f.write(ca_cert + "\n")
        # User provided permissions for writing private key
        with open(os.open(f"{dirpath}/"
                          f"{common_name}{settings.GLOBAL.KEY_SUFFIX}",
                          os.O_CREAT | os.O_WRONLY,
                          permissions), "w") as f:
            # Write out the client's private key
            f.write(client_private_key)

    def vault_enable_kv_secrets_engine(self):
        """foo
        """
        secrets_backends = self.vclient.sys.list_mounted_secrets_engines()
        logger.debug("Currently enabled secrets engines:")
        self._dump_response(secrets_backends, secret=False)
        backend_type_str = "kv"
        mount_point = settings.GLOBAL.VAULT_KV_ENDPOINT
        description_str = "Key/Value Store for QKD Keys."
        config_dict = {
            "default_lease_ttl": "",
            "max_lease_ttl": ""
        }
        # This must be set to get Key/Value Version 2
        options_dict = {
            "version": 2
        }
        logger.debug("Attempt to enable kv version 2 secrets engine")
        self.enable_kv_response = \
            self.vclient.sys.enable_secrets_engine(backend_type_str,
                                                   path=mount_point,
                                                   description=description_str,
                                                   config=config_dict,
                                                   options=options_dict)
        logger.debug("Enable kv version 2 secrets egine response okay:")
        self._dump_response(self.enable_kv_response.ok, secret=False)
        secrets_backends = self.vclient.sys.list_mounted_secrets_engines()
        logger.debug("Currently enabled secrets engines:")
        self._dump_response(secrets_backends, secret=False)
        # Enforce check-and-set versioning
        cas_required = True
        logger.debug(f"Attempt to configure secrets engine mount_point: \"{mount_point}\"")
        # TODO: Vault sometimes returns a 400 status as it is "upgrading to KV V2.
        # Need to make this retry if there is a failure:
        # hvac.exceptions.InvalidRequest: Upgrading from non-versioned to versioned data. This backend will be unavailable for a brief period and will resume service shortly., on post https://vault:8200/v1/QKEYS/config
        time.sleep(3)
        set_config_response = \
            self.vclient.secrets.kv.v2.\
            configure(mount_point=mount_point, cas_required=cas_required)
        logger.debug(f"Set secret engine mount_point: \"{mount_point}\" reponse ok:")
        self._dump_response(set_config_response.ok, secret=False)
        logger.debug("Attempt to read specific secrets engine configuration")
        read_config_response = \
            self.vclient.secrets.kv.v2.\
            read_configuration(mount_point=mount_point)
        logger.debug(f"Read secret engine mount_point: \"{mount_point}\" reponse:")
        self._dump_response(read_config_response, secret=False)

    def vault_create_watcher_service_acl(self):
        """foo
        """
        policy_name_str = "watcher"
        policy_template = \
            VaultClient.vault_read_hcl_file(policy_name_str=policy_name_str,
                                            is_template=True)
        policy_str = policy_template
        policy_str = policy_str.replace("<<<KV_MOUNT_POINT>>>",
                                        settings.GLOBAL.VAULT_KV_ENDPOINT)
        policy_str = policy_str.replace("<<<QKDE_ID>>>",
                                        settings.GLOBAL.VAULT_QKDE_ID)
        policy_str = policy_str.replace("<<<QCHANNEL_ID>>>",
                                        settings.GLOBAL.VAULT_QCHANNEL_ID)
        filepath = f"{settings.GLOBAL.POLICIES_DIRPATH}/" \
                   f"{policy_name_str}.policy.hcl"
        logger.debug(f"Writing out policy to: {filepath}")
        with open(filepath, "w") as f:
            f.write(policy_str)
        self.vault_create_acl_policy(policy_name_str=policy_name_str)

    def vault_create_rest_service_acl(self):
        """foo
        """
        policy_name_str = "rest"
        policy_template = \
            VaultClient.vault_read_hcl_file(policy_name_str=policy_name_str,
                                            is_template=True)
        policy_str = policy_template
        policy_str = policy_str.replace("<<<KV_MOUNT_POINT>>>",
                                        settings.GLOBAL.VAULT_KV_ENDPOINT)
        policy_str = policy_str.replace("<<<QKDE_ID>>>",
                                        settings.GLOBAL.VAULT_QKDE_ID)
        policy_str = policy_str.replace("<<<QCHANNEL_ID>>>",
                                        settings.GLOBAL.VAULT_QCHANNEL_ID)
        policy_str = policy_str.replace("<<<LEDGER_ID>>>",
                                        settings.GLOBAL.VAULT_LEDGER_ID)
        filepath = f"{settings.GLOBAL.POLICIES_DIRPATH}/" \
                   f"{policy_name_str}.policy.hcl"
        logger.debug(f"Writing out policy to: {filepath}")
        with open(filepath, "w") as f:
            f.write(policy_str)
        self.vault_create_acl_policy(policy_name_str=policy_name_str)


if __name__ == "__main__":
    vclient = VaultClient()
