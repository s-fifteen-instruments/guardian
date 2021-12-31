Unsealer Client Configuration
=============================

Unsealer configuration options passed to the ``unsealer`` Docker service
found in the `unsealer_config.py <../common/unsealer_config.py>`__ file.

+-----------------+-----------------+-----------------+-----------------+
| Variable        | Type            | Set Value       | Description     |
+=================+=================+=================+=================+
| UNS\            | str             | os.env\         | Unsealer client |
| EALER_LOG_LEVEL |                 | iron.get(“UNSEA\| log-level       |
|                 |                 | LER_LOG_LEVEL”,\| pulled from the |
|                 |                 | str\            | environment;    |
|                 |                 | (logging.info)) | set by the      |
|                 |                 |                 | log.env file    |
+-----------------+-----------------+-----------------+-----------------+
| CLIEN\          | str             | f“{GLOBAL.CE\   | In-container    |
| T_CERT_FILEPATH |                 | RT_DIRPATH}/{G\ | file path for   |
|                 |                 | LOBAL.VAULT_IN\ | Unsealer client |
|                 |                 | IT_NAME}/{GLO\  | certificate     |
|                 |                 | BAL.VAULT_IN\   | chain file to   |
|                 |                 | IT_NAME}{GLOB\  | communicate     |
|                 |                 | AL.CA_CHAIN_SU\ | with the local  |
|                 |                 | FFIX}”          | Vault instance; |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| CLIE\           | str             | f“{             | In-container    |
| NT_KEY_FILEPATH |                 | GLOBAL.CERT_DIR | file path for   |
|                 |                 | PATH}/{GLOBAL.V | Unsealer client |
|                 |                 | AULT_INIT_NAME} | private key     |
|                 |                 | /{GLOBAL.VAUL\  | file to         |
|                 |                 | T_INIT_NAME}{GL\| communicate     |
|                 |                 | OBAL.KEY_SUF\   | with the local  |
|                 |                 | FIX}”           | Vault instance; |
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
