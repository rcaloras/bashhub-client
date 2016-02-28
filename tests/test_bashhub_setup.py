from bashhub import bashhub_setup
import ConfigParser
import os

def test_write_to_config_file(tmpdir):
  bashhub_setup.BH_HOME = tmpdir.mkdir('.bashhub').strpath
  bashhub_setup.write_to_config_file("access_token", 'some-auth-token')
  config = ConfigParser.ConfigParser()
  config.read(bashhub_setup.BH_HOME + '/config')
  assert config.get('bashhub', 'access_token') == 'some-auth-token'

