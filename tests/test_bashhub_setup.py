from bashhub import bashhub_setup
import uuid
import socket


def randomnode():
	return 1 << 40
def getnode():
	return 1

def test_get_mac_addresss():

	# Assuming uuid works
	test_mac = bashhub_setup.get_mac_address()
	assert str(uuid.getnode()) == test_mac

	# with uuid returning random
	uuid.getnode = randomnode
	hostname_mac = bashhub_setup.get_mac_address()
	assert str(abs(hash(socket.gethostname()))) == hostname_mac