Requirements
============

Guardian is built upon Docker containers running FastAPI, Vault and traefik. OpenSSL is used for some certificate signing before Vault is set up. Binding these together are bash scripts, Python scripts and docker-compose scripts.


To start from a clean installation, the following steps are necessary.

#. Establish domain name resolution of name to ip address, either via hosts file or a proper DNS server.

#. Install the docker and docker-compose. Start the docker daemon/server.

#. Install git to clone the Guardian repository from Github.


ROOT CA
^^^^^^^

When packaged on S-Fifteen's QKD device, Guardian is already installed with the certificate chain up to the Root CA. Otherwise, the Root CA and intermediate CA chain needs to be set up too. 


Hardware
--------

For building the Docker images, a fairly decent amount of memory is required. It is recommended to have >2 GB of Ram for a smooth build. A network connection is also necessary to establish communications to the other Guardian running on the other host.

