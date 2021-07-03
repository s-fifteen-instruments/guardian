# Prerequisites

* [Host File Customization](#host-file-customization)
* [Setup Passwordless SSH](#setup-passwordless-ssh)
* [Installing Docker and docker-compose](#installing-docker-and-docker-compose)
* [Cloning the Github Repository](#cloning)
* [Makefile Customization](#makefile-customization)
* [Certificate Authority Secrets](#certificate-authority-secrets)

There will be two KME hosts; call them `kme1` and `kme2`. They will serve as the two endpoints that SAEs will interact with to receive keying material.

## Host File Customization

On each KME host, determine which network interface IP address will be used for remote communication between them. You may try `hostname --ip-address` or `ip address` commands to help determine which to use; for example:
```bash
# KME1 Host
alice@qtpi-1:~/code/guardian$ hostname --ip-address
192.168.1.75
```
```bash
# KME2 Host
bob@qtpi-2:~/code/guardian$ hostname --ip-address
192.168.1.90
```

Similarly, determine which IP addresses to use for each of the SAE hosts.

NOTE: For testing, each KME host is a Raspberry Pi while I set the SAE hosts to my laptop's IP address (192.168.1.153).

Next, on each KME host, edit with root privilege the `/etc/hosts` file to set up basic name resolution:
```bash
sudo vim /etc/hosts
```
Add in the lines:
```bash
192.168.1.75 kme1
192.168.1.90 kme2
192.168.1.153 sae1 sae2
```

Test using `ping` on each KME to ensure that name resolution is working:
```bash
# KME1 Host
alice@qtpi-1:~/code/guardian$ ping -c 1 kme1
PING kme1 (192.168.1.75) 56(84) bytes of data.
64 bytes from kme1 (192.168.1.75): icmp_seq=1 ttl=64 time=0.198 ms

--- kme1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.198/0.198/0.198/0.000 ms
alice@qtpi-1:~/code/guardian$ ping -c 1 kme2
PING kme2 (192.168.1.90) 56(84) bytes of data.
64 bytes from kme2 (192.168.1.90): icmp_seq=1 ttl=64 time=0.393 ms

--- kme2 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.393/0.393/0.393/0.000 ms
...
```

```
# KME2 Host
bob@qtpi-2:~/code/guardian$ ping -c 1 kme1
PING kme1 (192.168.1.75) 56(84) bytes of data.
64 bytes from kme1 (192.168.1.75): icmp_seq=1 ttl=64 time=0.371 ms

--- kme1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.371/0.371/0.371/0.000 ms
bob@qtpi-2:~/code/guardian$ ping -c 1 kme2
PING kme2 (192.168.1.90) 56(84) bytes of data.
64 bytes from kme2 (192.168.1.90): icmp_seq=1 ttl=64 time=0.203 ms

--- kme2 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.203/0.203/0.203/0.000 ms
...
```

## Setup Passwordless SSH

To automatically share TLS certificates, and at the moment QKD key information, we need to setup the ability to establish SSH connections between the KME hosts without the need to intervene with a password each time. This is done by adding corresponding public keys to each KME host's SSH authorized keys file.

On each KME host, first generate an RSA (other types okay too) public/private key pair if one does not already exist:
```bash
# KME1 host
cd  # Go to home directory
mkdir -p ~/.ssh
# Inspect ~/.ssh; if you already have keypairs, you may use them; overwrite at your own risk
ssh-keygen -t rsa
# Hit return for all defaults; do not set a passphrase unless you are confident in handling ssh-agents and keyrings
```

You end up with:
```bash
# KME1 host
alice@qtpi-1:~$ ls -al ~/.ssh/
total 16
drwxrwxr-x  2 alice alice 4096 Jun  8 16:43 .
drwxr-xr-x 13 alice alice 4096 Jun  8 16:42 ..
-rw-------  1 alice alice 2602 Jun  8 16:44 id_rsa
-rw-r--r--  1 alice alice  566 Jun  8 16:44 id_rsa.pub
```

Similarly, for the KME2 host. Next, we copy the id_rsa.pub file into the authorized_keys file of both the local and the remote host. Use `ssh-copy-id` if you have it; otherwise, `scp` the public key over to the remote host and append its contents onto ~/.ssh/authorized_keys:
```bash
# From KME1 to KME2
alice@qtpi-1:~$ ssh-copy-id bob@kme2
/usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "/home/alice/.ssh/id_rsa.pub"
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
bob@kme2's password:

Number of key(s) added: 1

Now try logging into the machine, with:   "ssh 'bob@kme2'"
and check to make sure that only the key(s) you wanted were added.
```

Do the same 3 more times:
```bash
alice@qtpi-1:~$ ssh-copy-id alice@kme1
bob@qtpi-2:~$ ssh-copy-id alice@kme1
bob@qtpi-2:~$ ssh-copy-id bob@kme2
```

And, indeed, we are not prompted to enter a password. Ensure that this works going from KME1 to KME2, from KME1 to KME1, from KME2 to KME2 and going from KME2 to KME1. The first time you SSH, you will be prompted to inspect the SSH fingerprint of the server. Answer yes to the query to store the fingerprint in the ~/.ssh/known_hosts file.

NOTE: In a full QKD setup, QKD keys will arrive at the remote QKDE via the quantum channel and have no need of passwordless SSH connections. In this simulated QKD setup, keying material is being generated on the Primary QKDE/KME host and then `rsync`ed over to the Secondary QKDE/KME. Similarly, for the TLS client certificates, it is possible to manually transfer the correct certificates between KMEs instead of using SSH. This is done mainly for convenience and later for testing.

## Installing docker and docker-compose

### Docker

Please refer to the following [Docker Instructions](https://docs.docker.com/engine/install/) to appropriately install the docker. I recommend the most basic package-managed version of docker on your KME systems; i.e. stay away from manually installed static binaries. For reference, I installed Ubuntu 20.04 on Raspberry Pi 4's and use the ARM64 architecture. Refer to your distribution's instructions (e.g. OpenSUSE) if direct instructions do not appear on the Docker page.

Next, add the user who will be operating the `guardian` REST API to the `docker` Linux group; e.g. user `alice`:
```bash
alice@qtpi-1:~$ groups
alice admin
alice@qtpi-1:~$ sudo usermod -a -G docker alice
# Log out and log back in to take effect
alice@qtpi-1:~$ groups
alice admin docker
```

You will need to re-login to see the change take effect. Do this on both KME hosts. This allows user `alice` to run docker commands without needing privileged access to the system.

NOTE: I recommend keeping the Docker daemon itself running as root as there are several privileged ports that are used throughout (80/443). YMMV.

If you wish docker to start upon host startup:
```bash
sudo systemctl enable docker
```

To start the docker daemon:
```bash
sudo systemctl start docker
# Inspect that it did startup properly
systemctl status docker
```

Test with docker `hello-world`:
```bash
alice@qtpi-1:~$ systemctl status docker
● docker.service - Docker Application Container Engine
     Loaded: loaded (/lib/systemd/system/docker.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2021-06-04 19:52:33 UTC; 3 days ago
TriggeredBy: ● docker.socket
       Docs: https://docs.docker.com
   Main PID: 1906 (dockerd)
      Tasks: 25
     CGroup: /system.slice/docker.service
             └─1906 /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock

Warning: some journal files were not opened due to insufficient permissions.
alice@qtpi-1:~$ docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
256ab8fe8778: Pull complete
Digest: sha256:5122f6204b6a3596e048758cabba3c46b1c937a46b5be6225b835d091b90e46c
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.
...
For more examples and ideas, visit:
 https://docs.docker.com/get-started/
```

### docker-compose

Next, install docker-compose. Again, I recommend if possible to install based off your distribution's instructions utilizing a package manager; e.g. [OpenSUSE](https://en.opensuse.org/Docker) or [Fedora](https://developer.fedoraproject.org/tools/docker/compose.html).

If you'd like to go through a docker-compose tutorial (not necessary), checkout the [docker docs page](https://docs.docker.com/compose/gettingstarted/).

At least verify it is working:
```bash
alice@qtpi-1:~$ docker-compose --version
docker-compose version 1.25.0, build unknown
```

Ensure that the version isn't too old, otherwise some newer syntax may not work (the version 1.25.0 is sufficient as of this writing 2021/06/08).

Only if necessary, use Python pip to update the version; see [here](https://pypi.org/project/docker-compose/). Decide whether to upgrade as root or as an individual user. Understand having both package managed and pip managed versions can lead to conflicts.

Not recommended: Last resort, download a staic binary from the [docker-compose site](https://docs.docker.com/compose/install/) (gross).

## Cloning

Clone this repository to each KME host; we'll put it in `~/code/guardian` where the tilde is expanded by current user's shell to their home directory: 

```bash
mkdir -p ~/code && cd ~/code
git clone https://github.com/s-fifteen-instruments/guardian.git
cd guardian
export TOP_DIR=`pwd`
git fetch --all --tags
```

NOTE: We'll refer to this directory throughout as `${TOP_DIR}`.

Let's inspect all the current tags of the repository:
```bash
alice@qtpi-1:~/code/guardian$ git tag -l -n
v0.1            Initial release
v0.2            Move configuration links in common directory
v0.3            Global Configuration Model
...
```

Let's inspect all the branches of the repository:
```bash
alice@qtpi-1:~/code/guardian$ git branch -a
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
```

I have kept a fairly linear main branch with offshoots for specific fixes and then removed the branches afterwards. The tags are fairly major milestones and can be accompanied by a Github release, if one configures it. In the most basic setup, to checkout a specific tag:
```bash
git checkout tags/v0.3
```

Replace `v0.3` with whatever tag you wish.


## Makefile Customization

On each KME host, ensure the KME variable matches the KME host role (`kme1` or `kme2`) in the top-level [Makefile](../Makefile):

```Makefile
##########################
##### CAN CHANGE ME ######
## OR SET ME IN THE ENV ##
##########################
# - Choose "kme1" or "kme2" for the local KME identity.
export KME ?= kme1
...
```

Each KME has slightly different tasks to complete for initialization and this variable is what dictates this behavior.

Next, on each KME host, in the same Makefile, customize the directory paths for the local and remote `guardian` Git repositories:

```Makefile
# - Location of Local KME's guardian git repository
export LOCAL_KME_DIRPATH ?= alice@kme1:/home/alice/code/guardian
# - Location of Remote KME's guardian git repository
export REMOTE_KME_DIRPATH ?= bob@kme2:/home/bob/code/guardian
# NOTE:
# - Set to <username>@<hostnameORip>:<path/to/guardian/repository>
# - It is expected that passwordless SSH access is set up to this location.
# - Use a full absolute path. Do not use env variables or tilde (~) as
#   they will not necessarily expand correctly in a remote context.
```

NOTE: The `LOCAL` and `REMOTE` designations will reverse for KME2 host. In other words, for KME1 host, KME2 is the remote and for KME2 host, KME1 is the remote. Again, at minimum the REMOTE_KME_DIRPATH needs to be accessible via passwordless SSH.

## Certificate Authority Secrets

First, change directory over into the `common` directory and copy `CERTAUTH_SECRETS.example` to `CERTAUTH_SECRETS`:
```bash
cd ${TOP_DIR}/common
cp ./CERTAUTH_SECRETS.example CERTAUTH_SECRETS
```

Edit the file as needed following directions of the comments:
```bash
# Copy this template file to ./CERTAUTH_SECRETS and fill in private secrets

# Root Certificate Authority Password
export ROOT_CA_PASSWORD=changeme
# Intermediate Certificate Authority Password
export INT_CA_PASSWORD=changemetoo
...
```

It is recommended to update `ROOT_CA_PASSWORD` and `INT_CA_PASSWORD`, but it is not necessary. Leave the rest alone.

Now, copy `CERTAUTH_CONFIG.example` to `CERTAUTH_CONFIG` and customize:
```bash
cp CERTAUTH_CONFIG.example CERTAUTH_CONFIG
```
It is recommended to customize if there are certificate issues. Otherwise, it is fine as it is:
```bash
# Elliptic Curve Name (openssl ecparam -list_curves)
EC_NAME=secp384r1

# Root Certificate Authority Information
export CA_COUNTRY_CODE="US"
export CA_STATE="Texas"
export CA_LOCALITY="Austin"
export CA_ORGANIZATION="Quantum Internet Technologies LLC"
export CA_UNIT="Quantum Hacking Division"
export CA_COMMON_NAME="${CA_ORGANIZATION} Root CA ${LOCAL_KME_ID}"
export CA_EMAIL="admin@example.com"

# Intermediate Certificate Authority Information
export INT_CA_COUNTRY_CODE="${CA_COUNTRY_CODE}"
export INT_CA_STATE="${CA_STATE}"
export INT_CA_LOCALITY="${CA_LOCALITY}"
export INT_CA_ORGANIZATION="${CA_ORGANIZATION}"
export INT_CA_UNIT="${CA_UNIT}"
export INT_CA_COMMON_NAME="${INT_CA_ORGANIZATION} Intermediate CA ${LOCAL_KME_ID}"
export INT_CA_EMAIL="${CA_EMAIL}"

# Subject Alternative Names (SANs) for Intermediate CA
export ALT_NAMES=$(cat << EOA
DNS.1 = localhost
DNS.2 = vault
DNS.3 = vault_init
DNS.4 = rest
DNS.5 = kme1
DNS.6 = kme2
DNS.7 = 172.16.192.*
DNS.8 = 192.168.1.*
IP.1 = 127.0.0.1
IP.2 = 192.168.1.153
IP.3 = 192.168.1.75
IP.4 = 192.168.1.90
EOA
)
```

Refer the CERTAUTH Root and Intermediate CA configuration templates for constraints. Also, it may be necessary to customize the IP subnet depending on the particular setup. Lastly, it is possible to customize the CA private key types using the `EC_NAME` variable. Choose the named curve from the output of `openssl ecparam -list_curves`.
