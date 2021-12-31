Unsealer Client Configuration
=============================

Unsealer configuration options passed to the ``unsealer`` Docker service
found in the `unsealer_config.py <../common/unsealer_config.py>`__ file.

+-----------------+-----------------+-----------------+-----------------+
| Variable        | Type            | Set Value       | Description     |
+=================+=================+=================+=================+
| UNS             | str             | os.env          | Unsealer client |
| EALER_LOG_LEVEL |                 | iron.get(“UNSEA | log-level       |
|                 |                 | LER_LOG_LEVEL”, | pulled from the |
|                 |                 | str             | environment;    |
|                 |                 | (logging.info)) | set by the      |
|                 |                 |                 | log.env file    |
+-----------------+-----------------+-----------------+-----------------+
| CLIEN           | str             | f“{GLOBA        | In-container    |
| T_CERT_FILEPATH |                 | L.CERT_DIRPATH} | file path for   |
|                 |                 | /{GLOBAL.VAULT_ | Unsealer client |
|                 |                 | INIT_NAME}/{GLO | certificate     |
|                 |                 | BAL.VAULT_INIT_ | chain file to   |
|                 |                 | NAME}{GLOBAL.CA | communicate     |
|                 |                 | _CHAIN_SUFFIX}” | with the local  |
|                 |                 |                 | Vault instance; |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| CLIE            | str             | f“{             | In-container    |
| NT_KEY_FILEPATH |                 | GLOBAL.CERT_DIR | file path for   |
|                 |                 | PATH}/{GLOBAL.V | Unsealer client |
|                 |                 | AULT_INIT_NAME} | private key     |
|                 |                 | /{GLOBAL.VAULT_ | file to         |
|                 |                 | INIT_NAME}{GLOB | communicate     |
|                 |                 | AL.KEY_SUFFIX}” | with the local  |
|                 |                 |                 | Vault instance; |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| TIME_WINDOW     | float           | 30.0 # seconds  | How far back    |
|                 |                 |                 | from the        |
|                 |                 |                 | current time to |
|                 |                 |                 | look for Docker |
|                 |                 |                 | events on the   |
|                 |                 |                 | docker socket   |
|                 |                 |                 | that include    |
|                 |                 |                 | the label       |
|                 |                 |                 | ‘               |
|                 |                 |                 | unsealer=watch’ |
|                 |                 |                 | form the local  |
|                 |                 |                 | Vault instance  |
+-----------------+-----------------+-----------------+-----------------+
