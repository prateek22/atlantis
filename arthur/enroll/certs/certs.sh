#!/bin/bash

# Create Server certificate signed by CA
openssl genrsa -out certs/$1.key.pem 2048

openssl req -subj "/CN=$1" -extensions v3_req -sha256 -new -key certs/$1.key.pem -out certs/$1.csr

openssl x509 -req -extensions v3_req -days 3650 -sha256 -in certs/$1.csr -CA certs/ca.pem -CAkey certs/ca.key.pem -CAcreateserial -out certs/$1.crt -extfile /usr/lib/ssl/openssl.cnf

cat certs/$1.crt certs/$1.key.pem > certs/$1-ca-full.pem

# move certificate to ca certs
sudo cp certs/$1.crt /usr/share/ca-certificates/extra/
sudo chmod -R 755 /usr/share/ca-certificates/extra/ 
sudo chmod 644 /usr/share/ca-certificates/extra/$1.crt
#sudo dpkg-reconfigure ca-certificates
sudo update-ca-trust #certificates