#!/usr/bin/expect -f

set timeout -1

set domain [lindex $argv 0];

spawn ./certs.sh $domain

expect "Enter pass phrase for certs/ca.key.pem:"
send -- "$1\r"

expect eof