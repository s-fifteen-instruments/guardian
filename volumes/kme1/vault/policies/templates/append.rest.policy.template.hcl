path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["read", "update"]
}

path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/<<<LEDGER_ID>>>/*" {
    capabilities = ["create", "read", "update"]
}

path "<<<KV_MOUNT_POINT>>>/metadata/<<<QKDE_ID>>>/<<<QCHANNEL_ID>>>/*" {
    capabilities = ["read", "delete"]
}

path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/*" {
    capabilities = ["read", "update"]
}

path "<<<KV_MOUNT_POINT>>>/data/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/<<<LEDGER_ID>>>/*" {
    capabilities = ["create", "read", "update"]
}

path "<<<KV_MOUNT_POINT>>>/metadata/<<<QKDE_ID>>>/<<<REV_QCHANNEL_ID>>>/*" {
    capabilities = ["read", "delete"]
}
