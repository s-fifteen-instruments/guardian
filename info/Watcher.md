# Watcher Client Configuration

Watcher configuration options passed to the `watcher` Docker service found in the [watcher_config.py](../common/watcher_config.py) file.

Most of the variables will not need updating but do pay attention to `CLIENT_ALT_NAMES`.

| Variable | Type | Set Value | Description |
| --- | --- | --- | --- |
| WATCHER_LOG_LEVEL | str | os.environ.get("WATCHER_LOG_LEVEL", str(logging.info)) | Watcher client log-level pulled from the environment; set by the log.env file |
| DELETE_EPOCH_FILES | bool | True | Toggle to delete qcrypto final epoch files upon ingestion into Vault; note if False then it is possible reingest keys causing synch issues |
| CLIENT_NAME | str | "watcher" | Docker service name |
| CLIENT_CERT_FILEPATH | str | f"{GLOBAL.CERT_DIRPATH}/{CLIENT_NAME}/{CLIENT_NAME}{GLOBAL.CA_CHAIN_SUFFIX}" | In-container file path for Watcher client certificate chain file to communicate with the local Vault instance; must match docker-compose yaml file volume locations |
| CLIENT_KEY_FILEPATH | str | f"{GLOBAL.CERT_DIRPATH}/{CLIENT_NAME}/{CLIENT_NAME}{GLOBAL.KEY_SUFFIX}" | In-container file path for Watcher client private key file to communicate with the local Vault instance; must match docker-compose yaml file volume locations |
| NOTIFY_MAX_NUM_ATTEMPTS | int | 100 | Number of attempts to look for a notification FIFO pipe before stopping; in normal operations, this should appear quickly due to notifier service |
| NOTIFY_SLEEP_TIME | float | 0.5  # seconds | Once notify FIFO pipe exists, this is the amount of time to sleep in between checking the FIFO pipe for new data |
| NOTIFY_SLEEP_TIME_DELTA | float | 30.0  # seconds | If notification FIFO pipe is open and we're waiting for data; this is the amount of time notification messages on how long it has been since data has arrived |
