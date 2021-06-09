# Running

* [Starting the REST API](#starting-the-rest-api)
* [Stateful Shutdown](#stateful-shutdown)
* [Clearing the Vault](#clearing-the-vault)
* [Cleaning Up](#cleaning-up)
* [Creating Additional Keying Material](#creating-additional-keying-material)
* [Inspecting Addtional Logs](/#inspecting-addtional-logs)

## Starting the REST API

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

## Stateful Shutdown

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

## Clearing the Vault

To completely clear the Vault secret engine of all records (keys, statuses, and ledgers):

On KME host `kme1`:
```bash
# kme1
make clear
```

On KME host `kme2`:
```bash
# kme2
make clear
```

Order does not matter with this command. Although, if one KME host is cleared, to stay in synchronization, so too should the other KME host.

## Cleaning up

To remove all generated stateful content: certificates, keying material, logs:

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

NOTE: the `clean` and `allclean` Makefile targets run the [clean.sh](../scripts/clean.sh) script which expects to be run as root via `sudo`. Note that the paths are all within the ./volumes directory and utilize no environment variables. Even still, be mindful that these targets will erase everything and should only be run if you plan on starting from scratch.

## Creating Additional Keying Material

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

NOTE: This is an asynchronous task that may be completed while the REST API is up and running. The watcher service will add new keying material to the local Vault instance. Further work would need to be completed to have each KME host communicate when the new keying material is available for consumption. For now, if SAE requests are assigned this new keying material before it is available on both hosts, there is a potential race condition.

## Inspecting Addtional Logs

By default, `make log` will follow the `rest` container service's log until cancelled. It is possible to view other logs by adding the `SERVICES` environment variable:
```bash
# To follow Traefik's log
make log SERVICES=traefik
# To follow both Vault and Traefik simultaneously
make log SERVICES="vault traefik"
# To follow all services in the docker-compose file simultaneously:
make log SERVICES=
```

If you need `docker-compose` commands directly, then set `LOCAL_KME_ID` and `REMOTE_KME_ID` environment variables appropriately; e.g.:
```bash
LOCAL_KME_ID=kme2 REMOTE_KME_ID=kme1 docker-compose -f docker-compose.init.yml logs rest
```
It is recommended to allow the Makefile to handle environment variables. But sometimes, having the underlying command is useful for debugging.

