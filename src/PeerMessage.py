from struct import *
import math

# message supported: keep-alive, choke, unchoke, interested, not-interested, have, bitfield, request, piece, cancel, and port. 
# each message take the form of <length-prefix><message id><payload>
#keep-alive message, no message id or payload. it should be sent every 2 minutes to prevernt peers from closing connection
def marshalKeepAlive():
	message = pack("!I", 0)
	return message

#choke message, no payload
def marshalChoke():
	message = pack("!IB", 1, 0)
	return message

#unchoke message, no payload. It means that the peer is willing to serve
def marshalUnchoke():
	message = pack("!IB", 1, 1)
	return message

#Interested mean the client would like to download from the peer
def marshalInterested():
	message = pack("!IB", 1, 2)
	return message

#NotInterested message, no payload
def marshalNotInterested():
	message = pack("!IB", 1, 3)
	return message

#Have message indicates a piece that heve been downloaded and verified
def marshalHave(pidx):
	message = pack("!IBI", 5, 4, pidx)
	return message

#bitfield message, variable payload
def marshalBitfield(pieces_num):
	bitlength = math.ceil(pieces_num/float(8))
	#TODO pack bit field
	bitfield = str(bytearray(bitlength))
	#TODO piece number read from torrent file 
	 
	length = bitlength + 1
	message = pack('!IB%ds'%bitlength, length, 5, bitfield)
	return message

#Request message, <piece-index><offset><length>

def marshalRequest(pidx, offset, length):
	message = pack("!IBIII", 13, 6, pidx, offset, length)
	return message

#piece message, variable payload
def marshalPiece(pidx, offset, block):
	block_length = len(block)
	length = block_length + 9
	message = pack('!IBII%ds'%block_length, length, 7, pidx, offset, block)
	return message

