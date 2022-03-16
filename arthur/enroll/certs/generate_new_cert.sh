#!/usr/bin/expect -f

set timeout -1

spawn ./certs.sh $1

expect "Enter pass phrase for certs/ca.key.pem:"
send -- "$1\r"

expect eof