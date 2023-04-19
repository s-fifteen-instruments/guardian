path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["create"]
}

path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/status" {
    capabilities = ["create", "read", "update"]
}

path "<<<KV_MOUNT_POINT>>>/metadata/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["read"]
}

path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/*" {
    capabilities = ["create"]
}

path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/status" {
    capabilities = ["create", "read", "update"]
}

path "<<<KV_MOUNT_POINT>>>/metadata/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/*" {
    capabilities = ["read"]
}
