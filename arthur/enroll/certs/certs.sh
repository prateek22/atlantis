#!/bin/bash

# Create Server certificate signed by CA
openssl genrsa -out ./enroll/certs/$1.key.pem 2048

openssl req -subj "/CN=$1" -extensions v3_req -sha256 -new -key ./enroll/certs/$1.key.pem -out ./enroll/certs/$1.csr

openssl x509 -req -extensions v3_req -days 3650 -sha256 -in ./enroll/certs/$1.csr -CA ./enroll/certs/ca.pem -CAkey ./enroll/certs/ca.key.pem -CAcreateserial -out ./enroll/certs/$1.crt -extfile /etc/pki/tls/openssl.cnf #/usr/lib/ssl/openssl.cnf

cat ./enroll/certs/$1.crt ./enroll/certs/$1.key.pem > ./enroll/certs/$1-ca-full.pem

# move certificate to ca certs
sudo cp ./enroll/certs/$1.crt /etc/pki/ca-trust/source/anchors/
sudo chmod -R 755 /etc/pki/ca-trust/source/anchors/ 
sudo chmod 644 /etc/pki/ca-trust/source/anchors/$1.crt
#sudo dpkg-reconfigure ca-certificates
sudo update-ca-trust #certificates