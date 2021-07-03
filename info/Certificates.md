# Certificates

Each KME host goes through a similiar process outlined below for creating private keys and certificates for authentication.

## Certauth

* Root Certificate Authority (CA)
  * Private Key (EC secp384r1)
  * Public Key (X.509 Certificate)
* Intermediate CA
  * Private Key (EC secp384r1)
  * Certificate Signing Request (CSR)
  * Use Root CA to Sign CSR to Make Certificate
  * Create Certificate Chain
* Vault Server
  * Private Key (EC secp384r1)
  * CSR
  * Use Intermediate CA to Sign CSR to Make Certificate
  * Certificate Chain
* Vault Initialization Client
  * Private Key (EC secp384r1)
  * CSR
  * Use Intermediate CA to Sign CSR to Make Certificate
  * Certificate Chain
  * Create PKCS#12 (.p12) File Containing Private Key Plus Certificate Chain

## Vault via Vault Initialization Client

* Enable PKI Secrets Engine
* Generate Private Key
* Generate Intermediate CA CSR
* Use Root CA to Sign CSR
* Ingest Certificate
* Generate `watcher` and `rest` Client Certificate/Private Key/PKCS#12 Bundles Plus Vault Access Policies
* Generate local SAE Client Certificte/Private Key/PKCS#12 Bundle
