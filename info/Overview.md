# Order of Operations

## Initialization

See [docker-compose.init.yml](../docker-compose.init.yml) and [init.sh](../scripts/init.sh) which govern the initialization behavior when a `make init` target is called from the top-level Makefile.

### certauth

* Startup certauth Docker service (`certs` and `install` Makefile targets)
* Create Local Root Certificate Authority (CA)
  * Private Key (EC secp384r1)
  * Public Key (X.509 Certificate)
* Create Local Intermediate CA
  * Private Key (EC secp384r1)
  * Certificate Signing Request (CSR)
  * Use Root CA to Sign CSR to Make Certificate
  * Create Certificate Chain
* Create Vault Server Key/Certificate
  * Private Key (EC secp384r1)
  * Generate CSR
  * Use Intermediate CA to Sign CSR to Make Certificate
  * Certificate Chain
* Create Vault Initialization Client Key/Certificate
  * Private Key (EC secp384r1)
  * Generate CSR
  * Use Intermediate CA to Sign CSR to Make Certificate
  * Certificate Chain
  * Create PKCS#12 (.p12) File Containing Private Key Plus Certificate Chain
* Certauth Docker service exits

### vault

* Start Local Docker Vault instance
  * TCP listener on port 8200
  * TLS enabled using server key/certificate generated by certauth
  * Allow clients from Vault client CA chain generated by certauth
* Local Docker Vault instance remains running until all intialization steps have completed; then it is shut down

### vault init phase 1

* Start Docker service vault_init (`--first` command-line option)
* Create Python hvac client
  * Start connection between Vault server instance and hvac client
* Initialize Vault instance
  * Generate Shamir secret shares and initial root token
* Unseal Vault instance
  * Use secret shares to decrypt/unseal the local Vault instance
  * Instance will remain unsealed until stop/restart of service or active call to seal
* Authenticate to Vault instance using root token
* Enable auditing for Vault instance; written out to audit log
* Enable authentication method that uses TLS certificates
* Enable a PKI secrets engine that will become an Intermediate CA to more conveniently issue TLS certificates
* Write out local Vault instance CSR to be signed by Root CA
* vault_init Docker service exits

### certauth csr

* Startup certauth Docker service (`csr` Makefile target)
* Sign Vault instance CSR with Root CA to create Vault Intermediate CA certificate
* Certauth Docker service exits

### vault init phase 2

* Start Docker service vault_init (`--second` command-line option)
* Create Python hvac client
* Verify Vault instance is initialized
* Unseal Vault instance
* Authenticate to Vault instance using root token
* Ingest Root CA signed certificate to become Intermediate CA
* Create Intermediate CA certificate issuer Access Control List (ACL) policy
* Enable Key Value version2 secrets engine for storing QKD key information
* Create watcher service ACL policy
* Create rest service ACL policy
* Generate watcher client private key/certificate and write to Docker volume
* Generate rest client private key/certificate and write to Docker volume
* Generate local SAE client private key/certificate and write to Docker volume
* vault_init Docker service exits

### vault client auth

* Start vault_client_auth Docker service
* This is a workaround that allows for injecting client certificates into the Vault instance cert authentication store. Ideally, this would be done with an hvac Python client in vault_init but at the time of this writing, this functionality did not exist. Therefore, a shell script is used instead.
* Authenticate to Vault instance using root token
* Inject rest client TLS certificate into cert authentication endpoint
* Inject watcher client TLS certificate into cert authentication endpoint
* This enables both clients to authenticate to the local Vault instance using their client-side certificate identities
* vault_client_auth Docker service exits

### qkd

#### Only on KME Host 1 

* Start qkd Docker service (`clean` and `ctest` Makefile targets)
* Run the `esim` binary to completion to generate simulated entangled photons and their detection and timetagging (including noise, delays, etc.) output into binary files
* Run the `chopper` and `chopper2` binaries to process the timetagged photons for both Alice and Bob -- NOTE: this is all happening locally; no `transferd` process is started
* Run the `getrate` binary on both Alice and Bob's photon stream to estimate the number of detected photons per second
* Run the `pfind` binary to determine the time offset between Alice and Bob's detected photon streams
* Run the `costream` binary to sift entangled photons by recovering coincidences between Alice and Bob
* Run the `splicer` binary to recombine information from both parties to get raw keying material
* Run the `errcd` binary to perform the Cascade error correction algorithm along with privacy amplification to generate the final key material
* Copy the final keying material to a Docker volume for further processing by other services
* qkd Docker service exits

#### Only on KME Host 2: Transfer Keys

* On this remote side, final epoch files are rsynced over from the KME host 1 and removed upon successful transfer; see [transfer_keys.sh](../scripts/transfer_keys.sh)
* No qcrypto or qsim binaries are executed

### watcher

* Start watcher Docker service
* Wait for creation of FIFO pipe and (non-blocking) open as the end reader of this pipe
* Listen for data on the pipe in the form of notifications when final epoch files are ready for consumption
* When a file notification is ready, spawn a thread to read the epoch file and send to the local Vault instance Key Value version 2 secrets engine QKEYs endpoint
  * Open and read final epoch key file
  * Parse the raw keying material
  * Create Vault secret object with Base64 encoded key, HMAC digest of key, number of bytes, and epoch number; write to Vault instance
  * Add in new epoch number into Vault instance status file to allow consumption by other services
  * Remove ingested final epoch file
* The watcher Docker service can run indefinitely but it is shut down at this stage

### notifier

* Start notifier Docker service
* Create a FIFO pipe for writing notifications to; watcher service should be on the other end waiting
* Find all final epoch files in a specific directory
* For each final epoch file; send a notification through the pipe
* notifier Docker service exits

NOTE: This service is not necessary if full QKD is setup between the two QKDEs/KMEs. qcrypto has its own set of notification pipes (-l command-line option) for both Alice and Bob that should replace this service.

NOTE: The notification pipe should be used as opposed to watching when a file is written to directory. There is a race condition between when a file is created and when it is fully written that a service like watcher could end up with material out of sync. Keying material could also be sent directly to the watcher service and/they could share memory space instead of a file transfer method.

## Running

Once both KME hosts have gone through their full initialization steps, the REST API server is ready to be started

All the below services are started together and will remain running until shut down.

### rest

* Start rest docker service
* Gunicorn Python Web Server Gateway Interface (WSGI) HTTP server is started up
* Uvicorn worker threads are spun up to receive and process incoming requests
* Each request is handled based on the validated input into the FastAPI-based REST service
* A corresponding response is generated to match each request

### vault

* The already configured Vault instance is brought back up to serve as the back end endpoint that the rest service uses to manage QKD key state

### unsealer

* This service is started solely to watch for when a Vault instance is started or restarted
* It attempts to unseal the Vault instance using the root token while the rest service only uses its own certificates

### traefik

* Start the Docker traefik service
* This container is configured to handle all HTTP/HTTPS external requests coming into the rest service
* It checks the validity of the client-side certificates and manages the authorization part of the connection