#!/bin/sh
/usr/local/openvpn_scripts/client_connect.py $1 $2 $3 2>&1 |logger -t openvpn[client-connect]
