.. _traefik:

Traefik Configuration
=====================



Static Configuration File
-------------------------

Traefik is configured using first a static configuration file that is
read on startup. This static configuration file can be found here: `KME
Host 1 <../volumes/kme1/traefik/configuration/traefik.yml>`__ and `KME
Host 2 <../volumes/kme2/traefik/configuration/traefik.yml>`__.

An example of the static configuration file is reproduced below:

::

   # Traefik static configuration file

   global:
     checkNewVersion: True
     sendAnonymousUsage: False

   api:
     dashboard: True

   log:
     level: DEBUG
     format: common
     # Uncomment to dump to log file instead of to stdout
     # where Docker picks it up.
     #filePath: /var/log/traefik/traefik.log

   accessLog:
     format: common
     filePath: /var/log/traefik/access.log

   entryPoints:
     web:
       address: :80
       http:
         redirections:
           entryPoint:
             to: websecure
             scheme: https
             permanent: True

     websecure:
       address: :443

   providers:
     docker:
       swarmMode: False
       exposedByDefault: False
       network: traefik-public
       watch: True

     file:
       directory: /etc/traefik/traefik.d/
       watch: True

Two entrypoints are defined on port 80 and port 443. Port 80 is setup as
an entrypoint called ``web`` and is redirected to entrypoint called
``websecure`` on port 443.

Two configuration providers are specified as ``docker`` and ``file``.

The ``docker`` provider watches for information coming through the local
docker socket in the form of container labels. Look in the
docker-compose.yml and docker-compose.init.yml files for docker services
that set Traefik configuration information via labels (e.g. the ``rest``
service).

The ``file`` provider is setup to watch the in-container directory
``/etc/traefik/traefik.d/`` which is a docker volume mount to `KME Host
1 traefik.d
directory <../volumes/kme1/traefik/configuration/traefik.d/>`__ (similar
for KME host 2). Any files should be picked up that are at the top level
of this directory (i.e. be wary of nesting files in deepers
directories).

Docker Provider Configuration
-----------------------------

The docker labels for the ``rest`` service in the
`docker-compose.yml <../docker-compose.yml>`__ file setup the network,
routers, service, and a middleware configuration for the ``rest`` docker
service.

.. _`dynamic_tls`:

File Provider Configuration
---------------------------

Traefik will dynamically watch a file or file directory based on the
static configuration file settings. The `KME Host 1 Dynamic
File <../volumes/kme1/traefik/configuration/traefik.d/tls.yml>`__
dictate the TLS behavior for Traefik.

The TLS Certificates section sets the server-side identity. The default
store is setup to handle requests that do not provide a Server Name
Indication (SNI). The options section is setup to only provide TLS
version 1.2 and above using mutual TLS settings such that a client must
provide a valid certificate. The CA files section sets wich client files
will be authorized to pass through to the ``rest`` docker service.

Depending on how an SAE is configured, it may be necessary to relax the
``sniStrict`` setting and/or the ``clientAuthType``. See Traefik dynamic
TLS configuration documentation for more options.

NOTE: Go Template lanuage (e.g. ``{{ env "LOCAL_KME_ID" }}`` ) is used
within the dynamic configuration file. This is setup to pull environment
variable values which are provided by the docker-compose file which are
ultimately set in the top-level Makefile.

NOTE: The local and remote KME certificates are setup to access the
``rest`` service as well as the locally generated SAE certificate. If
another client certificate was to be generated, it along with its CA
chain would need to be provided to Traefik to access the ``rest``
service.

Looking for Configuration Issues
--------------------------------

When Traefik is set to a log-level of Debug, there should be no errors
arising upon startup or operation. The Traefik Dashboard is also
configured and available as a quick visual reference. There also should
be no errors on the Dashboard.
