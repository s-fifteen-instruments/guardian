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

if [ "${1}" != "kme1" ] && [ "${1}" != "kme2" ] && [ "${1}" != "both" ]; then
  echo "Expecting \"kme1\", \"kme2\", or \"both\" as the first argument."
  echo "Received ${1}. Exiting ..."
  exit -1
fi
# Run as root
set -x

if [ "${1}" = "kme1" ] || [ "${1}" = "both" ]; then

  rm -f  ./scripts/.kme1.initialized
  rm -rf ./volumes/kme1/certificates/production/vault
  rm -rf ./volumes/kme1/certificates/production/vault_init
  rm -rf ./volumes/kme1/certificates/production/rest
  rm -rf ./volumes/kme1/certificates/production/watcher
  rm -rf ./volumes/kme1/certificates/production/sae
  rm -rf ./volumes/kme1/certificates/production/admin
  rm -rf ./volumes/kme1/certificates/generation/root
  rm -rf ./volumes/kme1/vault/data/file
  rm -f  ./volumes/kme1/vault/logs/audit.log
  rm -f  ./volumes/kme1/vault/policies/watcher.policy.hcl
  rm -f  ./volumes/kme1/vault/policies/rest.policy.hcl
  rm -rf ./volumes/kme1/qkd/epoch_files/*
  rm -rf ./volumes/kme1/qkd/digest_files/*
  # For remote client CA chain
  rm -rf ./volumes/kme2/certificates/production/rest

fi
if [ "${1}" = "kme2" ] || [ "${1}" = "both" ]; then

  rm -f  ./scripts/.kme2.initialized
  rm -rf ./volumes/kme2/certificates/production/vault
  rm -rf ./volumes/kme2/certificates/production/vault_init
  rm -rf ./volumes/kme2/certificates/production/rest
  rm -rf ./volumes/kme2/certificates/production/watcher
  rm -rf ./volumes/kme2/certificates/production/sae
  rm -rf ./volumes/kme2/certificates/production/admin
  rm -rf ./volumes/kme2/certificates/generation/root
  rm -rf ./volumes/kme2/vault/data/file
  rm -f  ./volumes/kme2/vault/logs/audit.log
  rm -f  ./volumes/kme2/vault/policies/watcher.policy.hcl
  rm -f  ./volumes/kme2/vault/policies/rest.policy.hcl
  rm -rf ./volumes/kme2/qkd/epoch_files/*
  rm -rf ./volumes/kme2/qkd/digest_files/*
  # For remote client CA chain
  rm -rf ./volumes/kme1/certificates/production/rest

fi
