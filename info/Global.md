# Global Configuration

Global configuration options for any Docker service to use may be found in the [global_config.py](../common/global_config.py) file.

These configuration variables are accessible in all Python-based services and will take the form `settings.GLOBAL.<VARIABLE_NAME>` where `<VARIABLE_NAME>` is substituted with one below.

Most of these variables will not need updating in any typical scenarios.

| Variable | Type | Set Value | Description |
| --- | --- | --- | --- |
| LOCAL_KME_ID | str | os.environ.get("LOCAL_KME_ID", "kme1") | Local KME host ID; set by top-level Makefile |
| REMOTE_KME_ID | str | os.environ.get("REMOTE_KME_ID", "kme2") | Remote KME host ID; set by top-level Makefile |
| LOCAL_SAE_ID | str | os.environ.get("LOCAL_SAE_ID", "sae1") | Local SAE ID; set by top-level Makefile |
| REMOTE_SAE_ID | str | os.environ.get("REMOTE_SAE_ID", "sae2") | Remote SAE ID; set by top-level Makefile |
| SHOW_SECRETS | bool | True | Show potentially senstive information (e.g. keying material) in server logs when log-level is at least Debug |
| VAULT_NAME | str | "vault" | Local Vault instance Docker service name |
| VAULT_SERVER_URL | str | f"https://{VAULT_NAME}:8200" | URL to reach local Vault instance |
| CA_CHAIN_SUFFIX | str | ".ca-chain.cert.pem" | Certificate file suffixes (all are complete cert chain files) |
| KEY_SUFFIX | str | ".key.pem" | Private key file suffix |
| CSR_SUFFIX | str | ".csr.pem" | Certificate Signing Request file suffix |
| DIGEST_KEY | bytes | b"TODO: Change me; no hard code" | HMAC SHA256 digest key used in comparing key HMACs across KME hosts; Should match on both KME hosts |
| EPOCH_FILES_DIRPATH | str | "/epoch_files" | In-container directory path where qcrypto files are stored; must match docker-compose yaml file volume locations |
| NOTIFY_PIPE_FILEPATH | str | f"{EPOCH_FILES_DIRPATH}/notify.pipe" | In-container FIFO path used in notifier and watcher services for communication on when new keying information is available; must match docker compose yaml file volume locations |
| DIGEST_FILES_DIRPATH | str | "/digest_files" | In-container directory path where HMAC digest files of keying material are stored; must match docker-compose yaml file volume locations |
| CERT_DIRPATH | str | "/certificates/production" | In-container directory path where production TLS certificates are stored; must match docker-compose yaml file volume locations |
| ADMIN_DIRPATH | str | f"{CERT_DIRPATH}/admin" | In-container directory path where admin-readable TLS certificates are stored; for convenience, not production per se; must match docker-compose yaml file volume locations|
| POLICIES_DIRPATH | str | "/vault/policies" | In-container directory path where pre-generated and template policies for Vault roles are stored (read-only); must match docker-compose yaml file volume locations |
| LOG_DIRPATH | str | "/vault/logs" | In-container directory path where local Vault instance logs (if configured to write to file) are stored; must match docker-compose yaml file volume locations|
| VAULT_SECRETS_FILEPATH | str | f"{ADMIN_DIRPATH}/{VAULT_NAME}/SECRETS" | In-container file path to write out local Vault instance unseal keys and root token (sensitive material); must match docker compose yaml file volume locations |
| VAULT_INIT_NAME | str | "vault_init" | Local Vault initialization client Docker service name |
| SERVER_CERT_FILEPATH | str | f"{CERT_DIRPATH}/{VAULT_INIT_NAME}/{VAULT_NAME}{CA_CHAIN_SUFFIX}" | In-container local Vault server certificate chain file path for Vault initialization client to use in mutual TLS verification of Vault server identity |
| PKI_INT_CSR_PEM_FILEPATH | str | f"{CERT_DIRPATH}/{VAULT_INIT_NAME}/pki_int{CSR_SUFFIX}" | Local Vault instance PKI secrets engine certificate signing request file path to be signed by CERTAUTH service |
| PKI_INT_CERT_PEM_FILEPATH | str | f"{CERT_DIRPATH}/{VAULT_INIT_NAME}/pki_int{CA_CHAIN_SUFFIX}" | Local Vault instance PKI secrets engine certificate chain file produced by CERTAUTH |
| VAULT_MAX_CONN_ATTEMPTS | int | 10 | Number of attempts to try and connect to local Vault instance before failure |
| BACKOFF_FACTOR | float | 1.0 | Backoff multiplication factor used when slowing down connection attempts |
| BACKOFF_MAX | float | 64.0  # seconds | Maximum backoff time in connection attempts |
| VAULT_KV_ENDPOINT | str | "QKEYS" | Vault Key Value secrets engine mount point name |
| VAULT_QKDE_ID | str | "QKDE0001" | Vault unique QKD Entity ID  |
| VAULT_QCHANNEL_ID | str | "ALICEBOB" | Vault unique quantum channel ID |
| VAULT_LEDGER_ID | str | "LEDGER" | Vault KeyIDLedger directory to store key metadata between KME hosts |
