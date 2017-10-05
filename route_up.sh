#!/bin/sh
/usr/local/openvpn_scripts/route_up.py 2>&1 |logger -t openvpn[route_up.py]
