# Vault Instance


## Configuration

A local Vault instance is configured using a file [KME Host 1](../volumes/kme1/vault/config/vault-config.hcl) and [KME Host 2](volumes/kme2/vault/config/vault-config.hcl).

Likley nothing should need to change in this file. 
* The user interface is enabled, a default log-level is set but superseded by an environment variable set in the log.env file
* A max lease time-to-live (ttl) is set here for authentication tokens
* A basic file storage path is setup and could be changed if one desired
* A TCP listener is setup to listen on port 8200 with minimum TLS version of 1.2
* The listener is configured for mutual TLS
* The Vault instance's server certificate and private key file path are provided as well as the client CA chain that is used to validate incoming requests. It works for both Vault initialiation client and rest service requests

## Policies

Policies and policy templates are stored in the [${TOP_DIR}/volumes/${LOCAL_KME_ID}/vault/policies](../volumes/kme1/valut/policies/) directory. These dictate what permission various roles (watcher or rest role) have when interacting with the local Vault instance. These policies and policy templates are setup by the Vault initialization client service.
