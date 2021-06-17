# REST API Configuration

REST API configuration options passed to the `rest` Docker service found in the [rest_config.py](../common/rest_config.py) file.

| Variable | Type | Set Value | Description |
| --- | --- | --- | --- |
REST_LOG_LEVEL | str | os.environ.get("REST_LOG_LEVEL", str(logging.info)) | REST API log-level pulled from the environment; set by the log.env file |
API_V1_STR | str | "/api/v1" | REST API version 1 URL path |
DIGEST_COMPARE_TO_FILE | bool | True | Toggle wether to compare keying material HMAC digest to the one previously written out to file by either watcher or previous request |
DIGEST_COMPARE | bool | True | Toggle wether to compare keying material to HMAC digest either written to file or also within the Vault epoch file entry |
KEY_ID_MAX_LENGTH | int | 128  # Number of characters | Max length of key ID -- usually associated with a UUID |
KEY_ID_MIN_LENGTH | int | 16  # Number of characters | Min length of a key ID -- usually associated with a UUID |
KEY_SIZE | int | 32  # Bits | Default key size in bits to serve if a key requested |
KME_ID_MAX_LENGTH | int | 32  # Number of characters | Max length of KME ID string |
KME_ID_MIN_LENGTH | int | 3  # Number of characters | Min length of KME ID string |
MAX_EX_MANADATORY_COUNT | int | 2 | Max number of 'extension_mandatory' entries; see ETSI document |
MAX_EX_OPTIONAL_COUNT | int | 2 | Max number of 'extension_optional' entries; see ETSI document |
MAX_KEY_COUNT | int | 1048576 | Max key count that can be stored in the back end Vault instance; currently arbitrarly set |
MAX_KEY_PER_REQUEST | int | 100 | Max number of keys per key request; currently arbitrarily set |
MAX_KEY_SIZE | int | 65536  # Bits | Max size in bits of one key; currently arbitrarily set |
MAX_SAE_ID_COUNT | int | 0 | Max number of additional SAEs to send keyig material to; NOTE: no key relay is currently built into guardian |
MIN_KEY_SIZE | int | 8  # Bits | Min key size in bits; this is specifically set with Base64 and bit/byte storage in mind |
SAE_ID_MAX_LENGTH | int | 32  # Number of characters | Max length of SAE ID |
SAE_ID_MIN_LENGTH | int | 3  # Number of characters | Min length of SAE ID |
STATUS_MIN_LENGTH | int | 8  # Number of characters | Currently limited to the sizes of 'consumed' and 'available' strings used in KeyIDLedgers |
STATUS_MAX_LENGTH | int | 9  # Number of characters | Currenlty limited to the sizes of 'consumed' and 'available' strings used in KeyIDLedgers |
VALID_HOSTNAME_REGEX | str | r"^(([a-zA-Z0-9]\|[a-zA-Z0-9]..." | A regular expression to limit a string to a hostname |
VALID_IP_ADDRESS_REGEX | str | r"^(([0-9]\|[1-9][0-9]..." | A regular expression to limit a string to an IP address |
VALID_SAE_REGEX | str | f"{VALID_HOSTNAME_REGEX}\|{VALID_IP_ADDRESS_REGEX}" | Full regular expression limitation used for SAE IDs |
VALID_KME_REGEX | str | f"{VALID_HOSTNAME_REGEX}\|{VALID_IP_ADDRESS_REGEX}" | Full regular expression limitation used for KME IDs |
VALID_STATUS_REGEX | str | r"^consumed$\|^available$" | Full regular expression limitation for KeyIDLedger statuses in the Vault back end |
MAX_NUM_RESERVE_ATTEMPTS | int | 50 | Max number of rconsecutive Vault back end epoch file reservation attempts before erroring with a 503/504 HTTP status code |
RESERVE_SLEEP_TIME | float | 0.05  # seconds | Time to wait in seconds between reservation attempts if a Vault back end epoch file is not currently available |
CLIENT_NAME | str | "rest" | Name of the Docker service |
VAULT_CLIENT_CERT_FILEPATH | str | f"{GLOBAL.CERT_DIRPATH}/{GLOBAL.LOCAL_KME_ID}/{CLIENT_NAME}/{CLIENT_NAME}{GLOBAL.CA_CHAIN_SUFFIX}" | In-container file path to the rest certificate chain file to use when connecting to the local Vault instance; must match docker-compose yaml file volume locations |
VAULT_CLIENT_KEY_FILEPATH | str | f"{GLOBAL.CERT_DIRPATH}/{GLOBAL.LOCAL_KME_ID}/{CLIENT_NAME}/{CLIENT_NAME}{GLOBAL.KEY_SUFFIX}" | In-container file path to the rest private key file to use when connecting to the local Vault instance; must match docker-compose yaml file volume locations |
VAULT_SERVER_CERT_FILEPATH | str | f"{GLOBAL.CERT_DIRPATH}/{GLOBAL.LOCAL_KME_ID}/{GLOBAL.VAULT_NAME}/{GLOBAL.VAULT_NAME}{GLOBAL.CA_CHAIN_SUFFIX}" | In-container file path to the Vault back end server certificate chain file to use in server vertification; must match docker-compose file volume locations |
REMOTE_KME_CERT_FILEPATH | str | f"{GLOBAL.CERT_DIRPATH}/{GLOBAL.REMOTE_KME_ID}/{CLIENT_NAME}/{CLIENT_NAME}{GLOBAL.CA_CHAIN_SUFFIX}" | In-container file path to the remote KME certificate chain file to use in client vertification; must match docker-compose file volume locations |
VAULT_TLS_AUTH_MOUNT_POINT | str | "cert" | Vault back end instance certificate authentication mount point |
REMOTE_KME_URL | str | f"https://{GLOBAL.REMOTE_KME_ID}{API_V1_STR}/ledger/{GLOBAL.LOCAL_KME_ID}/key_ids" | URL to the remote KME host |
REMOTE_KME_RESPONSE_TIMEOUT | float | 10.0  # seconds | Time in seconds to wait for remote KME host response before timeout occurs |
VAULT_MAX_CONN_ATTEMPTS | int | 10 | Max number of Vault back end connection attempts before failing |
BACKOFF_FACTOR | float | 1.0 | Back off factor used for connection attempts |
BACKOFF_MAX | float | 8.0  # seconds | Max backoff time when attempting connection in seconds |
