# Allow the client to read and update epoch file paths
path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["read", "update"]
}

# Allow client to read epoch file metadata paths and delete associated data
path "<<<KV_MOUNT_POINT>>>/metadata/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["read", "delete"]
}

# Allow the client to read and update epoch file paths
path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/*" {
    capabilities = ["read", "update"]
}

# Allow client to read epoch file metadata paths and delete associated data
path "<<<KV_MOUNT_POINT>>>/metadata/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/*" {
    capabilities = ["read", "delete"]
}
