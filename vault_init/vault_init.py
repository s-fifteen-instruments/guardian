#!/usr/bin/env python3

import json
import logging as logger
import hvac
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
    ADMIN_DIRPATH: str = f"{CERT_DIRPATH}/admin"
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
        self.vclient: hvac.Client = \
            hvac.Client(url=vaultClient.VAULT_URI,
                        cert=(vaultClient.CLIENT_CERT_FILEPATH,
                              vaultClient.CLIENT_KEY_FILEPATH),
                        verify=vaultClient.SERVER_CERT_FILEPATH)
        self.connection_loop(self.vault_init)
        self.connection_loop(self.vault_unseal)
        self.connection_loop(self.vault_auth)
        self.connection_loop(self.vault_enable_audit_file)
        self.connection_loop(self.vault_enable_auth_method)
        # self.connection_loop(self.vault_enable_pki_secrets_engine)
        # self.connection_loop(self.vault_setup_ca_certs)
        self.connection_loop(self.vault_enable_pki_int_secrets_engine)
        self.connection_loop(self.vault_setup_int_ca_certs)
        # self.connection_loop(self.vault_create_acl_policy)

    def connection_loop(self, connection_callback) -> None:
        """foo
        """
        self.max_attempts: int = vaultClient.MAX_CONN_ATTEMPTS
        self.backoff_factor: float = vaultClient.BACKOFF_FACTOR
        self.backoff_max: float = vaultClient.BACKOFF_MAX

        attempt_num: int = 0
        total_stall_time: float = 0.0
        while attempt_num < self.max_attempts:
            attempt_num = attempt_num + 1
            logger.info(f"Connection Attempt #: {attempt_num}")
            try:
                logger.debug("Read Vault instance health status")
                health_response = self.vclient.sys.read_health_status(method="GET")
                logger.debug("Vault server status:")
                logger.debug(f"Health response type {type(health_response)}")
                if isinstance(health_response, dict):
                    self._dump_response(health_response)
                else:
                    self._dump_response(health_response.json())

                if callable(connection_callback):
                    logger.debug(f"Attempting function callback: {connection_callback.__name__}()")
                    connection_callback()
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

    def write_secrets(self):
        """foo
        """
        json_output_str = json.dumps({"keys": self.unseal_keys,
                                      "root_token": self.root_token},
                                     indent=2,
                                     sort_keys=True)
        logger.info(f"Writing Vault secrets to: {vaultClient.VAULT_SECRETS_FILEPATH}")
        with open(vaultClient.VAULT_SECRETS_FILEPATH, "w") as f:
            f.write(json_output_str)

    def vault_init(self):
        """foo
        """
        if not self.vclient.sys.is_initialized():
            self.secret_shares: int = vaultClient.SECRET_SHARES
            self.secret_threshold: int = vaultClient.SECRET_THRESHOLD
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
                self._dump_response(self.init_response)
            else:
                logger.error("Vault instance initialization failed")
                self._dump_response(self.init_response)
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
                self._dump_response(self.unseal_response)
            else:
                logger.error("Vault instance unseal failed")
                self._dump_response(self.unseal_response)
        else:
            logger.info("Vault instance already unsealed")

    def vault_auth(self):
        """foo
        """
        if not self.vclient.is_authenticated():
            # TODO: Secret Exposure
            if self.root_token:
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
        self._dump_response(audit_devices)
        logger.debug("Attempt to enable file audit device")
        device_type_str = "file"
        description_str = "File to hold audit events"
        options_dict = {"file_path": f"{vaultClient.LOG_DIRPATH}/audit.log"}
        self.enable_audit_response = \
            self.vclient.sys.enable_audit_device(device_type_str,
                                                 description=description_str,
                                                 options=options_dict)
        logger.debug("Enable audit response okay:")
        self._dump_response(self.enable_audit_response.ok)
        audit_devices = self.vclient.sys.list_enabled_audit_devices()
        logger.debug("Currently enabled audit devices:")
        self._dump_response(audit_devices)

    def vault_enable_auth_method(self):
        """foo
        """
        auth_methods = self.vclient.sys.list_auth_methods()
        logger.debug("Currently enabled auth methods:")
        self._dump_response(auth_methods)
        logger.debug("Attempt to enable cert auth method")
        self.enable_cert_response = self.vclient.sys.enable_auth_method("cert")
        logger.debug("Enable cert response okay:")
        self._dump_response(self.enable_cert_response.ok)
        auth_methods = self.vclient.sys.list_auth_methods()
        logger.debug("Currently enabled auth methods:")

    def vault_enable_pki_secrets_engine(self):
        """foo
        """
        secrets_backends = self.vclient.sys.list_mounted_secrets_engines()
        logger.debug("Currently enabled secrets engines:")
        self._dump_response(secrets_backends)
        backend_type_str = "pki"
        mount_point = "pki"
        description_str = "Root CA Certificate Store to be used in Authenication"
        config_dict = {
            "default_lease_ttl": "87600h",
            "max_lease_ttl": "87600h"
        }
        logger.debug("Attempt to enable pki secrets engine")
        self.enable_pki_response = \
            self.vclient.sys.enable_secrets_engine(backend_type_str,
                                                   path=mount_point,
                                                   description=description_str,
                                                   config=config_dict)
        logger.debug("Enable pki secrets egine response okay:")
        self._dump_response(self.enable_pki_response.ok)
        secrets_backends = self.vclient.sys.list_mounted_secrets_engines()
        logger.debug("Currently enabled secrets engines:")
        self._dump_response(secrets_backends)

    def vault_setup_ca_certs(self):
        """foo
        """
        mount_point = "pki"
        type_str = "exported"
        common_name = "Vault Root CA pki mount point"
        extra_param_dict = {
            "format": "pem",
            "key_type": "rsa",
            "key_bits": "4096",
            "ou": "Quantum Hacking",
            "organization": "Quantum Internet Technologies LLC",
            "country": "US",
            "province": "Texas",
            "locality": "Austin",
            # "valt_names": "vault,vault.localhost,localhost",
            # "ip_sans": "127.0.0.1"
        }
        logger.debug("Attempting to generate root CA certificate/private key")
        # TODO: Secret Exposure
        self.gen_root_ca_response = \
            self.vclient.secrets.pki.generate_root(type_str,
                                                   common_name=common_name,
                                                   mount_point=mount_point,
                                                   extra_params=extra_param_dict)
        logger.debug("Generate root CA response:")
        self._dump_response(self.gen_root_ca_response)
        cert_list_reponse = \
            self.vclient.secrets.pki.list_certificates(mount_point=mount_point)
        logger.debug("Current pki certificates:")
        self._dump_response(cert_list_reponse)
        mount_point = "pki"
        params_dict = {
            "issuing_certificates": f"https://vault:8200/v1/{mount_point}/ca",
            "crl_distribution_points": f"https://vault:8200/v1/{mount_point}/crl",
            "ocsp_servers": ""
        }
        logger.debug("Attempting to set root CA URLs")
        url_response = \
            self.vclient.secrets.pki.set_urls(params=params_dict,
                                              mount_point=mount_point)
        logger.debug("Set root CA URLs response okay:")
        self._dump_response(url_response.ok)

    def vault_enable_pki_int_secrets_engine(self):
        """foo
        """
        secrets_backends = self.vclient.sys.list_mounted_secrets_engines()
        logger.debug("Currently enabled secrets engines:")
        self._dump_response(secrets_backends)
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
        self._dump_response(self.enable_pki_response.ok)
        secrets_backends = self.vclient.sys.list_mounted_secrets_engines()
        logger.debug("Currently enabled secrets engines:")
        self._dump_response(secrets_backends)

    def write_pki_int_csr_pem_file(self):
        """foo
        """
        logger.info(f"Writing Vault intermediate PKI CSR to: {vaultClient.PKI_INT_CSR_PEM_FILEPATH}")
        with open(vaultClient.PKI_INT_CSR_PEM_FILEPATH, "w") as f:
            f.write(self.int_ca_csr)

    def vault_setup_int_ca_certs(self):
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
            self.vclient.secrets.pki.generate_intermediate(type_str,
                                                           common_name=common_name,
                                                           mount_point=mount_point,
                                                           extra_params=extra_param_dict)
        logger.debug("Generate intermediate CA response:")
        self._dump_response(self.gen_int_ca_response)
        self.int_ca_csr = self.gen_int_ca_response["data"]["csr"]
        logger.debug("Intermediate CA Certificate Signing Request (CSR):")
        self._dump_response(self.int_ca_csr)
        self.write_pki_int_csr_pem_file()
        """
        logger.debug("Attempt to sign intermediate CA CSR with root CA")
        root_ca_mount_point = "pki"
        self.sign_int_ca_csr_response = \
            self.vclient.secrets.pki.sign_intermediate(csr=self.int_ca_csr,
                                                       common_name=common_name,
                                                       mount_point=root_ca_mount_point,
                                                       extra_params=extra_param_dict)
        logger.debug("Sign intermediate CA response:")
        self._dump_response(self.sign_int_ca_csr_response)
        int_ca_cert = self.sign_int_ca_csr_response["data"]["certificate"]
        logger.debug("Attempt to set signed intermediate CA certificate")
        set_int_ca_cert_response = \
            self.vclient.secrets.pki.set_signed_intermediate(certificate=int_ca_cert,
                                                             mount_point=mount_point)
        logger.debug("Set signed intermediate CA certificate response okay:")
        self._dump_response(set_int_ca_cert_response.ok)
        params_dict = {
            "issuing_certificates": f"https://vault:8200/v1/{mount_point}/ca",
            "crl_distribution_points": f"https://vault:8200/v1/{mount_point}/crl",
            "ocsp_servers": ""
        }
        logger.debug("Attempting to set intermediate CA URLs")
        url_response = \
            self.vclient.secrets.pki.set_urls(params=params_dict,
                                              mount_point=mount_point)
        logger.debug("Set intermediate CA URLs response okay:")
        self._dump_response(url_response.ok)
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
            # "allowed_domains": "vault,vault.localhost,localhost",
            # "not_before_duration": "96h"
        }
        logger.debug("Attempting to create intermediate CA role for cert issuing")
        create_role_response = \
            self.vclient.secrets.pki.create_or_update_role(name=role_name_str,
                                                           extra_params=role_param_dict,
                                                           mount_point=mount_point)
        logger.debug("Create intermediate CA role response okay:")
        self._dump_response(create_role_response.ok)
        logger.debug("Attempt to read newly created role")
        read_role_resposne = \
            self.vclient.secrets.pki.read_role(name=role_name_str,
                                               mount_point=mount_point)
        logger.debug("Read newly created role:")
        self._dump_response(read_role_resposne)
        """

    def vault_setup_int_ca_certs_internal_ca(self):
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
            self.vclient.secrets.pki.generate_intermediate(type_str,
                                                           common_name=common_name,
                                                           mount_point=mount_point,
                                                           extra_params=extra_param_dict)
        logger.debug("Generate intermediate CA response:")
        self._dump_response(self.gen_int_ca_response)
        int_ca_csr = self.gen_int_ca_response["data"]["csr"]
        logger.debug("Intermediate CA Certificate Signing Request (CSR):")
        self._dump_response(int_ca_csr)
        logger.debug("Attempt to sign intermediate CA CSR with root CA")
        root_ca_mount_point = "pki"
        self.sign_int_ca_csr_response = \
            self.vclient.secrets.pki.sign_intermediate(csr=int_ca_csr,
                                                       common_name=common_name,
                                                       mount_point=root_ca_mount_point,
                                                       extra_params=extra_param_dict)
        logger.debug("Sign intermediate CA response:")
        self._dump_response(self.sign_int_ca_csr_response)
        int_ca_cert = self.sign_int_ca_csr_response["data"]["certificate"]
        logger.debug("Attempt to set signed intermediate CA certificate")
        set_int_ca_cert_response = \
            self.vclient.secrets.pki.set_signed_intermediate(certificate=int_ca_cert,
                                                             mount_point=mount_point)
        logger.debug("Set signed intermediate CA certificate response okay:")
        self._dump_response(set_int_ca_cert_response.ok)
        params_dict = {
            "issuing_certificates": f"https://vault:8200/v1/{mount_point}/ca",
            "crl_distribution_points": f"https://vault:8200/v1/{mount_point}/crl",
            "ocsp_servers": ""
        }
        logger.debug("Attempting to set intermediate CA URLs")
        url_response = \
            self.vclient.secrets.pki.set_urls(params=params_dict,
                                              mount_point=mount_point)
        logger.debug("Set intermediate CA URLs response okay:")
        self._dump_response(url_response.ok)
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
            # "allowed_domains": "vault,vault.localhost,localhost",
            # "not_before_duration": "96h"
        }
        logger.debug("Attempting to create intermediate CA role for cert issuing")
        create_role_response = \
            self.vclient.secrets.pki.create_or_update_role(name=role_name_str,
                                                           extra_params=role_param_dict,
                                                           mount_point=mount_point)
        logger.debug("Create intermediate CA role response okay:")
        self._dump_response(create_role_response.ok)
        logger.debug("Attempt to read newly created role")
        read_role_resposne = \
            self.vclient.secrets.pki.read_role(name=role_name_str,
                                               mount_point=mount_point)
        logger.debug("Read newly created role:")
        self._dump_response(read_role_resposne)

    def vault_create_acl_policy(self):
        """foo
        """
        policy_name_str = "policy_int_ca_cert_issuer"
        policy_json = """
            path "pki_int/issue" {
                capabilities = ["create", "update"]
            }

            path "pki/cert/ca" {
                capabilities = ["read"]
            }

            path "auth/token/renew" {
                capabilities = ["update"]
            }

            path "auth/token/renew-self" {
                capabilities = ["update"]
            }
        """
        logger.debug("Attempt to add ACL for int CA issuer")
        policy_response = \
            self.vclient.sys.create_or_update_policy(name=policy_name_str,
                                                     policy=policy_json,
                                                     pretty_print=False)
        logger.debug("Add ACL policy response okay:")
        self._dump_response(policy_response.ok)
        logger.debug("Attemp to read back policy")
        read_policy_response = \
            self.vclient.sys.read_policy(name=policy_name_str)
        logger.debug("Read policy response:")
        self._dump_response(read_policy_response)


if __name__ == "__main__":
    # init_vault()
    vclient = vaultClient()
