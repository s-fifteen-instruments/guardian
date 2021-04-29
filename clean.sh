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
rm -rf ./volumes/certificates/production/vault
rm -rf ./volumes/certificates/production/vault_init
rm -rf ./volumes/certificates/production/rest
rm -rf ./volumes/certificates/production/watcher
rm -rf ./volumes/certificates/production/admin
rm -rf ./volumes/certificates/generation/root
rm -rf ./volumes/vault/data/file
rm -f  ./volumes/vault/logs/audit.log
rm -f  ./volumes/vault/policies/watcher.policy.hcl
rm -rf ./volumes/qkd/epoch_files/*
rm -rf ./volumes/qkd/digest_files/*
