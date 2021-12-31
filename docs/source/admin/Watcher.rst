Watcher Client Configuration
============================

Watcher configuration options passed to the ``watcher`` Docker service
found in the `watcher_config.py <../common/watcher_config.py>`__ file.

Most of the variables will not need updating but do pay attention to
``CLIENT_ALT_NAMES``.

+-----------------+-----------------+-----------------+-----------------+
| Variable        | Type            | Set Value       | Description     |
+=================+=================+=================+=================+
| WA\             | str             | os.en\          | Watcher client  |
| TCHER_LOG_LEVEL |                 | viron.get(“WATC\| log-level       |
|                 |                 | HER_LOG_LEVEL”,\| pulled from the |
|                 |                 | str\            | environment;    |
|                 |                 | (logging.info)) | set by the      |
|                 |                 |                 | log.env file    |
+-----------------+-----------------+-----------------+-----------------+
| DEL\            | bool            | True            | Toggle to       |
| ETE_EPOCH_FILES |                 |                 | delete qcrypto  |
|                 |                 |                 | final epoch     |
|                 |                 |                 | files upon      |
|                 |                 |                 | ingestion into  |
|                 |                 |                 | Vault; note if  |
|                 |                 |                 | False then it   |
|                 |                 |                 | is possible     |
|                 |                 |                 | reingest keys   |
|                 |                 |                 | causing synch   |
|                 |                 |                 | issues          |
+-----------------+-----------------+-----------------+-----------------+
| CLIENT_NAME     | str             | “watcher”       | Docker service  |
|                 |                 |                 | name            |
+-----------------+-----------------+-----------------+-----------------+
| CLIEN\          | str             | f\              | In-container    |
| T_CERT_FILEPATH |                 | “{GLOBAL.CERT_D\| file path for   |
|                 |                 | IRPATH}/{CLIENT\| Watcher client  |
|                 |                 | _NAME}/{CLIENT\ | certificate     |
|                 |                 | _NAME}{GLOBAL.C\| chain file to   |
|                 |                 | A_CHAIN_SUFFIX}”| communicate     |
|                 |                 |                 | with the local  |
|                 |                 |                 | Vault instance; |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| CLIE\           | str             | f“{GLOBAL.C\    | In-container    |
| NT_KEY_FILEPATH |                 | ERT_DIRPATH}/{C\| file path for   |
|                 |                 | LIENT_NAME}/{CL\| Watcher client  |
|                 |                 | IENT_NAME}{GLOB\| private key     |
|                 |                 | AL.KEY_SUFFIX}” | file to         |
|                 |                 |                 | communicate     |
|                 |                 |                 | with the local  |
|                 |                 |                 | Vault instance; |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| NOTIFY_M\       | int             | 100             | Number of       |
| AX_NUM_ATTEMPTS |                 |                 | attempts to     |
|                 |                 |                 | look for a      |
|                 |                 |                 | notification    |
|                 |                 |                 | FIFO pipe       |
|                 |                 |                 | before          |
|                 |                 |                 | stopping; in    |
|                 |                 |                 | normal          |
|                 |                 |                 | operations,     |
|                 |                 |                 | this should     |
|                 |                 |                 | appear quickly  |
|                 |                 |                 | due to notifier |
|                 |                 |                 | service         |
+-----------------+-----------------+-----------------+-----------------+
| NO\             | float           | 0.5 # seconds   | Once notify     |
| TIFY_SLEEP_TIME |                 |                 | FIFO pipe       |
|                 |                 |                 | exists, this is |
|                 |                 |                 | the amount of   |
|                 |                 |                 | time to sleep   |
|                 |                 |                 | in between      |
|                 |                 |                 | checking the    |
|                 |                 |                 | FIFO pipe for   |
|                 |                 |                 | new data        |
+-----------------+-----------------+-----------------+-----------------+
| NOTIFY_S\       | float           | 30.0 # seconds  | If notification |
| LEEP_TIME_DELTA |                 |                 | FIFO pipe is    |
|                 |                 |                 | open and we’re  |
|                 |                 |                 | waiting for     |
|                 |                 |                 | data; this is   |
|                 |                 |                 | the amount of   |
|                 |                 |                 | time            |
|                 |                 |                 | notification    |
|                 |                 |                 | messages on how |
|                 |                 |                 | long it has     |
|                 |                 |                 | been since data |
|                 |                 |                 | has arrived     |
+-----------------+-----------------+-----------------+-----------------+
