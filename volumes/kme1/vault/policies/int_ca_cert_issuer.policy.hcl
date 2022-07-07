# Policy for intermediate CA certificate issuer

path "pki_int/*" {
    capabilities = ["list", "read"]
}

path "pki_int/ca" {
    capabilities = ["create", "update"]
}

path "pki_int/certs" {
    capabilities = ["list"]
}

path "pki_int/revoke" {
    capabilities = ["create", "update"]
}

path "pki_int/tidy" {
    capabilities = ["create", "update"]
}

path "auth/token/renew" {
    capabilities = ["update"]
}

path "auth/token/renew-self" {
    capabilities = ["update"]
}

path "auth/userpass/users/qkd_controller/password" {
  capabilities = [ "update" ]
  allowed_parameters = {
    "password" = []
  }
}
