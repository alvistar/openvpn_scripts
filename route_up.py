#!/usr/bin/env python3
import os
from string import Template

from subprocess import call

print("Configuring and launching RADVD")

ADDR = os.environ.get('OPENVPN_RADVD')

print("Setting RADVD prefix to {}".format(ADDR))

CONFIG = Template("""\
interface em1
{
	AdvSendAdvert on;

# This may be needed on some interfaces which are not active when
# radvd starts, but become available later on; see man page for details.

	# IgnoreIfMissing on;

#
# These settings cause advertisements to be sent every 3-10 seconds.  This
# range is good for 6to4 with a dynamic IPv4 address, but can be greatly
# increased when not using 6to4 prefixes.
#

	MinRtrAdvInterval 3;
	MaxRtrAdvInterval 10;

#
# You can use AdvDefaultPreference setting to advertise the preference of
# the router for the purposes of default router determination.
# NOTE: This feature is still being specified and is not widely supported!
#
	AdvDefaultPreference low;

#
# Disable Mobile IPv6 support
#
	AdvHomeAgentFlag off;

	prefix $ADDRESS
	{
		DeprecatePrefix on;
		AdvOnLink on;
		AdvAutonomous on;
		AdvRouterAddr off;
	};

#Passing Google DNS Servers

        RDNSS 2001:4860:4860::8888 2001:4860:4860::8844
        {
                AdvRDNSSLifetime 30;
        };

};
""").substitute(ADDRESS=ADDR)

file = open('/usr/local/etc/radvd.conf', 'w')
file.write(CONFIG)
file.close()

call(["/usr/sbin/service", "radvd", "onerestart"])

