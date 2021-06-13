# First Time Only

When you first clone the repository on both KME hosts, there are some special permissions that need to be set for bind mounted volumes that Vault writes information to. Git by itself does not track the correct permissions infomration to help with this issue. To set permissions correctly, go to the top-level repository directory on each KME host and run:
```bash
# kme1
${TOP_DIR}/scripts/init_permissions.sh main
```

Similarly on the other KME host:
```bash
# kme2
${TOP_DIR}/scripts/init_permissions.sh main
```

This script checks out the `main` branch and  will require sudo priviledges to set the permissions that are listed in the `${TOP_DIR}/.permissions` file. Moreover, this sets the appropriate Git hooks such that this process is automatically done on any subsequent pre- and post-commit Git actions. See the [post-checkout](../scripts/hooks/post-checkout) and [pre-commit](../scripts/hooks/pre-commit) hooks for more details.

To notice the difference between doing this step and not doing this step requires the Vault service to be outputting at the `Debug` log level to read that it is having trouble writing out information. Please see the [Logging](Logging.md) configuration file for more details on how to do that.

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
