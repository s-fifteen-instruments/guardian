# Initialization

KME host `kme1` must complete its initialization steps first:

```bash
# kme1
make clean && make init
```

NOTE: the `clean` and `allclean` Makefile targets run the [clean.sh](../scripts/clean.sh) script which expects to be run as root. Note that the paths are all within the ./volumes directory and utilize no environment variables. Even still, be mindful that these targets will erase everything and should only be run if you plan on starting from scratch.

This initialization sequence will go through several steps to setup a Certificate Authority, a Vault instance and its configuration, and lastly, a simulated QKDE sequence where keying material is generated and ingested into the Vault instance.

Next, KME host `kme2` must complete its initialization before continuing:

```
# kme2
make clean && make init
```

This process is almost identical to KME host `kme1`, except that we ingest keying material from the initial QKDE run sequence instead of running another session.


There are many steps in this process. Refer to the [init script](../scripts/init.sh) and the [docker-compose init](../docker-compose.init.yml) files for specific details.

Intialization need only be run once on each KME host, assuming no errors or issues. A local dot file will be created the prevents initialization from rerunning and overwriting the now existing configuration. To start over from scratch, issue a `make clean` on each host.
