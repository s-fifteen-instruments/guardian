# Policy for rest service to read QKD keys

# Allow the client to create, read, and update key ID ledger paths
path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/<<<LEDGER_ID>>>/*" {
    capabilities = ["create", "read", "update"]
}

path "auth/token/renew" {
    capabilities = ["update"]
}

path "auth/token/renew-self" {
    capabilities = ["update"]
}
