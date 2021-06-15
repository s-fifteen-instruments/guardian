# Demonstration Instructions

## Hostnames and IP Addresses

| Hostname | IP Address |
| --- | --- |
| s1-kme1 | 139.59.100.122 |
| s1-kme2 | 139.59.120.255 |
| s2-kme1 | 165.22.248.223 |
| s2-kme2 | 68.183.230.21 |
| s3-kme1 | 206.189.90.168 |
| s3-kme2 | 165.22.244.41 |
| s4-kme1 | 165.22.248.242 |
| s4-kme2 | 165.22.240.161 |
| s5-kme1 | 174.138.24.192 |
| s5-kme2 | 174.138.28.92 |

Each person who wishes to participate should claim one KME host set (s1, s2, s3, s4, or s5).

## Logging in via SSH

### Windows Users

If you use a Windows operating system and you plan on participating, I recommend using PuTTY as your SSH client. If you choose another, you are on your own for getting setup with the supplied IP address and RSA key pair.

For PuTTY users, you will need to convert the supplied (via email) RSA private key using the tool PuTTYgen:
* Download the `sfi_demo` and `sfi_demo.pub` keys to your local machine
* Download the `puttygen.exe` binary that is appropriate for your system from [here](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html). The **puttygen.exe** binary; NOT the **PuTTY** binary!
* Your goal is to create a PuTTY-formatted .ppk private key file for use with your PuTTY SSH session; follow the tutorial [here](https://devops.ionos.com/tutorials/use-ssh-keys-with-putty-on-windows/#use-existing-public-and-private-keys)
* Combine the converted .ppk file along with the supplied IP addressed to your KME host set to login as the `root` user

### Users with a native terminal (Linux/Mac OS)

It is typical to save SSH keypairs in the directory `~/.ssh/` but they can be anywhere, technically.

Download the keypair, and double check permissions:
```bash
ls -al ~/.ssh/
total 84
drwxrwxr-x. 1 cproctor cproctor   394 Jun 15 12:56 .
drwx--x---+ 1 cproctor cproctor  3240 Jun 15 12:56 ..
-rw-------. 1 cproctor cproctor  2602 Jun 14 15:42 sfi_demo
-rw-r--r--. 1 cproctor cproctor   568 Jun 14 15:42 sfi_demo.pub
...
```

Note that the private key is 0600 and the public key is 0644 (permission octal codes).

To login to your KME hosts, use a command line similar to:
```bash
# kme1
ssh -i /path/to/sfi_demo/rsa/private/key root@<kme1-ip-address>
# kme2
ssh -i /path/to/sfi_demo/rsa/private/key root@<kme2-ip-address>
```

You may also edit `~/.ssh/config` to include the following
```bash
Host kme1
  User root
  Hostname <kme1-ip-address>
  IdentityFile /path/to/sfi_demo/rsa/private/key
Host kme2
  User root
  Hostname <kme2-ip-address>
  IdentityFile /path/to/sfi_demo/rsa/private/key
```

and you could then use `kme1` and `kme2` in your SSH command-line instead of the IP address directly.

# Getting Started

Once you are logged in on *both* KME hosts; i.e. have two separate terminals open and logged in to KME host 1 and KME host 2, navigate to the code repository location:
```bash
# Example for KME host 1
#
root@s1-kme1:~/code# cd
root@s1-kme1:~# whoami
root
root@s1-kme1:~# pwd
/root
root@s1-kme1:~# cd ~/code/
root@s1-kme1:~/code# ls -al
total 5624
drwxr-xr-x 2 root root    4096 Jun 15 15:55 .
drwx------ 6 root root    4096 Jun 15 15:55 ..
-rw-r--r-- 1 root root 5750390 Jun 15 13:09 guardian-0.5.tar.gz
```

On both KME hosts, untar the `guardian-0.5.tar.gz` gzipped tarball:
```bash
# Example for KME host 1
root@s1-kme1:~/code# tar xfz guardian-0.5.tar.gz
root@s1-kme1:~/code# ls -al
total 5628
drwxr-xr-x  3 root root    4096 Jun 15 18:04 .
drwx------  6 root root    4096 Jun 15 15:55 ..
drwxr-xr-x 15 1000 1000    4096 Jun 15 13:08 guardian-0.5
-rw-r--r--  1 root root 5750390 Jun 15 13:09 guardian-0.5.tar.gz
root@s1-kme1:~/code# cd guardian-0.5/
root@s1-kme1:~/code/guardian-0.5# pwd
/root/code/guardian-0.5
```

## Turning Up the Logging Level

After changing directory into the guardian repository, edit the configuration file that controls the logging level for our Docker services, which is [${TOP_DIR}/common/log.env](../common/log.env). Change the file with you favority remote text editor (I have installed emacs, nano, and vim for your convenience) to read:
```
# NOTE: No variable substitution or expansion
# Vault log level options: Trace, Debug, Error, Warn, Info
VAULT_LOG_LEVEL=Debug
# Traefik log level options: DEBUG, PANIC, FATAL, ERROR, WARN, INFO
# Appears to be ignored. Set in static traefik.yml file instead.
#TRAEFIK_LOG_LEVEL=
# HTTPX log level options: (unset), debug, trace
HTTPX_LOG_LEVEL=debug
# QKD log level options: (unset), debug
QKD_LOG_LEVEL=debug
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
VAULT_INIT_LOG_LEVEL=10
NOTIFY_LOG_LEVEL=10
WATCHER_LOG_LEVEL=10
UNSEALER_LOG_LEVEL=10
REST_LOG_LEVEL=10
```

Update and save this file for both KME hosts. This will help us debug any issues that may arise while we set up our KME hosts.

# Moving On

Jump into the [Prerequisites documentation](Prerequisites.md)

NOTE: You may skip the following steps on the Prerequisites page:
* Setup Passwordless SSH
* Installing docker and docker-compose
* Cloning

Please ensure all other steps are carried out on the `Prerequisites` page before moving on in the order shown in the top-level [Info README](README.md) file.
