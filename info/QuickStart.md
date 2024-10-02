# Quick Start

This document gives full instructions for a two-node Guardian setup, with network separation between internal inter-KME communication and KME-SAE communication.

Tested with openSUSE 15.6 (Docker 25.0.6-ce) and Ubuntu 24.04 (Docker 24.0.5).

## Network setup

Domain names should be used and need to be resolvable.
If a DNS server is unavailable, set up static hosts in `/etc/hosts` instead:

```
192.168.1.1    qkde0001.internal
192.168.1.2    qkde0002.internal
192.168.101.1  qkde0001.public
192.168.102.1  qkde0002.public
```

Appropriate firewall rules can be set up for each interface on the host itself. Take special care with Docker ports which may bypass your local firewall rules, e.g. `ufw`, due to direct modification via `iptables`.
The relevant ports used by Guardian are:

* Port 8200/tcp for Vault (keystore) interface
* Port 443/tcp for the HTTP(S) and REST interface
* Port 80/tcp for HTTPS redirection

These interfaces are secured behind mutual TLS, so unintended firewall holes may not necessarily be a big security concern.

## Initial configuration

Clone the Guardian repository at each desired node.

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

## Running

On each side, run `make init` as root, then `make connect` once the remote side is done configuring.

The REST service can be started using `make rest`, and torn down using `make down`. To reset KME configuration and rebuild, use `make clean` (or `make allclean` for more destructive behaviour).

Two endpoints are available:
* `https://${LOCAL_KME_ADDRESS}/docs` for FastAPI's wrapper for quick tests.
  * The client certificate and key are found in `volumes/${LOCAL_KME_ID}/certificates/production/admin/${LOCAL_SAE_ID}/*.p12`.
* `https://${LOCAL_KME_ADD_SSH}:8200` for direct Vault access. Note that keys need to be generated for the correspond key ledger table to be instantiated.
  * The default root login token for Vault is found in `volumes/${LOCAL_KME_ID}/certificates/production/admin/vault/SECRETS`.

## Backend QKD and simulator

QKD keys are ingested from the `epochs` volume by the `watcher` service, which reads epoch values from the `notify.pipe` pipe and extracts key bits from the file of the same name (before deletion). See the detailed file specification for [epoch values](https://github.com/s-fifteen-instruments/qcrypto/blob/master/remotecrypto/epochdefinition) and the [key bit files (stream-7)](https://github.com/s-fifteen-instruments/qcrypto/blob/master/remotecrypto/filespec.txt).

QKD keys can be generated locally using a PRNG as well (as opposed to network copies of the key). A simple script that can be mocked as a QKD interface compatible with Guardian is provided [here](https://github.com/s-fifteen-instruments/QKDServer/blob/master/scripts/simulate_keygen.py). Some quick instructions to run this from within the `watcher` container (use `docker exec -it guardian-watcher-1 /bin/sh` to summon a shell):

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

If a custom mock interface is desired, the format of the piped data is implemented [here](https://github.com/s-fifteen-instruments/QKDServer/commit/978c1c03c6b545e89968dbe3b10893a1fde6a39b).
If network activity simulation is desired, consult the QKD backend provider for the network packet file specifications.
