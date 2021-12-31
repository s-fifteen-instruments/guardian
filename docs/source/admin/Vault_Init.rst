Vault Initialization Client Configuration
=========================================

Vault initialization configuration options passed to the ``vault_init``
Docker service found in the
`vault_init_config.py <../common/vault_init_config.py>`__ file.

Most of the variables will not need updating but do pay attention to
``CLIENT_ALT_NAMES``.

+-----------------+-----------------+-----------------+-----------------+
| Variable        | Type            | Set Value       | Description     |
+=================+=================+=================+=================+
| VAULT\          | str             | os.envir\       | Vault           |
| _INIT_LOG_LEVEL |                 | on.get(“VAULT_I\| initialization  |
|                 |                 | NIT_LOG_LEVEL”,\| client          |
|                 |                 | str\            | log-level       |
|                 |                 | (logging.info)) | pulled from the |
|                 |                 |                 | environment;    |
|                 |                 |                 | set by the      |
|                 |                 |                 | log.env file    |
+-----------------+-----------------+-----------------+-----------------+
| CLIEN\          | str             | f“{GLOBAL.CERT\ | In-container    |
| T_CERT_FILEPATH |                 | _DIRPATH}/{GLOB\| file path for   |
|                 |                 | AL.VAULT_INI\   | Vault           |
|                 |                 | T_NAME}/{GLOBA\ | initialization  |
|                 |                 | L.VAULT_INIT\_\ | client          |
|                 |                 | NAME}{GLOBAL.CA\| certificate     |
|                 |                 | _CHAIN_SUFFIX}” | chain to        |
|                 |                 |                 | communicate     |
|                 |                 |                 | with the local  |
|                 |                 |                 | Vault instance; |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| CLIE\           | str             | f“{\            | In-container    |
| NT_KEY_FILEPATH |                 | GLOBAL.CERT_DIR\| file path for   |
|                 |                 | PATH}/{GLOBAL.V\| Vault           |
|                 |                 | AULT_INIT_NAME}\| initialization  |
|                 |                 | /{GLOBAL.VAULT\ | client private  |
|                 |                 | _INIT_NAME}{GLO\| key to          |
|                 |                 | BAL.KEY_SUFFIX}”| communicate     |
|                 |                 |                 | with the local  |
|                 |                 |                 | Vault instance; |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| SECRET_SHARES   | int             | 5               | Number of       |
|                 |                 |                 | Shamir secret   |
|                 |                 |                 | shares          |
|                 |                 |                 | generated when  |
|                 |                 |                 | first creating  |
|                 |                 |                 | the local Vault |
|                 |                 |                 | instance        |
+-----------------+-----------------+-----------------+-----------------+
| S\              | int             | 3               | Number of       |
| ECRET_THRESHOLD |                 |                 | Shamir secret   |
|                 |                 |                 | shares needed   |
|                 |                 |                 | to first        |
|                 |                 |                 | initialize the  |
|                 |                 |                 | local Vault     |
|                 |                 |                 | instance        |
+-----------------+-----------------+-----------------+-----------------+
| C\              | str             | f“{GLOBAL.L\    | The Subject     |
| LIENT_ALT_NAMES |                 | OCAL_SAE_ID},{G\| Alternative     |
|                 |                 | LOBAL.LOCAL_KME\| Names (SANs)    |
|                 |                 | _ID},traefik.{G\| that are used   |
|                 |                 | LOBAL.LOCAL_KME\| for Vault       |
|                 |                 | _ID},localhost” | initialization  |
|                 |                 |                 | client          |
|                 |                 |                 | generated       |
|                 |                 |                 | certificates;   |
|                 |                 |                 | this includes   |
|                 |                 |                 | the rest and    |
|                 |                 |                 | watcher service |
|                 |                 |                 | certificate     |
|                 |                 |                 | pairs as well   |
|                 |                 |                 | as the local    |
|                 |                 |                 | Traefik         |
|                 |                 |                 | Dashboard       |
+-----------------+-----------------+-----------------+-----------------+
