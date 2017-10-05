#!/usr/bin/env python3

import ipaddress
import os
import warnings
import sys

from textwrap import dedent
import ruamel
from ruamel.yaml import YAML
from pykwalify.core import Core


class Leases:
    FOLDER = sys.path[0]
    LEASES_FILE = os.path.join(FOLDER, 'leases.yaml')
    SCHEMA = os.path.join(FOLDER, 'schema.yaml')

    def __init__(self):
        self.config = None
        self.yaml = YAML()
        self.read_config()
        self.supernet = ipaddress.IPv6Network(self.config['supernet'])

        self.start_subnet = ipaddress.IPv6Network(self.config['start_subnet']) if self.config[
                                                                                      'start_subnet'] is not None else next(
            self.supernet.subnets(new_prefix=64))

        self.available_subnets = {k: None for k in self.supernet.subnets(new_prefix=64) if k >= self.start_subnet}
        tmp = {ipaddress.IPv6Network(k): v for v, k in self.config['clients'].items()}
        self.available_subnets = {**self.available_subnets, **tmp}

    def init_config(self):
        self.config = {'next': 1, 'clients': {}, 'prefix': ''}

    def read_config(self):
        try:
            stream = open(Leases.LEASES_FILE, 'r')
            self.config = self.yaml.load(stream)
            warnings.simplefilter('ignore',
                                  ruamel.yaml.error.UnsafeLoaderWarning)
            core = Core(
                source_file=Leases.LEASES_FILE, schema_files=[Leases.SCHEMA])
            core.validate(raise_exception=True)

        except IOError:
            pass

        if self.config is None:
            self.init_config()
            self.write_config()

    def write_config(self):
        stream = open(Leases.LEASES_FILE, 'w')
        self.yaml.default_flow_style = False
        self.yaml.dump(self.config, stream)
        stream.close()

    def get_subnet(self, client):
        """ Return address """

        address = self.config['clients'].get(client)

        if address is None:
            sorted_keys = sorted(self.available_subnets.keys())
            address = next(k for k in sorted_keys if self.available_subnets[k] is None)

            print(address)
            self.config['clients'][client] = str(address)
        return address

    def save_file(self, address, filename):
        output = """\
      iroute-ipv6 {0}
      push "setenv-safe RADVD {0}"
    """.format(address)

        stream = open(filename, 'w')
        stream.write(dedent(output))
        stream.close()


print('Invoked client_connect with {}'.format(str(sys.argv)))

CLIENT = os.environ.get('common_name')
FILE = sys.argv[1]

print('Client common name {}'.format(CLIENT))

L = Leases()
ADDRESS = L.get_subnet(CLIENT)
L.save_file(ADDRESS, FILE)
L.write_config()
