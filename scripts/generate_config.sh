#!/bin/sh
# Simply copies the CONFIG and SECRETS file
if [ ! -f common/CERTAUTH_SECRETS ]; then
    cp -p common/CERTAUTH_SECRETS.example common/CERTAUTH_SECRETS
    echo "Generated 'CERTAUTH_SECRETS'."
fi
if [ ! -f common/CERTAUTH_CONFIG ]; then
    cp -p common/CERTAUTH_CONFIG.example common/CERTAUTH_CONFIG
    echo "Generated 'CERTAUTH_CONFIG'."
fi

