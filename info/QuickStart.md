# Quick Start

This document gives full instructions for a two-node Guardian setup, with network separation between internal inter-KME communication and KME-SAE communication.

Tested with openSUSE 15.6 (Docker 25.0.6-ce) and Ubuntu 24.04 (Docker 24.0.5). Running both nodes on the same host is currently unsupported, e.g. due to port conflicts.

## Network setup

Domain names should be used and need to be resolvable. These can be user-defined to suit the existing DNS/network configuration.
If a DNS server is unavailable, set up static hosts in `/etc/hosts` instead. The example deployment below will use the following hosts setup:

```
192.168.1.1    qkde0001.internal
192.168.1.2    qkde0002.internal
192.168.101.1  qkde0001.public
192.168.102.1  qkde0002.public
```

If network separation is not required, simply map both the internal and public domains to the same IP address.

Appropriate firewall rules can be set up for each interface on the host itself. Take special care with Docker ports which may bypass your local firewall rules, e.g. `ufw`, due to direct modification via `iptables`.
The relevant ports used by Guardian are:

* Port 8200/tcp for Vault (keystore) interface
* Port 443/tcp for the HTTP(S) and REST interface
* Port 80/tcp for HTTPS redirection

These interfaces are secured behind mutual TLS, so unintended firewall holes may not necessarily be a big security concern.

## Initial configuration

These instructions are simplified for users running the software for the first time:

- Clone the Guardian repository at each desired node, using the `2node_networksep` branch.
- Run `make init_test` on both sides, to generate certificates and configuration.
- Mirror the node-specific addresses and repository locations on the remote node (see below for an example diff).
- On each side, run `make init` as root, then `make connect` once the remote side is done configuring.

<details>
<summary>Corresponding commands</summary>

```bash
git clone -b 2node_networksep git@github.com:s-fifteen-instruments/guardian.git
cd guardian
make init_test
vim Makefile  # edit the remote repository location (and node-specific IDs for the remote node)
sudo make init
make connect  # only once the remote is done with its init
```

</details>

<details>
<summary>Example changes made for the remote node, from the initial configuration</summary>

```diff
diff --git a/Makefile b/Makefile
index 368cc9b..93a5a61 100644
--- a/Makefile
+++ b/Makefile
@@ -23,18 +23,18 @@
# Location of local and remote KME's guardian git repository
# - For transferring REST client certificates for inter-KME communication.
# - Passwordless SSH access must be set up to the remote directory.
-export LOCAL_KME_ADDRESS  ?= qkde0002.public
-export REMOTE_KME_ADDRESS ?= qkde0001.public
-export LOCAL_KME_ADD_SSH  ?= qkde0002.internal
-export REMOTE_KME_ADD_SSH ?= qkde0001.internal
-export REMOTE_KME_DIR_SSH ?= qitlab@$(REMOTE_KME_ADD_SSH):~/programs/software/s-fifteen/guardian
+export LOCAL_KME_ADDRESS  ?= qkde0001.public
+export REMOTE_KME_ADDRESS ?= qkde0002.public
+export LOCAL_KME_ADD_SSH  ?= qkde0001.internal
+export REMOTE_KME_ADD_SSH ?= qkde0002.internal
+export REMOTE_KME_DIR_SSH ?= qitlab@$(REMOTE_KME_ADD_SSH):~/guardian

# Identity strings for QKDE and KME, with an initial local SAE bootstrapped, swap at remote
-export LOCAL_QKDE_ID  ?= QKDE0002
-export REMOTE_QKDE_ID ?= QKDE0001
-export LOCAL_KME_ID  ?= KME-S15-Guardian-002-Guardian
-export REMOTE_KME_ID ?= KME-S15-Guardian-001-Guardian
-export LOCAL_SAE_ID ?= SAE-S15-Test-002-sae1
+export LOCAL_QKDE_ID  ?= QKDE0001
+export REMOTE_QKDE_ID ?= QKDE0002
+export LOCAL_KME_ID  ?= KME-S15-Guardian-001-Guardian
+export REMOTE_KME_ID ?= KME-S15-Guardian-002-Guardian
+export LOCAL_SAE_ID ?= SAE-S15-Test-001-sae1

# Path used only for key comparison tests, *no need to modify* if not performing out-of-band tests
export LOCAL_KME_DIRPATH  ?= s-fifteen@$(LOCAL_KME_ADDRESS):~/code/guardian
```

</details>

<details>
<summary>Instructions for commit `e32780c3` and/or custom configuration</summary>

Run `./scripts/init_permissions.sh ${CURR_BRANCH_NAME}` as root to set required permissions for Vault.

Run `make generate_config`, and modify as much (or little) as desired.

Populate the certificates for the KME, under `common/kme-ca.cert.pem`, `common/kme-ca.key.pem` and `common/full-chain.cert.pem`.
  * Ensure that the `ROOT_CA_PASSWORD` variable in `CERTAUTH_SECRETS` matches that of the private key passphrase.
  * This will be used to provision the intermediate CA certificate used by Vault's PKI, which in turn manages client certificates for both internal services and SAEs.
  * If existing certificates are not available, run `make generate_sample_certs` to generate temporary certificates using [EasyRSA](https://github.com/OpenVPN/easy-rsa).

Edit the `Makefile` with the appropriate variables:
* `LOCAL_KME_ADDRESS` and `LOCAL_KME_ADD_SSH` correspond to the node's external and internal domain name.
* `REMOTE_KME_ADDRESS` and `REMOTE_KME_ADD_SSH` correspond to that of the remote node.
* `REMOTE_KME_DIR_SSH` points to the remote Guardian directory via SSH.
  * This is used for copying REST certificates for inter-KME access.
  * Passwordless SSH access is required (hint: `ssh-copy-id`), and used for non-interactive copies.

Some additional variables should not be edited (except when swapping at the remote node) for the 2-node test deployment:
* `LOCAL_QKDE_ID` and `REMOTE_QKDE_ID` identify the QKD backend entity tied to the corresponding node.
* `LOCAL_KME_ID`, `REMOTE_KME_ID` and `LOCAL_SAE_ID` ideally follows whichever user specification used.
* These need to align with the entries in the global connections file located at `volumes/connections`, in order for multi-node operation.
* Additional SAEs can be specified, and subsequently provisioned using Vault's PKI.
</details>

## Running the REST service and key generation

The REST service is started using `make rest`. This also automatically starts the key generation simulator script as well.

* Stopping only the `guardian-qkdsim-1` container is sufficient to stop key generation.
  * **IMPORTANT**: To avoid conflicts with existing keys, specify a different generation start time by changing `epoch` in the configuration, i.e. `qkd/csim/simulate_keygen.py.conf.example` before restarting the container.
  * Epochs of previously generated keys can be checked under the `guardian-qkdsim-1` container logs.
* If the QKD simulator is not desired, e.g. manual start / using a custom simulator / actual QKD backend, this can be disabled by uncommenting the `profiles: [donotstart]` line under the `qkdsim` service in `docker-compose.yml`.
* The REST service and key simulator can be simulataneously torn down using `make down`.

Two additional endpoints are available, on top of the usual ESTI-014 "api" endpoint:
* `https://${LOCAL_KME_ADDRESS}/docs` for FastAPI's wrapper for quick tests.
  * The client certificate and key are found in `volumes/${LOCAL_KME_ID}/certificates/production/admin/${LOCAL_SAE_ID}/*.p12`.
* `https://${LOCAL_KME_ADD_SSH}:8200` for direct Vault access. Note that keys need to be generated for the correspond key ledger table to be instantiated.
  * The default root login token for Vault is found in `volumes/${LOCAL_KME_ID}/certificates/production/admin/vault/SECRETS`.

To reset KME configuration and rebuild, use `make clean` (or `make allclean` for more destructive behaviour).

<details>
<summary>Corresponding commands</summary>

```bash
make rest
docker ps -a                       # check container status
docker logs -f guardian-qkdsim-1   # verify keys are generated
docker logs -f guardian-watcher-1  # verify keys are ingested
docker stop guardian-qkdsim-1      # stop key generation
make clean                         # teardown the KME
```

</details>


## Backend QKD and simulator

QKD keys are ingested from the `epochs` volume by the `watcher` service, which reads epoch values from the `notify.pipe` pipe and extracts key bits from the file of the same name (before deletion). See the detailed file specification for [epoch values](https://github.com/s-fifteen-instruments/qcrypto/blob/master/remotecrypto/epochdefinition) and the [key bit files (stream-7)](https://github.com/s-fifteen-instruments/qcrypto/blob/master/remotecrypto/filespec.txt).

QKD keys can be simulated by generating symmetric keys locally using a PRNG (as opposed to network copies of the key) independently on both sides. A simple script that can be mocked as a QKD interface compatible with Guardian is provided [here](https://github.com/s-fifteen-instruments/QKDServer/blob/master/scripts/simulate_keygen.py). This has been integrated in docker-compose to start automatically, as of commit `66b5e75d`.

If a custom mock interface is desired, the format of the piped data is implemented [here](https://github.com/s-fifteen-instruments/QKDServer/commit/978c1c03c6b545e89968dbe3b10893a1fde6a39b).
If network activity simulation is desired, consult the QKD backend provider for the network packet file specifications.

<details>
<summary>Manual keygen instructions for commit `e32780c3`</summary>

We run this script from within the `watcher` container (use `docker exec -it guardian-watcher-1 /bin/sh` to summon a shell):

```bash
# Pull key simulator script
wget https://raw.githubusercontent.com/s-fifteen-instruments/QKDServer/refs/heads/master/scripts/simulate_keygen.py
wget https://raw.githubusercontent.com/s-fifteen-instruments/QKDServer/refs/heads/master/scripts/simulate_keygen.py.default.conf

# Install dependencies
wget https://github.com/s-fifteen-instruments/fpfind/archive/refs/heads/main.zip
unzip main.zip
cd fpfind-main
pip3 install .
cd ..

# Run the key simulator
apk add vim
vim simulate_keygen.py.default.conf
#...
#localconn = QKDE0001    # swap as appropriate
#remoteconn = QKDE0002   # swap as appropriate
#seed = 1                # PRNG seed
#epoch = b1234567        # reference epoch to align key bits
#length = 10             # number of key files to concatenate, spaced every 0.536s (behaviour from our QKD backend)
#bitrate = 1000          # overall bitrate in bits/s
python3 simulate_keygen.py -vv  # run in background if needed, hint: bg/nohup
```

</details>
