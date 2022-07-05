# Policy for rest service to read QKD keys

# Allow the client to read and update epoch file paths
path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["read", "update"]
}

# Allow the client to create, read, and update key ID ledger paths
path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/<<<LEDGER_ID>>>/*" {
    capabilities = ["create", "read", "update"]
}

# Allow client to read epoch file metadata paths and delete associated data
path "<<<KV_MOUNT_POINT>>>/metadata/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["read", "delete"]
}

# Allow the client to read and update epoch file paths
path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/*" {
    capabilities = ["read", "update"]
}

# Allow the client to create, read, and update key ID ledger paths
path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/<<<LEDGER_ID>>>/*" {
    capabilities = ["create", "read", "update"]
}

# Allow client to read epoch file metadata paths and delete associated data
path "<<<KV_MOUNT_POINT>>>/metadata/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/*" {
    capabilities = ["read", "delete"]
}


path "auth/token/renew" {
    capabilities = ["update"]
}

path "auth/token/renew-self" {
    capabilities = ["update"]
}
