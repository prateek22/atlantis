#!/usr/bin/expect -f

set timeout -1

set domain [lindex $argv 0];

spawn ./certs/certs.sh $domain

expect "Enter pass phrase for certs/ca.key.pem:"
<<<<<<< Updated upstream
send -- "seceon\r"
=======
send "seceon\r"
>>>>>>> Stashed changes

expect eof
