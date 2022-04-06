#!/usr/bin/expect -f

set timeout -1

set domain [lindex $argv 0];

spawn ./enroll/certs/certs.sh $domain

expect "Enter pass phrase for ./enroll/certs/ca.key.pem:"
send -- "seceon\r"

expect eof
