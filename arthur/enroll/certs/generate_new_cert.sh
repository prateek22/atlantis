#!/usr/bin/expect -f

set timeout -1

set domain [lindex $argv 0];

spawn ./certs/certs.sh $domain

expect "Enter pass phrase for certs/ca.key.pem:"
send -- "seceon\r"

expect eof
