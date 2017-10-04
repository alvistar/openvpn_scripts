#!/usr/bin/env python3

import warnings
import sys
from textwrap import dedent
import ruamel
from ruamel.yaml import YAML
from pykwalify.core import Core

class Leases():
  LEASES_FILE = 'leases.yaml'
  SCHEMA = 'schema.yaml'

  def __init__(self):
    self.config = None
    self.yaml = YAML()
    self.read_config()

  def init_config(self):
    self.config = {
      'next':1,
      'clients': {},
      'prefix': ''
    }

  def read_config(self):
    try:
      stream = open(Leases.LEASES_FILE, 'r')
      self.config = self.yaml.load(stream)
      warnings.simplefilter('ignore', ruamel.yaml.error.UnsafeLoaderWarning)
      core = Core(source_file=Leases.LEASES_FILE, schema_files=[Leases.SCHEMA])
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

  def get_address(self, client):
    """ Return address """
    address = None

    try:
      address = self.config['clients'].get(client)
    except KeyError:
      self.config['clients']={}

    if address is None:
      address = "{0}{1:02x}".format(self.config['prefix'], self.config['next'])
      self.config['clients'][client] = address
      self.config['next'] = self.config['next']+1
    return address

  def save_file(self, address, filename):
    output = """\
    iroute-ipv6 {0}::/64
    ifconfig-ipv6-push {0}::1/128
    """.format(address)

    stream = open(filename, 'w')
    stream.write(dedent(output))
    stream.close()

CLIENT = sys.argv[1]
IP = sys.argv[2]
FILE = sys.argv[3]

L = Leases()
ADDRESS = L.get_address(CLIENT)
L.save_file(ADDRESS, FILE)
L.write_config()
