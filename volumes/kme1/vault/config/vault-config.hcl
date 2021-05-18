ui = true
log_level = "Debug"
default_lease_ttl = "1h"
max_lease_ttl = "6h"
api_addr = "https://127.0.0.1:8200"
storage "file" {
  path = "/vault/data/file"
}
listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = false
  tls_min_version = "tls12"
  tls_prefer_server_cipher_suites = true
  tls_require_and_verify_client_cert = true
  tls_cert_file = "/certificates/vault/vault.ca-chain.cert.pem"
  tls_key_file = "/certificates/vault/vault.key.pem"
  tls_client_ca_file = "/certificates/vault/vault_init.ca-chain.cert.pem"
}
