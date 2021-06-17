# Unsealer Client Configuration

Unsealer configuration options passed to the `unsealer` Docker service found in the [unsealer_config.py](../common/unsealer_config.py) file.

| Variable | Type | Set Value | Description |
| --- | --- | --- | --- |
| UNSEALER_LOG_LEVEL | str | os.environ.get("UNSEALER_LOG_LEVEL", str(logging.info)) | Unsealer client log-level pulled from the environment; set by the log.env file |
| CLIENT_CERT_FILEPATH | str | f"{GLOBAL.CERT_DIRPATH}/{GLOBAL.VAULT_INIT_NAME}/{GLOBAL.VAULT_INIT_NAME}{GLOBAL.CA_CHAIN_SUFFIX}" | In-container file path for Unsealer client certificate chain file to communicate with the local Vault instance; must match docker-compose yaml file volume locations |
| CLIENT_KEY_FILEPATH | str | f"{GLOBAL.CERT_DIRPATH}/{GLOBAL.VAULT_INIT_NAME}/{GLOBAL.VAULT_INIT_NAME}{GLOBAL.KEY_SUFFIX}" | In-container file path for Unsealer client private key file to communicate with the local Vault instance; must match docker-compose yaml file volume locations |
| TIME_WINDOW | float | 30.0  # seconds | How far back from the current time to look for Docker events on the docker socket that include the label 'unsealer=watch' form the local Vault instance |

