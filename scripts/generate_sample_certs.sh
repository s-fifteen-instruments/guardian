#!/bin/bash
# Install EasyRSA automatically if unavailable
if ! command -v ./common/easyrsa 2>&1 >/dev/null; then
    echo "easyrsa v3.2.1 will be loaded into 'common'..."
    VER="3.2.1"
    wget https://github.com/OpenVPN/easy-rsa/releases/download/v${VER}/EasyRSA-${VER}.tgz
    tar xzvf EasyRSA-${VER}.tgz
    mv EasyRSA-${VER}/easyrsa common/
    rm EasyRSA-${VER}.tgz
fi

echo "Generating certificates..."
cd common
./easyrsa init-pki >/dev/null
./easyrsa build-ca >/dev/null
echo "Copying CA certificates..."
cp -p pki/private/ca.key ./kme-ca.key.pem
cp -p pki/ca.crt ./kme-ca.cert.pem
cp -p pki/ca.crt ./full-chain.cert.pem
echo "Replaced: common/{kme-ca.key,kme-ca.cert,full-chain.cert}.pem"
if [ -f CERTAUTH_SECRETS ]; then
    sed -i "s/.*ROOT_CA_PASSWORD.*/export ROOT_CA_PASSWORD=/g" CERTAUTH_SECRETS
    echo "Updated 'CERTAUTH_SECRETS' password."
fi
echo ""
echo "Warning: Root self-signed CA certificate without private key passphrase"
echo "         has been generated for ease of testing 'guardian'. For your"
echo "         safety, this certificate is set to expire in 30 days."
echo ""
echo "Please bootstrap your own intermediate CA in production."

