#!/bin/bash

# Check if IP address is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <IP_ADDRESS>"
  exit 1
fi

# Variables
IP_ADDRESS=$1
OUTPUT_DIR="ssl"
CA_KEY="${OUTPUT_DIR}/ca.key"
CA_CERT="${OUTPUT_DIR}/ca.crt"
SERVER_KEY="${OUTPUT_DIR}/tls.key"
SERVER_CSR="${OUTPUT_DIR}/server.csr"
SERVER_CERT="${OUTPUT_DIR}/tls.crt"
CONFIG_FILE="${OUTPUT_DIR}/server.csr.cnf"
EXT_FILE="${OUTPUT_DIR}/v3.ext"
KEYSTORE="${OUTPUT_DIR}/keystore.p12"
DAYS_VALID=365
KEYSTORE_PASSWORD=""

# Create the output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Step 1: Generate the CA Key and Certificate
echo "Generating CA key and certificate..."
openssl genrsa -out $CA_KEY 2048
openssl req -x509 -new -nodes -key $CA_KEY -sha256 -days $DAYS_VALID -out $CA_CERT -subj "/C=US/ST=California/L=San Francisco/O=MyCompany/CN=MyCompany Root CA"

# Step 2: Create a Configuration File for the CSR
echo "Creating configuration file for the CSR..."
cat <<EOT > $CONFIG_FILE
[ req ]
default_bits       = 2048
prompt             = no
default_md         = sha256
req_extensions     = req_ext
distinguished_name = dn

[ dn ]
C  = US
ST = California
L  = San Francisco
O  = MyCompany
CN = $IP_ADDRESS

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
IP.1 = $IP_ADDRESS
EOT

# Step 3: Generate the Server Key and CSR
echo "Generating server key and CSR..."
openssl genrsa -out $SERVER_KEY 2048
openssl req -new -key $SERVER_KEY -out $SERVER_CSR -config $CONFIG_FILE

# Step 4: Create a Configuration File for the Certificate Extensions
echo "Creating configuration file for the certificate extensions..."
cat <<EOT > $EXT_FILE
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
IP.1 = $IP_ADDRESS
EOT

# Step 5: Sign the Server Certificate with the CA
echo "Signing the server certificate with the CA..."
openssl x509 -req -in $SERVER_CSR -CA $CA_CERT -CAkey $CA_KEY -CAcreateserial -out $SERVER_CERT -days $DAYS_VALID -sha256 -extfile $EXT_FILE

# Step 6: Verify the Certificate
echo "Verifying the certificate..."
openssl x509 -in $SERVER_CERT -text -noout

# Step 7: Create the PKCS#12 Keystore with alias ssl-cert
echo "Creating PKCS#12 keystore..."
openssl pkcs12 -export -out $KEYSTORE -inkey $SERVER_KEY -in $SERVER_CERT -certfile $CA_CERT -name ssl-cert -passout pass:$KEYSTORE_PASSWORD

# Verify all generated files
if [ -f "$CA_CERT" ] && [ -f "$SERVER_CERT" ] && [ -f "$SERVER_KEY" ] && [ -f "$KEYSTORE" ]; then
  echo "Certificates and keystore generated successfully in the '$OUTPUT_DIR' directory:"
  echo "CA Certificate: $CA_CERT"
  echo "Server Certificate: $SERVER_CERT"
  echo "Server Key: $SERVER_KEY"
  echo "Keystore: $KEYSTORE"
else
  echo "Error: Failed to generate one or more certificates or keystore."
fi
