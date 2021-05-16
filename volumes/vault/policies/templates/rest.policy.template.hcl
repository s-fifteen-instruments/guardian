# Policy for rest service to read QKD keys

# Allow the client to read keys (no update)
path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["read", "update"]
}

# Allow client to read list epoch file paths and delete associated data
path "<<<KV_MOUNT_POINT>>>/metadata/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["delete"]
}

path "auth/token/renew" {
    capabilities = ["update"]
}

path "auth/token/renew-self" {
    capabilities = ["update"]
}
