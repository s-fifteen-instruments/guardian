#!/bin/sh

# Run as root
set -x
rm -rf ./volumes/certificates/production/vault
rm -rf ./volumes/certificates/production/vault_init
rm -rf ./volumes/certificates/production/admin
rm -rf ./volumes/certificates/generation/root
rm -rf ./volumes/vault/data/file
rm -rf ./volumes/vault/logs/audit.log
rm -rf ./volumes/qkd/epoch_files/*
