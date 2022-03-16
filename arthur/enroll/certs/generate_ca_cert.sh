#!/usr/bin/expect -f

set timeout -1

spawn ./certs/ca_cert.sh

expect "Enter pass phrase for certs/ca.key.pem:"
send -- "seceon\r"

expect "Verifying - Enter pass phrase for certs/ca.key.pem:"
send -- "seceon\r"

expect "Enter pass phrase for certs/ca.key.pem:"
send -- "seceon\r"

expect eof
