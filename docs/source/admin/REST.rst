REST API Configuration
======================

REST API configuration options passed to the ``rest`` Docker service
found in the `rest_config.py <../common/rest_config.py>`__\file.

+-----------------+-----------------+-----------------+-----------------+
| Variable        | Type            | Set Value       | Description     |
+=================+=================+=================+=================+
| REST_LOG_LEVEL  | str             | os\             | REST API        |
|                 |                 | .environ.get(“R\| log-level       |
|                 |                 | EST_LOG_LEVEL”,\| pulled from the |
|                 |                 | str\            | environment;    |
|                 |                 | (logging.info)) | set by the      |
|                 |                 |                 | log.env file    |
+-----------------+-----------------+-----------------+-----------------+
| API_V1_STR      | str             | “/api/v1”       | REST API        |
|                 |                 |                 | version 1 URL   |
|                 |                 |                 | path            |
+-----------------+-----------------+-----------------+-----------------+
| DIGEST\_\       | bool            | True            | Toggle wether   |
| COMPARE_TO_FILE |                 |                 | to compare      |
|                 |                 |                 | keying material |
|                 |                 |                 | HMAC digest to  |
|                 |                 |                 | the one         |
|                 |                 |                 | previously      |
|                 |                 |                 | written out to  |
|                 |                 |                 | file by either  |
|                 |                 |                 | watcher or      |
|                 |                 |                 | previous        |
|                 |                 |                 | request         |
+-----------------+-----------------+-----------------+-----------------+
| DIGEST_COMPARE  | bool            | True            | Toggle wether   |
|                 |                 |                 | to compare      |
|                 |                 |                 | keying material |
|                 |                 |                 | to HMAC digest  |
|                 |                 |                 | either written  |
|                 |                 |                 | to file or also |
|                 |                 |                 | within the      |
|                 |                 |                 | Vault epoch     |
|                 |                 |                 | file entry      |
+-----------------+-----------------+-----------------+-----------------+
| KE\             | int             | 128 # Number of | Max length of   |
| Y_ID_MAX_LENGTH |                 | characters      | key ID –        |
|                 |                 |                 | usually         |
|                 |                 |                 | associated with |
|                 |                 |                 | a UUID          |
+-----------------+-----------------+-----------------+-----------------+
| KE\             | int             | 16 # Number of  | Min length of a |
| Y_ID_MIN_LENGTH |                 | characters      | key ID –        |
|                 |                 |                 | usually         |
|                 |                 |                 | associated with |
|                 |                 |                 | a UUID          |
+-----------------+-----------------+-----------------+-----------------+
| KEY_SIZE        | int             | 32 # Bits       | Default key     |
|                 |                 |                 | size in bits to |
|                 |                 |                 | serve if a key  |
|                 |                 |                 | requested       |
+-----------------+-----------------+-----------------+-----------------+
| KM\             | int             | 32 # Number of  | Max length of   |
| E_ID_MAX_LENGTH |                 | characters      | KME ID string   |
+-----------------+-----------------+-----------------+-----------------+
| KM\             | int             | 3 # Number of   | Min length of   |
| E_ID_MIN_LENGTH |                 | characters      | KME ID string   |
+-----------------+-----------------+-----------------+-----------------+
| MAX_EX_M\       | int             | 2               | Max number of   |
| ANADATORY_COUNT |                 |                 | ‘exten          |
|                 |                 |                 | sion_mandatory’ |
|                 |                 |                 | entries; see    |
|                 |                 |                 | ETSI document   |
+-----------------+-----------------+-----------------+-----------------+
| MAX_EX\         | int             | 2               | Max number of   |
| _OPTIONAL_COUNT |                 |                 | ‘exte           |
|                 |                 |                 | nsion_optional’ |
|                 |                 |                 | entries; see    |
|                 |                 |                 | ETSI document   |
+-----------------+-----------------+-----------------+-----------------+
| MAX_KEY_COUNT   | int             | 1048576         | Max key count   |
|                 |                 |                 | that can be     |
|                 |                 |                 | stored in the   |
|                 |                 |                 | back end Vault  |
|                 |                 |                 | instance;       |
|                 |                 |                 | currently       |
|                 |                 |                 | arbitrarly set  |
+-----------------+-----------------+-----------------+-----------------+
| MAX\_\          | int             | 100             | Max number of   |
| KEY_PER_REQUEST |                 |                 | keys per key    |
|                 |                 |                 | request;        |
|                 |                 |                 | currently       |
|                 |                 |                 | arbitrarily set |
+-----------------+-----------------+-----------------+-----------------+
| MAX_KEY_SIZE    | int             | 65536 # Bits    | Max size in     |
|                 |                 |                 | bits of one     |
|                 |                 |                 | key; currently  |
|                 |                 |                 | arbitrarily set |
+-----------------+-----------------+-----------------+-----------------+
| M\              | int             | 0               | Max number of   |
| AX_SAE_ID_COUNT |                 |                 | additional SAEs |
|                 |                 |                 | to send keyig   |
|                 |                 |                 | material to;    |
|                 |                 |                 | NOTE: no key    |
|                 |                 |                 | relay is        |
|                 |                 |                 | currently built |
|                 |                 |                 | into guardian   |
+-----------------+-----------------+-----------------+-----------------+
| MIN_KEY_SIZE    | int             | 8 # Bits        | Min key size in |
|                 |                 |                 | bits; this is   |
|                 |                 |                 | specifically    |
|                 |                 |                 | set with Base64 |
|                 |                 |                 | and bit/byte    |
|                 |                 |                 | storage in mind |
+-----------------+-----------------+-----------------+-----------------+
| SA\             | int             | 32 # Number of  | Max length of   |
| E_ID_MAX_LENGTH |                 | characters      | SAE ID          |
+-----------------+-----------------+-----------------+-----------------+
| SA\             | int             | 3 # Number of   | Min length of   |
| E_ID_MIN_LENGTH |                 | characters      | SAE ID          |
+-----------------+-----------------+-----------------+-----------------+
| ST\             | int             | 8 # Number of   | Currently       |
| ATUS_MIN_LENGTH |                 | characters      | limited to the  |
|                 |                 |                 | sizes of        |
|                 |                 |                 | ‘consumed’ and  |
|                 |                 |                 | ‘available’     |
|                 |                 |                 | strings used in |
|                 |                 |                 | KeyIDLedgers    |
+-----------------+-----------------+-----------------+-----------------+
| ST\             | int             | 9 # Number of   | Currenlty       |
| ATUS_MAX_LENGTH |                 | characters      | limited to the  |
|                 |                 |                 | sizes of        |
|                 |                 |                 | ‘consumed’ and  |
|                 |                 |                 | ‘available’     |
|                 |                 |                 | strings used in |
|                 |                 |                 | KeyIDLedgers    |
+-----------------+-----------------+-----------------+-----------------+
| VALID\          | str             | r“^(([a-zA-Z0-9\| A regular       |
| _HOSTNAME_REGEX |                 | ]|[a-zA-Z0-9]…” | expression to   |
|                 |                 |                 | limit a string  |
|                 |                 |                 | to a hostname   |
+-----------------+-----------------+-----------------+-----------------+
| VALID_I\        | str             | r“^(([0-\       | A regular       |
| P_ADDRESS_REGEX |                 | 9]|[1-9][0-9]…” | expression to   |
|                 |                 |                 | limit a string  |
|                 |                 |                 | to an IP        |
|                 |                 |                 | address         |
+-----------------+-----------------+-----------------+-----------------+
| VALID_SAE_REGEX | str             | f“{VALID_HOS\   | Full regular    |
|                 |                 | TNAME_REGEX}|{V\| expression      |
|                 |                 | ALID_IP\_\      | limitation used |
|                 |                 | ADDRESS_REGEX}” | for SAE IDs     |
+-----------------+-----------------+-----------------+-----------------+
| VALID_KME_REGEX | str             | f“{VALI\        | Full regular    |
|                 |                 | D_HOSTNAME_REGE\| expression      |
|                 |                 | X}|{VALID_IP\_\ | limitation used |
|                 |                 | ADDRESS_REGEX}” | for KME IDs     |
+-----------------+-----------------+-----------------+-----------------+
| VAL\            | str             | r“^c\           | Full regular    |
| ID_STATUS_REGEX |                 | onsumed\$\      | expression      |
|                 |                 | \|^available\$" | limitation for  |
|                 |                 |                 | KeyIDLedger     |
|                 |                 |                 | statuses in the |
|                 |                 |                 | Vault back end  |
+-----------------+-----------------+-----------------+-----------------+
| MAX_NUM_R\      | int             | 50              | Max number of   |
| ESERVE_ATTEMPTS |                 |                 | rconsecutive    |
|                 |                 |                 | Vault back end  |
|                 |                 |                 | epoch file      |
|                 |                 |                 | reservation     |
|                 |                 |                 | attempts before |
|                 |                 |                 | erroring with a |
|                 |                 |                 | 503/504 HTTP    |
|                 |                 |                 | status code     |
+-----------------+-----------------+-----------------+-----------------+
| RES\            | float           | 0.05 # seconds  | Time to wait in |
| ERVE_SLEEP_TIME |                 |                 | seconds between |
|                 |                 |                 | reservation     |
|                 |                 |                 | attempts if a   |
|                 |                 |                 | Vault back end  |
|                 |                 |                 | epoch file is   |
|                 |                 |                 | not currently   |
|                 |                 |                 | available       |
+-----------------+-----------------+-----------------+-----------------+
| CLIENT_NAME     | str             | “rest”          | Name of the     |
|                 |                 |                 | Docker service  |
+-----------------+-----------------+-----------------+-----------------+
| VAULT_CLIEN\    | str             | f“{GLOBAL.C\    | In-container    |
| T_CERT_FILEPATH |                 | ERT_DIRPATH}/{G\| file path to    |
|                 |                 | LOBAL.LOCAL\_KM\| the rest        |
|                 |                 | E_ID}/{CLIENT_N\| certificate     |
|                 |                 | AME}/{CLIENT\_\ | chain file to   |
|                 |                 | NAME}{GLOBAL.CA\| use when        |
|                 |                 | _CHAIN_SUFFIX}” | connecting to   |
|                 |                 |                 | the local Vault |
|                 |                 |                 | instance; must  |
|                 |                 |                 | match           |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| VAULT_CLIE\     | str             | f“{\            | In-container    |
| NT_KEY_FILEPATH |                 | GLOBAL.CERT_DIR\| file path to    |
|                 |                 | PATH}/{GLOBAL.L\| the rest        |
|                 |                 | OCAL_KME_ID}/{C\| private key     |
|                 |                 | LIENT_NAME}/{CL\| file to use     |
|                 |                 | IENT_NAME}{GLOB\| when connecting |
|                 |                 | AL.KEY_SUFFIX}” | to the local    |
|                 |                 |                 | Vault instance; |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| VAULT_SERVE\    | str             | f“{GL\          | In-container    |
| R_CERT_FILEPATH |                 | OBAL.CERT_DIRPA\| file path to    |
|                 |                 | TH}/{GLOBAL.LOC\| the Vault back  |
|                 |                 | AL_KME_ID}/{GLO\| end server      |
|                 |                 | BAL.VAULT_NAME}\| certificate     |
|                 |                 | /{GLOBAL.\      | chain file to   |
|                 |                 | VAULT\_\        | use in server   |
|                 |                 | NAME}{GLOBAL.CA\| vertification;  |
|                 |                 | _CHAIN_SUFFIX}” | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | file volume     |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| REMOTE_KM\      | str             | f“{GLOBAL\      | In-container    |
| E_CERT_FILEPATH |                 | .CERT_DIRPATH}{/| file path to    |
|                 |                 | GLOBAL.REMOTE\_\| the remote KME  |
|                 |                 | KME_ID}/{CLIENT\| certificate     |
|                 |                 | _NAME}\         | chain file to   |
|                 |                 | /{CLIENT\_\     | use in client   |
|                 |                 | NAME}{GLOBAL.CA\| vertification;  |
|                 |                 | _CHAIN_SUFFIX}” | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | file volume     |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| VAULT_TLS_A\    | str             | “cert”          | Vault back end  |
| UTH_MOUNT_POINT |                 |                 | instance        |
|                 |                 |                 | certificate     |
|                 |                 |                 | authentication  |
|                 |                 |                 | mount point     |
+-----------------+-----------------+-----------------+-----------------+
| REMOTE_KME_URL  | str             | f“https:/\      | URL to the      |
|                 |                 | /{GLOBAL.REMOTE\| remote KME host |
|                 |                 | _KME_ID}{API\_\ |                 |
|                 |                 | V1_STR}/ledger/\|                 |
|                 |                 | {GLOBAL.LOCAL_K\|                 |
|                 |                 | ME_ID}/key_ids” |                 |
+-----------------+-----------------+-----------------+-----------------+
| REMOTE_KME_R\   | float           | 10.0 # seconds  | Time in seconds |
| ESPONSE_TIMEOUT |                 |                 | to wait for     |
|                 |                 |                 | remote KME host |
|                 |                 |                 | response before |
|                 |                 |                 | timeout occurs  |
+-----------------+-----------------+-----------------+-----------------+
| VAULT_MA\       | int             | 10              | Max number of   |
| X_CONN_ATTEMPTS |                 |                 | Vault back end  |
|                 |                 |                 | connection      |
|                 |                 |                 | attempts before |
|                 |                 |                 | failing         |
+-----------------+-----------------+-----------------+-----------------+
| BACKOFF_FACTOR  | float           | 1.0             | Back off factor |
|                 |                 |                 | used for        |
|                 |                 |                 | connection      |
|                 |                 |                 | attempts        |
+-----------------+-----------------+-----------------+-----------------+
| BACKOFF_MAX     | float           | 8.0 # seconds   | Max backoff     |
|                 |                 |                 | time when       |
|                 |                 |                 | attempting      |
|                 |                 |                 | connection in   |
|                 |                 |                 | seconds         |
+-----------------+-----------------+-----------------+-----------------+
