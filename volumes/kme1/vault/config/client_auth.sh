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
export VAULT_ADDR="https://vault:8200/"
base_dir=/certificates
admin_dir=${base_dir}/admin
init_dir=${base_dir}/vault_init
client_delimited_str="rest watcher"
root_token=$(cat ${admin_dir}/vault/SECRETS | grep "root_token" | sed 's/"//g' | tr " 
" "\n" | tail -1)
tls_certs="-ca-cert=${init_dir}/vault.ca-chain.cert.pem \
    -client-cert=${init_dir}/vault_init.ca-chain.cert.pem \
    -client-key=${init_dir}/vault_init.key.pem"

vault login -no-print ${tls_certs} ${root_token}

set -x
for client in ${client_delimited_str}; do
    vault write ${tls_certs} auth/cert/certs/${client}_cert \
        display_name=${client}_cert \
        policies=${client} \
        certificate=@${base_dir}/${client}/${client}.ca-chain.cert.pem
done
