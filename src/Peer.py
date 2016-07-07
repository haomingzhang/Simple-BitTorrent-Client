import socket
import hashlib
import struct

def connectTo(peer):
	socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	socket.settimeout(10)
	try:
		socket.connect(peer)
	except:
		return False
	return True

def send_handshake(info_hash, peerid):
	pstr = "BitTorrent protocol"
	handshake_msg = struct.pack("!B19s8x20s20s", 19, pstr, info_hash, peerid)
	#print 'handshake len:' + str(len(handshake_msg))
	return handshake_msg

def recv_handshake(msg, info_hash):
	if(len(msg) < 68):
		return False
	handshake_msg = struct.unpack_from("!B19s8x20s20s", msg)
	print handshake_msg
	if (handshake_msg[2] != info_hash):
		print "info hash not match"
		return False
	return True
