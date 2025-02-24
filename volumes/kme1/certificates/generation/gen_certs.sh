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
# 
# Create a root certificate authority private key and certificate.
# Create an intermediate certificate authority private key, certificate
# signing request, and resulting root CA signed ceritifcate.
# Create a Hashicorp Vault server private key and certificate for use
# in TLS communications.
# Create a Vault initial client private key and certificate to perform
# mutual TLS with the Vault server.
#
# Starting point:
# https://jamielinux.com/docs/openssl-certificate-authority/index.html

# Filepath must match docker-compose SECRETS volume mount point
export SECRETS_FILEPATH=/SECRETS
if [ ! -f "${SECRETS_FILEPATH}" ]; then
  echo -e "\n\n"
  echo "================================================"
  echo "================================================"
  echo "'${SECRETS_FILEPATH}' file is not mounted."
  echo "Please follow README instructions for proper initialization."
  echo "Exiting without certificate generation."
  echo "================================================"
  echo "================================================"
  echo -e "\n\n"
  exit -1
else
  echo "Sourcing ${SECRETS_FILEPATH}"
  source ${SECRETS_FILEPATH}
fi

# Filepath must match docker-compose CONFIG volume mount point
export CONFIG_FILEPATH=/CONFIG
if [ ! -f "${SECRETS_FILEPATH}" ]; then
  echo -e "\n\n"
  echo "================================================"
  echo "================================================"
  echo "'${CONFG_FILEPATH}' file is not mounted."
  echo "Please follow README instructions for proper initialization."
  echo "Exiting without certificate generation."
  echo "================================================"
  echo "================================================"
  echo -e "\n\n"
  exit -1
else
  echo "Sourcing ${CONFG_FILEPATH}"
  source ${CONFIG_FILEPATH}
fi

set -ex

export base_dir=`pwd`
# Location for production certificates and keys
export PRODUCTION_DIR=${base_dir}/../production
# root CA directory
export ca_dir=${base_dir}/root/ca
# intermediate CA directory
export int_ca_dir=${ca_dir}/intermediate
# Certificates
export guardian_root_key=/kme-ca.key.pem
export guardian_root_cert=/kme-ca.cert.pem
export guardian_root_chain=/full-chain.cert.pem

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

# Only invoke root certificate generation if in CAGEN mode
if [ "${ACTION}" == "CAGEN" ]; then

# Only invoke certificate generation if
# root CA dir does NOT already exist
#if [ -d "${ca_dir}" ]; then
#  set +x
#  echo -e "\n\n"
#  echo "================================================"
#  echo "================================================"
#  echo "Root CA directory already exists..."
#  echo "To preserve the root and intermediate CA,"
#  echo "all subsequent generation actions are skipped."
#  echo "Issue a 'make clean' if you truly wish to remove"
#  echo "the root and intermediate CAs."
#  echo "================================================"
#  echo "================================================"
#  echo -e "\n\n"
#  exit 0
#fi

# Create root Certificate Authority directory and configuration
mkdir -p ${ca_dir}
cd ${ca_dir}
mkdir -p certs crl newcerts private
chmod 0700 private
touch index.txt
if [ ! -f serial ]; then
	echo 1000 > serial
fi
cp -a ${base_dir}/openssl.root.cnf.template ${ca_dir}/openssl.cnf
sed -i "s#<<<BASE_DIRECTORY>>>#${base_dir}#g" ${ca_dir}/openssl.cnf

# Copy the guardian root CA private key and full-chain
# TODO: Consider populating serial/index for more robust CRL
cd ${ca_dir}
cp ${guardian_root_key} private/ca.key.pem
chmod 0400 private/ca.key.pem
cp ${guardian_root_cert} certs/ca.cert.pem
chmod 0444 certs/ca.cert.pem
cp ${guardian_root_chain} certs/ca-chain.cert.pem
chmod 0444 certs/ca-chain.cert.pem

#-----------------------------------------------------------------------------

# Create intermediate Certificate Authority directory and configuration
mkdir -p ${int_ca_dir}
cd ${int_ca_dir}
mkdir -p certs crl csr newcerts private
chmod 0700 private
touch index.txt
echo 1000 > serial
echo 1000 > crlnumber
cp -a ${base_dir}/openssl.intermediate.cnf.template ${int_ca_dir}/openssl.cnf
sed -i "s#<<<BASE_DIRECTORY>>>#${base_dir}#g" ${int_ca_dir}/openssl.cnf
sed -i "s#<<<COUNTRY_CODE>>>#${INT_CA_COUNTRY_CODE}#g" ${int_ca_dir}/openssl.cnf
sed -i "s#<<<STATE>>>#${INT_CA_STATE}#g" ${int_ca_dir}/openssl.cnf
sed -i "s#<<<LOCALITY>>>#${INT_CA_LOCALITY}#g" ${int_ca_dir}/openssl.cnf
sed -i "s#<<<ORGANIZATION>>>#${INT_CA_ORGANIZATION}#g" ${int_ca_dir}/openssl.cnf
sed -i "s#<<<UNTI>>>#${INT_CA_UNIT}#g" ${int_ca_dir}/openssl.cnf
sed -i "s#<<<COMMON_NAME>>>#${INT_CA_COMMON_NAME}#g" ${int_ca_dir}/openssl.cnf
sed -i "s#<<<EMAIL>>>#${INT_CA_EMAIL}#g" ${int_ca_dir}/openssl.cnf
# Substitute " qqq" as dummy placeholder to allow multi-line sed
export ALT_NAMES=$(echo "${ALT_NAMES}" | sed "s#\$# qqq#g")
sed -i "s/<<<ALT_NAMES>>>/$(echo ${ALT_NAMES})/g;s/ qqq/\n/g" ${int_ca_dir}/openssl.cnf

# Create the intermediate CA private key "intermediate.key.pem"
cd ${ca_dir}
openssl genpkey \
    -algorithm EC \
    -pkeyopt ec_paramgen_curve:${EC_NAME} \
    -pkeyopt ec_param_enc:named_curve \
    -aes256 \
    -pass stdin \
    -out intermediate/private/intermediate.key.pem \
    <<INTCA
${INT_CA_PASSWORD}
${INT_CA_PASSWORD}
INTCA
chmod 0400 intermediate/private/intermediate.key.pem

# Create the intermediate CA certificate signing request "intermediate.csr.pem"
# Leave vertical spaces; they are important input
openssl req -config intermediate/openssl.cnf -new -sha256 \
    -key intermediate/private/intermediate.key.pem \
    -out intermediate/csr/intermediate.csr.pem \
    -passin stdin <<INTCA
${INT_CA_PASSWORD}







INTCA

#With the CSR, use root CA to create intermediate CA certificate "intermediate.cert.pem"
openssl ca -config openssl.cnf -extensions v3_intermediate_ca \
    -days 3650 -notext -md sha256 \
    -in intermediate/csr/intermediate.csr.pem \
    -out intermediate/certs/intermediate.cert.pem \
    -passin stdin << INTCA
${ROOT_CA_PASSWORD}
y
y
INTCA
chmod 0444 intermediate/certs/intermediate.cert.pem

# Inspect and verify the intermediate CA certificate
openssl x509 -noout -text \
    -in intermediate/certs/intermediate.cert.pem
openssl verify -CAfile certs/ca-chain.cert.pem \
    intermediate/certs/intermediate.cert.pem
# Create the CA certificate chain file
cat intermediate/certs/intermediate.cert.pem \
    certs/ca-chain.cert.pem > intermediate/certs/ca-chain.cert.pem
chmod 0444 intermediate/certs/ca-chain.cert.pem

#------------------------------------------------------------------------------

# Create a VAULT server private key
cd ${ca_dir}
# Input to use if the server key has a password set
#openssl genpkey \
#    -algorithm EC \
#    -pkeyopt ec_paramgen_curve:${EC_NAME} \
#    -pkeyopt ec_param_enc:named_curve \
#    -aes256 \
#    -pass stdin \
#    -out intermediate/private/${VAULT_SERVER_FQDN}.key.pem 
#    <<VAULTSERVERKEY
#${VAULT_SERVER_KEY_PASSWORD}
#${VAULT_SERVER_KEY_PASSWORD}
#VAULTSERVERKEY
openssl genpkey \
    -algorithm EC \
    -pkeyopt ec_paramgen_curve:${EC_NAME} \
    -pkeyopt ec_param_enc:named_curve \
    -out intermediate/private/${VAULT_SERVER_FQDN}.key.pem
chmod 0400 intermediate/private/${VAULT_SERVER_FQDN}.key.pem

# Create a VAULT server CSR for the intermediate CA to sign
cd ${ca_dir}
openssl req -config intermediate/openssl.cnf \
    -key intermediate/private/${VAULT_SERVER_FQDN}.key.pem \
    -new -sha256 -out intermediate/csr/${VAULT_SERVER_FQDN}.csr.pem \
    -passin stdin << VAULTSERVERCERT
${VAULT_SERVER_KEY_PASSWORD}





${VAULT_SERVER_FQDN}

VAULTSERVERCERT

# Use intermediate CA to sign VAULT CSR; note "server_cert" extension
openssl ca -config intermediate/openssl.cnf \
    -extensions server_cert \
    -days 375 -notext -md sha256 \
    -in intermediate/csr/${VAULT_SERVER_FQDN}.csr.pem \
    -out intermediate/certs/${VAULT_SERVER_FQDN}.cert.pem \
    -passin stdin << INTCA
${INT_CA_PASSWORD}
y
y
INTCA
chmod 0444 intermediate/certs/${VAULT_SERVER_FQDN}.cert.pem

# Inspect and verify the VAULT server certificate
openssl x509 -noout -text \
    -in intermediate/certs/${VAULT_SERVER_FQDN}.cert.pem
openssl verify -CAfile intermediate/certs/ca-chain.cert.pem \
      intermediate/certs/${VAULT_SERVER_FQDN}.cert.pem

# Create the full certificate chain file
cat intermediate/certs/${VAULT_SERVER_FQDN}.cert.pem \
    intermediate/certs/intermediate.cert.pem \
    certs/ca-chain.cert.pem > intermediate/certs/${VAULT_SERVER_FQDN}.ca-chain.cert.pem
chmod 0444 intermediate/certs/${VAULT_SERVER_FQDN}.ca-chain.cert.pem

#------------------------------------------------------------------------------

# Create an VAULT_INIT client key
cd ${ca_dir}
# Input to use if the client key has a password set
#openssl genpkey \
#    -algorithm EC \
#    -pkeyopt ec_paramgen_curve:${EC_NAME} \
#    -pkeyopt ec_param_enc:named_curve \
#    -aes256 \
#    -pass stdin \
#    -out intermediate/private/${VAULT_INIT_CLIENT_NAME}.key.pem \
#    <<VAULT_INITCLIENTKEY
#${VAULT_INIT_CLIENT_KEY_PASSWORD}
#${VAULT_INIT_CLIENT_KEY_PASSWORD}
#VAULT_INITCLIENTKEY
openssl genpkey \
    -algorithm EC \
    -pkeyopt ec_paramgen_curve:${EC_NAME} \
    -pkeyopt ec_param_enc:named_curve \
    -out intermediate/private/${VAULT_INIT_CLIENT_NAME}.key.pem
chmod 0400 intermediate/private/${VAULT_INIT_CLIENT_NAME}.key.pem

# Create a VAULT_INIT client CSR for the intermediate CA to sign
cd ${ca_dir}
openssl req -config intermediate/openssl.cnf \
    -key intermediate/private/${VAULT_INIT_CLIENT_NAME}.key.pem \
    -new -sha256 -out intermediate/csr/${VAULT_INIT_CLIENT_NAME}.csr.pem \
    -passin stdin << VAULT_INITCLIENTCERT
${VAULT_INIT_CLIENT_KEY_PASSWORD}





${VAULT_INIT_CLIENT_NAME}

VAULT_INITCLIENTCERT

# Use intermediate CA to sign VAULT_INIT CSR; note "user_cert" extension
openssl ca -config intermediate/openssl.cnf \
    -extensions usr_cert \
    -days 375 -notext -md sha256 \
    -in intermediate/csr/${VAULT_INIT_CLIENT_NAME}.csr.pem \
    -out intermediate/certs/${VAULT_INIT_CLIENT_NAME}.cert.pem \
    -passin stdin << INTCA
${INT_CA_PASSWORD}
y
y
INTCA
chmod 0444 intermediate/certs/${VAULT_INIT_CLIENT_NAME}.cert.pem

# Inspect and verify the VAULT_INIT client certificate
openssl x509 -noout -text \
    -in intermediate/certs/${VAULT_INIT_CLIENT_NAME}.cert.pem
openssl verify -CAfile intermediate/certs/ca-chain.cert.pem \
      intermediate/certs/${VAULT_INIT_CLIENT_NAME}.cert.pem

# Create the full certificate chain file
cat intermediate/certs/${VAULT_INIT_CLIENT_NAME}.cert.pem \
    intermediate/certs/intermediate.cert.pem \
    certs/ca-chain.cert.pem > intermediate/certs/${VAULT_INIT_CLIENT_NAME}.ca-chain.cert.pem
chmod 0444 intermediate/certs/${VAULT_INIT_CLIENT_NAME}.ca-chain.cert.pem

# Bundle the VAULT_INIT client certificate and key into PKCS#12 format for browsers
openssl pkcs12 -export \
    -in intermediate/certs/${VAULT_INIT_CLIENT_NAME}.ca-chain.cert.pem \
    -inkey intermediate/private/${VAULT_INIT_CLIENT_NAME}.key.pem \
    -out intermediate/private/${LOCAL_KME_ID}${VAULT_INIT_CLIENT_NAME}.p12 \
    -passout stdin << VAULT_INITCLIENTP12


VAULT_INITCLIENTP12
chmod 0400 intermediate/private/${LOCAL_KME_ID}${VAULT_INIT_CLIENT_NAME}.p12

exit 0

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

# Only invoke certificate generation if in CSR mode
elif [ "${ACTION}" == "CSR" ]; then


cd ${ca_dir}
cp --archive \
    ${PRODUCTION_DIR}/${VAULT_INIT_CLIENT_NAME}/${VAULT_PKI_INT}.csr.pem \
    intermediate/csr

#With the CSR, use root CA to create Vault intermediate CA certificate
openssl ca -config openssl.cnf -extensions v3_intermediate_ca \
    -days 3650 -notext -md sha256 \
    -in intermediate/csr/${VAULT_PKI_INT}.csr.pem \
    -out intermediate/certs/${VAULT_PKI_INT}.cert.pem \
    -passin stdin << INTCA
${ROOT_CA_PASSWORD}
y
y
INTCA
chmod 0444 intermediate/certs/${VAULT_PKI_INT}.cert.pem

# Inspect and verify the intermediate CA certificate
openssl x509 -noout -text \
    -in intermediate/certs/${VAULT_PKI_INT}.cert.pem
openssl verify -CAfile certs/ca-chain.cert.pem \
    intermediate/certs/${VAULT_PKI_INT}.cert.pem
# Create the CA certificate chain file
cat intermediate/certs/${VAULT_PKI_INT}.cert.pem \
    certs/ca-chain.cert.pem > intermediate/certs/${VAULT_PKI_INT}.ca-chain.cert.pem
chmod 0444 intermediate/certs/${VAULT_PKI_INT}.ca-chain.cert.pem

cp --archive \
    intermediate/certs/${VAULT_PKI_INT}.ca-chain.cert.pem \
    ${PRODUCTION_DIR}/${VAULT_INIT_CLIENT_NAME}/


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

# Only copy certificates into production if in INSTALL mode
elif [ "${ACTION}" == "INSTALL" ]; then


mkdir -p ${PRODUCTION_DIR}/${VAULT_SERVER_FQDN}
mkdir -p ${PRODUCTION_DIR}/${VAULT_INIT_CLIENT_NAME}
mkdir -p ${PRODUCTION_DIR}/admin
cd ${ca_dir}
cp --archive \
    intermediate/private/${VAULT_SERVER_FQDN}.key.pem \
    intermediate/certs/${VAULT_SERVER_FQDN}.ca-chain.cert.pem \
    intermediate/certs/${VAULT_INIT_CLIENT_NAME}.ca-chain.cert.pem \
    ${PRODUCTION_DIR}/${VAULT_SERVER_FQDN}
chown -R vault:vault ${PRODUCTION_DIR}/${VAULT_SERVER_FQDN}
cp --archive \
    intermediate/private/${VAULT_INIT_CLIENT_NAME}.key.pem \
    intermediate/private/${LOCAL_KME_ID}${VAULT_INIT_CLIENT_NAME}.p12 \
    intermediate/certs/${VAULT_INIT_CLIENT_NAME}.ca-chain.cert.pem \
    intermediate/certs/${VAULT_SERVER_FQDN}.ca-chain.cert.pem \
    ${PRODUCTION_DIR}/${VAULT_INIT_CLIENT_NAME}
chown -R vaultinit:vault ${PRODUCTION_DIR}/${VAULT_INIT_CLIENT_NAME}
cp --archive \
    ${PRODUCTION_DIR}/${VAULT_SERVER_FQDN} \
    ${PRODUCTION_DIR}/${VAULT_INIT_CLIENT_NAME} \
    ${PRODUCTION_DIR}/admin
chown -R root:root ${PRODUCTION_DIR}/admin
chmod -R 0444 ${PRODUCTION_DIR}/admin/${VAULT_SERVER_FQDN}/*
chmod -R 0444 ${PRODUCTION_DIR}/admin/${VAULT_INIT_CLIENT_NAME}/*
touch ${PRODUCTION_DIR}/admin/${VAULT_SERVER_FQDN}/SECRETS
chmod -R 0666 ${PRODUCTION_DIR}/admin/${VAULT_SERVER_FQDN}/SECRETS

exit 0

fi
