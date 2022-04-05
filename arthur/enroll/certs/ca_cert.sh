#!/bin/bash

mkdir certs

# Create CA certificate
openssl genrsa -aes256 -out certs/ca.key.pem 2048

# gen key
openssl req -new -x509 -subj "/CN=edrapi" -extensions v3_ca -days 3650 -key certs/ca.key.pem -sha256 -out certs/ca.pem -config /etc/pki/tls/openssl.cnf