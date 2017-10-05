# OPENVN SCRIPTS FOR OPNSENSE
A collection of scripts to create site to site IPV6 tunnels from a
gateway with ipv4 only network
## Rationale
There are some applications for IOT that now requires IPV6 networks,
yet IPV6 is not so popular.

There are some tunnel brokers on internet, but it's very difficult to
find a reliable broker that:
- Works behind nat
- Doesn't need an IPV4 public address
- Be firewall friendly

This solution has been created to work in very difficult setup, like
hotels and conference rooms, where we have limited control on the
network.

## Opnsense
Actually any Linux or BSD can use this setup, but Opnsense provides a
nice frontend with certificates manager and monitor capabilities.

PFSense is another popular alternative, but I find Opnsense more clean

## Hosting Opnsense Gateway
Unfortunately it's not easy to find a good service who is providing
IPV6/56 network.

For more details look [IPv6 setup in two hosting providers compared:
 awful (OVH) and awesome (Online.net)](https://otacon22.com/2016/02/21/two-hosting-providers-ipv6-setups-compared-ovh-online-net/)

Choose Dedibox offering to get a full /56 address per machine.

## Installing Opnsense to online.net

## Configure IPV6 on online.net
The WAN interface need some special configuration.

The ratio is:
WAN interface need to request a prefix delegation ia-pd with a specific
ID (DUID).

The wan interface will send then a ia-nd for getting a standard address.

Unfortunately there's no possibility to set DUID from the gui and you
will need to do from console.

```shell
echo 00:03:XX:XX:... | awk '{ gsub(":"," "); printf "0: 0a 00 %s\n", $0 }' | xxd -r > dhcp6c_duid
```

Now from the web interface you need to set to interface: [WAN]
- IPv4 Configuration Type: DHCP
- IPV6 Configuration Type: DHCPv6
- DHCPV6
  - Enable **Directly Send Solicit**
  - **Send Options** (without quotes) "ia-pd 0, ia-na 0"
  - Enable **Non-Temporary Address Allocation**
    - **id-assoc na ID** 0
  - Enable **Prefix Delegation**
    - **id-assoc pd ID** 0

Now the machine should get and ipv6 address and should be able to ping
ipv6.google.com

```shell
ping6 ipv6.google.com
```

## Network setup

Here's the setup we want to achieve:
- Cloud Server (Opnsense on online.net) will act as an Openvpn Server
  - All ipv6 prefix/56 traffic is routed through openvpn
  - Openvpn server
    - Will run ipv6 on a /64 subnet (prefix:ff/64)
    - Will provide other /64 subnets to edgerouters via specifying a
        variable
  - This setup can support up to 255 edge routers out of a /56 address

- Edge Router(s)
  - Acting as openvpn client
    - Wan interface can have only IPV4 address
    - Lan interface will autoconfigure with SLAC its IPV6 address
    - Openvpn client
      - Script running on client will take a variable sent by Openvpn
        server and configure the radvd daemon
    - Radvd daemon will send router advertising to Lan configuring all
      clients on the same segment


![Alt text](/images/NetworkSetup.png?raw=true "Network Diagram")







