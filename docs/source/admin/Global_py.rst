Global Configuration
====================

.. _`Global_py`:

Global configuration options for any Docker service to use may be found
in the `global_config.py <https://github.com/s-fifteen-instruments/guardian/blob/main/common/global_config.py>`__ file.

These configuration variables are accessible in all Python-based
services and will take the form ``settings.GLOBAL.<VARIABLE_NAME>``
where ``<VARIABLE_NAME>`` is substituted with one below.

Most of these variables will not need updating in any typical scenarios.

+-----------------+-----------------+-----------------+-----------------+
| Variable        | Type            | Set Value       | Description     |
+=================+=================+=================+=================+
| LOCAL_KME_ID    | str             | os.environ.get( | Local KME host  |
|                 |                 | “LOCAL_KME_ID”, | ID; set by      |
|                 |                 | “kme1”)         | top-level       |
|                 |                 |                 | Makefile        |
+-----------------+-----------------+-----------------+-----------------+
| REMOTE_KME_ID   | str             | o\              | Remote KME host |
|                 |                 | s.environ.get(“\| ID; set by      |
|                 |                 | REMOTE_KME_ID”, | top-level       |
|                 |                 | “kme2”)         | Makefile        |
+-----------------+-----------------+-----------------+-----------------+
| LOCAL_SAE_ID    | str             | os.environ.get( | Local SAE ID;   |
|                 |                 | “LOCAL_SAE_ID”, | set by          |
|                 |                 | “sae1”)         | top-level       |
|                 |                 |                 | Makefile        |
+-----------------+-----------------+-----------------+-----------------+
| REMOTE_SAE_ID   | str             | o\              | Remote SAE ID;  |
|                 |                 | s.environ.get(“ | set by          |
|                 |                 | REMOTE_SAE_ID”, | top-level       |
|                 |                 | “sae2”)         | Makefile        |
+-----------------+-----------------+-----------------+-----------------+
| SHOW_SECRETS    | bool            | True            | Show            |
|                 |                 |                 | potentially     |
|                 |                 |                 | senstive        |
|                 |                 |                 | information     |
|                 |                 |                 | (e.g. keying    |
|                 |                 |                 | material) in    |
|                 |                 |                 | server logs     |
|                 |                 |                 | when log-level  |
|                 |                 |                 | is at least     |
|                 |                 |                 | Debug           |
+-----------------+-----------------+-----------------+-----------------+
| VAULT_NAME      | str             | “vault”         | Local Vault     |
|                 |                 |                 | instance Docker |
|                 |                 |                 | service name    |
+-----------------+-----------------+-----------------+-----------------+
| V\              | str             | f“https\        | URL to reach    |
| AULT_SERVER_URL |                 | ://{VA\         | local Vault     |
|                 |                 | ULT_NAME}:8200” | instance        |
+-----------------+-----------------+-----------------+-----------------+
| CA_CHAIN_SUFFIX | str             | “.ca-\          | Certificate     |
|                 |                 | chain.cert.pem” | file suffixes   |
|                 |                 |                 | (all are        |
|                 |                 |                 | complete cert   |
|                 |                 |                 | chain files)    |
+-----------------+-----------------+-----------------+-----------------+
| KEY_SUFFIX      | str             | “.key.pem”      | Private key     |
|                 |                 |                 | file suffix     |
+-----------------+-----------------+-----------------+-----------------+
| CSR_SUFFIX      | str             | “.csr.pem”      | Certificate     |
|                 |                 |                 | Signing Request |
|                 |                 |                 | file suffix     |
+-----------------+-----------------+-----------------+-----------------+
| DIGEST_KEY      | bytes           | b“TODO: Change  | HMAC SHA256     |
|                 |                 | me; no hard     | digest key used |
|                 |                 | code”           | in comparing    |
|                 |                 |                 | key HMACs       |
|                 |                 |                 | across KME      |
|                 |                 |                 | hosts; Should   |
|                 |                 |                 | match on both   |
|                 |                 |                 | KME hosts       |
+-----------------+-----------------+-----------------+-----------------+
| EPOC\           | str             | “/epoch_files”  | In-container    |
| H_FILES_DIRPATH |                 |                 | directory path  |
|                 |                 |                 | where qcrypto   |
|                 |                 |                 | files are       |
|                 |                 |                 | stored; must    |
|                 |                 |                 | match           |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| NOTIF\          | str             | f“{EPO\         | In-container    |
| Y_PIPE_FILEPATH |                 | CH_FILES_DIRPAT | FIFO path used  |
|                 |                 | H}/notify.pipe” | in notifier and |
|                 |                 |                 | watcher         |
|                 |                 |                 | services for    |
|                 |                 |                 | communication   |
|                 |                 |                 | on when new     |
|                 |                 |                 | keying          |
|                 |                 |                 | information is  |
|                 |                 |                 | available; must |
|                 |                 |                 | match docker    |
|                 |                 |                 | compose yaml    |
|                 |                 |                 | file volume     |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| DIGES\          | str             | “/digest_files” | In-container    |
| T_FILES_DIRPATH |                 |                 | directory path  |
|                 |                 |                 | where HMAC      |
|                 |                 |                 | digest files of |
|                 |                 |                 | keying material |
|                 |                 |                 | are stored;     |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| CERT_DIRPATH    | str             | “/certifica\    | In-container    |
|                 |                 | tes/production” | directory path  |
|                 |                 |                 | where           |
|                 |                 |                 | production TLS  |
|                 |                 |                 | certificates    |
|                 |                 |                 | are stored;     |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| ADMIN_DIRPATH   | str             | f“{CERT\_\      | In-container    |
|                 |                 | DIRPATH}/admin” | directory path  |
|                 |                 |                 | where           |
|                 |                 |                 | admin-readable  |
|                 |                 |                 | TLS             |
|                 |                 |                 | certificates    |
|                 |                 |                 | are stored; for |
|                 |                 |                 | convenience,    |
|                 |                 |                 | not production  |
|                 |                 |                 | per se; must    |
|                 |                 |                 | match           |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| P\              | str             | “/\             | In-container    |
| OLICIES_DIRPATH |                 | vault/policies” | directory path  |
|                 |                 |                 | where           |
|                 |                 |                 | pre-generated   |
|                 |                 |                 | and template    |
|                 |                 |                 | policies for    |
|                 |                 |                 | Vault roles are |
|                 |                 |                 | stored          |
|                 |                 |                 | (read-only);    |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| LOG_DIRPATH     | str             | “/vault/logs”   | In-container    |
|                 |                 |                 | directory path  |
|                 |                 |                 | where local     |
|                 |                 |                 | Vault instance  |
|                 |                 |                 | logs (if        |
|                 |                 |                 | configured to   |
|                 |                 |                 | write to file)  |
|                 |                 |                 | are stored;     |
|                 |                 |                 | must match      |
|                 |                 |                 | docker-compose  |
|                 |                 |                 | yaml file       |
|                 |                 |                 | volume          |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| VAULT_S\        | str             | f“{ADMIN\_\     | In-container    |
| ECRETS_FILEPATH |                 | DIRPATH}/{VAULT\| file path to    |
|                 |                 | _NAME}/SECRETS” | write out local |
|                 |                 |                 | Vault instance  |
|                 |                 |                 | unseal keys and |
|                 |                 |                 | root token      |
|                 |                 |                 | (sensitive      |
|                 |                 |                 | material); must |
|                 |                 |                 | match docker    |
|                 |                 |                 | compose yaml    |
|                 |                 |                 | file volume     |
|                 |                 |                 | locations       |
+-----------------+-----------------+-----------------+-----------------+
| VAULT_INIT_NAME | str             | “vault_init”    | Local Vault     |
|                 |                 |                 | initialization  |
|                 |                 |                 | client Docker   |
|                 |                 |                 | service name    |
+-----------------+-----------------+-----------------+-----------------+
| SERVE\          | str             | f“{CE\          | In-container    |
| R_CERT_FILEPATH |                 | RT_DIRPATH}/{VA\| local Vault     |
|                 |                 | ULT_INIT_NAME}/\| server          |
|                 |                 | {VAULT_NAME}{CA\| certificate     |
|                 |                 | _CHAIN_SUFFIX}” | chain file path |
|                 |                 |                 | for Vault       |
|                 |                 |                 | initialization  |
|                 |                 |                 | client to use   |
|                 |                 |                 | in mutual TLS   |
|                 |                 |                 | verification of |
|                 |                 |                 | Vault server    |
|                 |                 |                 | identity        |
+-----------------+-----------------+-----------------+-----------------+
| PKI_INT_C\      | str             | f“{CERT_DI\     | Local Vault     |
| SR_PEM_FILEPATH |                 | RPATH}/{VAULT_I\| instance PKI    |
|                 |                 | NIT_NAME}/pki_i\| secrets engine  |
|                 |                 | nt{CSR_SUFFIX}” | certificate     |
|                 |                 |                 | signing request |
|                 |                 |                 | file path to be |
|                 |                 |                 | signed by       |
|                 |                 |                 | CERTAUTH        |
|                 |                 |                 | service         |
+-----------------+-----------------+-----------------+-----------------+
| PKI_INT_CE\     | str             | f“{CERT_DIRPATH\| Local Vault     |
| RT_PEM_FILEPATH |                 | }/{VAULT_INIT_N\| instance PKI    |
|                 |                 | AME}/pki_int{CA\| secrets engine  |
|                 |                 | _CHAIN_SUFFIX}” | certificate     |
|                 |                 |                 | chain file      |
|                 |                 |                 | produced by     |
|                 |                 |                 | CERTAUTH        |
+-----------------+-----------------+-----------------+-----------------+
| VAULT_MA\       | int             | 10              | Number of       |
| X_CONN_ATTEMPTS |                 |                 | attempts to try |
|                 |                 |                 | and connect to  |
|                 |                 |                 | local Vault     |
|                 |                 |                 | instance before |
|                 |                 |                 | failure         |
+-----------------+-----------------+-----------------+-----------------+
| BACKOFF_FACTOR  | float           | 1.0             | Backoff         |
|                 |                 |                 | multiplication  |
|                 |                 |                 | factor used     |
|                 |                 |                 | when slowing    |
|                 |                 |                 | down connection |
|                 |                 |                 | attempts        |
+-----------------+-----------------+-----------------+-----------------+
| BACKOFF_MAX\    | float           | 64.0 # seconds  | Maximum backoff |
|                 |                 |                 | time in         |
|                 |                 |                 | connection      |
|                 |                 |                 | attempts        |
+-----------------+-----------------+-----------------+-----------------+
| VA\             | str             | “QKEYS”         | Vault Key Value |
| ULT_KV_ENDPOINT |                 |                 | secrets engine  |
|                 |                 |                 | mount point     |
|                 |                 |                 | name            |
+-----------------+-----------------+-----------------+-----------------+
| VAULT_QKDE_ID\  | str             | “QKDE0001”      | Vault unique    |
|                 |                 |                 | QKD Entity ID   |
+-----------------+-----------------+-----------------+-----------------+
| VA\             | str             | “ALICEBOB”      | Vault unique    |
| ULT_QCHANNEL_ID |                 |                 | quantum channel |
|                 |                 |                 | ID              |
+-----------------+-----------------+-----------------+-----------------+
| VAULT_LEDGER_ID | str             | “LEDGER”        | Vault           |
|                 |                 |                 | KeyIDLedger     |
|                 |                 |                 | directory to    |
|                 |                 |                 | store key       |
|                 |                 |                 | metadata        |
|                 |                 |                 | between KME     |
|                 |                 |                 | hosts           |
+-----------------+-----------------+-----------------+-----------------+
