# Prerequisites

* Setup Certificate Authority secrets
* Correct Vault file permissions
* Setup name resolution for KMEs, SAEs
* Setup NFS mount for certificate sharing (can be done manually)
* Setup NFS mount for sharing epoch files (unnecessary with full QDKEs up and running)
* Docker daemon running with user in docker group
* docker-compose command available

# Initialization

There will be two KME hosts; call them `kme1` and `kme2`. They will serve as the two endpoints that SAEs will interact with to receving keying material.

Clone this repository to each KME host; we'll put it in `~/code/guardian`

```bash
mkdir -p ~/code && cd ~/code
git clone https://github.com/s-fifteen-instruments/guardian.git
cd guardian
```

Address the prerequisites above.

Next, on each KME host, ensure the KME variable matches the KME host (`kme1` or `kme2`) in the top-level [Makefile](../Makefile):

```Makefile
##########################
##### CAN CHANGE ME ######
##########################
export KME ?= kme1
##########################
##########################
##########################
```

Each KME has slightly different tasks to complete for initialization and this variable is what dictates this behavior.

Next, KME host `kme1` must complete its initialization steps first:

```bash
# kme1
make clean && make init
```

This initialization sequence will go through several steps to setup a Certificate Authority, a Vault instance and its configuration, and lastly, a simulated QKDE sequence where keying material is generated and ingested into the Vault instance.

Next, KME host `kme2` must complete its initialization before continuing:

```
# kme2
make clean && make init
```

This process is almost identical to KME host `kme1`, except that we ingest keying material from the initial QKDE run sequence instead of running another session.


There are many steps in this process. Refer to the [init script](../scripts/init.sh) and the [docker-compose init](../docker-compose.init.yml) files for specific details.

Intialization need only be run once on each KME host, assuming no errors or issues. A dot file will be created the prevents initialization from rerunning and overwriting the now existing configuration. To start over from scratch, issue a `make clean` on each host.

# Running

Once each KME host has successfully completed initialization, each can now start the REST API frontend that the SAEs will interact with.

On KME host `kme1`:
```bash
# kme1
make rest
```

On KME host `kme2`:
```bash
# kme2
make rest
```

If you wish to view the REST API server logs, you may issue:

```bash
# Either KME host
make log
```

to begin a log session that follows output in real-time. Issue a `CONTROL+C` (or equivalent on your OS) to end the log following session.


Refer to the [run script](../scripts/run.sh) and the [docker-compose](../docker-compose.yml) files for specific details.

# Creating Additional Keying Material

For now, qcrypto and driver scripts are started up to consume simulated entangled photons on KME host `kme1`

First, on KME host `kme1`:
```bash
# kme1
make keys
```

After KME host `kme1` has completed the key generation step, from KME host `kme2`:
```bash
# kme2
make keys
```

This sequence will start up a service to watch for new qcrypto final epoch files and a service to notify when those new files are available. qcrypto has a notify FIFO that can and should be used for this purpose in the future. The watcher service once notified will ingest and format the keying material to be put into the local Vault instance.

# Shutdown

On each KME host, we need to stop the Docker containers running our KME's services.

On KME host `kme1`:
```bash
# kme1
make down
```

On KME host `kme2`:
```bash
make down
```

You may restart the services by re-issuing a `make rest` again to resume.

# Cleaning up

To remove all generated content: certificates, keying material, logs:

On KME host `kme1`:
```
# kme1
make clean
```

On KME host `kme2`:
```bash
make clean
```

Currently, cleaning one KME host but not the other may lead to, at the least, mismatches in keying material. Also, the Traefik service would need to be restarted to pick up the new certificates. It is recommended to clean both KME hosts together. 



# License

`Guardian` is a quantum key distribution REST API and supporting software stack.
Copyright (C) 2021  W. Cyrus Proctor

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
