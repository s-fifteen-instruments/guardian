#!/bin/sh
#
# Guardian is a quantum key distribution REST API and supporting software stack.
# Copyright (C) 2021  W. Cyrus Proctor
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# Run as root
set -x

rm -f  ./scripts/.kme.initialized
sudo rm -rf ./volumes/${LOCAL_KME_ID}/certificates/production/vault
sudo rm -rf ./volumes/${LOCAL_KME_ID}/certificates/production/vault_init
sudo rm -rf ./volumes/${LOCAL_KME_ID}/certificates/production/rest
sudo rm -rf ./volumes/${LOCAL_KME_ID}/certificates/production/watcher
sudo rm -rf ./volumes/${LOCAL_KME_ID}/certificates/production/sae1
sudo rm -rf ./volumes/${LOCAL_KME_ID}/certificates/production/admin
sudo rm -rf ./volumes/${LOCAL_KME_ID}/certificates/generation/root
sudo rm -rf ./volumes/${LOCAL_KME_ID}/vault/data/file
sudo rm -f  ./volumes/${LOCAL_KME_ID}/vault/logs/audit.log
sudo rm -f  ./volumes/${LOCAL_KME_ID}/vault/policies/watcher.policy.hcl
sudo rm -f  ./volumes/${LOCAL_KME_ID}/vault/policies/rest.policy.hcl
sudo rm -rf ./volumes/${LOCAL_KME_ID}/qkd/epoch_files/*
sudo rm -rf ./volumes/${LOCAL_KME_ID}/qkd/digest_files/*
sudo rm -f  ./volumes/${LOCAL_KME_ID}/traefik/logs/access.log
# For remote client CA chain
rm -rf ./volumes/${REMOTE_KME_ID}/certificates/production/rest
