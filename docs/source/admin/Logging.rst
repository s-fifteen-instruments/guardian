Logging Configuration
=====================

Log levels for different Docker services can be controlled via the
`${TOP_DIR}/common/log.env <../common/log.env>`__ file. During normal
operations, an ``Info`` or ``Warning`` may be appropriate. ``Debug`` and
``Trace`` (in some services) are available to help diagnose any issues
that may arise.

NOTE: The output of potentially sensitive information (e.g. keying
material) in service logs can be controlled via ``SHOW_SECRETS`` boolean
in the
`${TOP_DIR}/common/global_config.py <../common/global_config.py>`__
file.

An example ``Info`` level log.env file is displayed below:

.. code:: bash

   # NOTE: No variable substitution or expansion
   # Vault log level options: Trace, Debug, Error, Warn, Info
   VAULT_LOG_LEVEL=Info
   # Traefik log level options: DEBUG, PANIC, FATAL, ERROR, WARN, INFO
   # Appears to be ignored. Set in static traefik.yml file instead.
   #TRAEFIK_LOG_LEVEL=
   # HTTPX log level options: (unset), debug, trace
   HTTPX_LOG_LEVEL=
   # QKD log level options: (unset), debug
   QKD_LOG_LEVEL=
   # Python log level options:
   # Level=Numeric_value
   # CRITICAL=50
   # ERROR=40
   # WARNING=30
   # INFO=20
   # DEBUG=10
   # NOTSET=0
   #####
   # Python-based services
   VAULT_INIT_LOG_LEVEL=20
   NOTIFY_LOG_LEVEL=20
   WATCHER_LOG_LEVEL=20
   UNSEALER_LOG_LEVEL=20
   REST_LOG_LEVEL=20

NOTE: The log-level for Traefik can be controlled from its static
configuration file: `KME Host
1 <../volumes/kme1/traefik/configuration/traefik.yml>`__ and `KME Host
2 <../volumes/kme2/traefik/configuration/traefik.yml>`__
