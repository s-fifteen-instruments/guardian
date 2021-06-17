# Vault Initialization Client Configuration

Vault initialization configuration options passed to the `vault_init` Docker service found in the [vault_init_config.py](../common/vault_init_config.py) file.

Most of the variables will not need updating but do pay attention to `CLIENT_ALT_NAMES`.

| Variable | Type | Set Value | Description |
| --- | --- | --- | --- |
| VAULT_INIT_LOG_LEVEL | str | os.environ.get("VAULT_INIT_LOG_LEVEL", str(logging.info)) | Vault initialization client log-level pulled from the environment; set by the log.env file |
| CLIENT_CERT_FILEPATH | str | f"{GLOBAL.CERT_DIRPATH}/{GLOBAL.VAULT_INIT_NAME}/{GLOBAL.VAULT_INIT_NAME}{GLOBAL.CA_CHAIN_SUFFIX}" | In-container file path for Vault initialization client certificate chain to communicate with the local Vault instance; must match docker-compose yaml file volume locations |
| CLIENT_KEY_FILEPATH | str | f"{GLOBAL.CERT_DIRPATH}/{GLOBAL.VAULT_INIT_NAME}/{GLOBAL.VAULT_INIT_NAME}{GLOBAL.KEY_SUFFIX}" | In-container file path for Vault initialization client private key to communicate with the local Vault instance; must match docker-compose yaml file volume locations |
SECRET_SHARES | int | 5 | Number of Shamir secret shares generated when first creating the local Vault instance |
SECRET_THRESHOLD | int | 3 | Number of Shamir secret shares needed to first initialize the local Vault instance |
CLIENT_ALT_NAMES | str | f"{GLOBAL.LOCAL_SAE_ID},{GLOBAL.LOCAL_KME_ID},traefik.{GLOBAL.LOCAL_KME_ID},localhost" | The Subject Alternative Names (SANs) that are used for Vault initialization client generated certificates; this includes the rest and watcher service certificate pairs as well as the local Traefik Dashboard |
