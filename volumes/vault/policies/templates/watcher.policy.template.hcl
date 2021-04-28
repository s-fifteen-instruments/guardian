# Policy for watcher service to inject new QKD keys

path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["create"]
}

# Allow client to read secret versioning information
path "<<<KV_MOUNT_POINT>>>/metadata/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["read"]
}

path "auth/token/renew" {
    capabilities = ["update"]
}

path "auth/token/renew-self" {
    capabilities = ["update"]
}
