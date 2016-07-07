#!/usr/bin/python
import bencode
import hashlib
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
import Peer
import struct
import PeerMessage
import sys

BUFFER_SIZE = 4096
# twisted framework
class BitTorrent(Protocol):
	def __init__(self, torrent, addr, info_hash):
		self.torrent = torrent
		self.pieces_num = len(torrent['info']['pieces'])/20
		self.info_hash = info_hash
		self.peerid = 'clienthaomingzyduan1'
		self.interested = False
		self.choked = True
		self.recv_buf = ""
		self.peer_interested = False
		self.addr = addr
		self.has_handshake = False
		self.bitfield = bytearray()
		self.data_buffer = bytearray(BUFFER_SIZE)
		self.offset = 0
	def connectionMade(self):
		print 'MADE: '+ str(self.addr.host)
		#handshake 
		self.transport.write(Peer.send_handshake(self.info_hash, self.peerid))
		self.factory = self.transport.connector.factory

	def dataReceived(self, data):
		print str(len(data)) + " bytes data received from " + str(self.addr.host)
		self.data_buffer[self.offset:(self.offset+len(data))] = data
		self.offset += len(data)
		for i in range(self.offset):
			for j in hex(self.data_buffer[i]):
				sys.stdout.write(j)
		print ''
		if (not self.has_handshake) and (self.offset>=68):
			# handshake
			self.extractHandshake()
		elif self.has_handshake:
			self.unmarshalCompleteMsg()
		# unmarshal message
		#self.unmarshalCompleteMsg(completeMsg)


	def unmarshalCompleteMsg(self):
		if self.has_handshake:
			begin = 0
			buff = buffer(self.data_buffer)
			#print  str(self.addr) + ' offset ' +  str(self.offset)
			while (self.offset-begin >= 4):
				print  str(self.addr) + ' offset ' +  str(self.offset)
				length = int(struct.unpack_from("!I", buff, offset=begin)[0])
				print  str(self.addr) + ' length ' +  str(length)
				if length < 1:
					print "keep-alive from" + str(self.addr)
				elif begin+4+length>self.offset:
					#incompleted message
					break
				else:
					msgid = int(struct.unpack_from("!B", buff, offset=begin+4)[0])
					if msgid == 0:
						print "choke " + str(self.addr)
						self.choked = True
					elif msgid == 1:
						print "unchoke " + str(self.addr)
						self.choked = False
					elif msgid == 2:
						print "interested " + str(self.addr)
						self.peer_interested = True
					elif msgid == 3:
						print "notinterested " + str(self.addr)
						self.peer_interested = False
					elif msgid == 4:
						piece = int(struct.unpack_from("!I", buff, offset=begin+5)[0])
						print str(self.addr) + " have " + str(piece)
						self.bitfield[piece/8] = self.bitfield[piece/8] | (1<<(7-(piece%8)))
					elif msgid == 5:
						print "bitfield " + str(self.addr)
						self.bitfield = self.data_buffer[(begin+5):(begin+4+length)]
					elif msgid == 6:
						print "request " + str(self.addr)
					elif msgid == 7:
						print "piece " + str(self.addr)

					begin += length+4
			if begin == self.offset:
				#has consumed all buffered data
				self.offset = 0
			else:
				#copy the unconsumed data to the front of the buffer
				left_len = self.offset-begin
				self.data_buffer[0:left_len] = self.data_buffer[begin:self.offset]
				self.offset = left_len
		else:
			print 'ERROR IN unmarshalCompleteMsg() ' + str(self.offset) + ' ' + str(self.begin)


	def disconnetFromPeer(self):
		self.transport.loseConnection()

	def extractHandshake(self):
		if (not self.has_handshake) and (self.offset>=68):
			data = str(self.data_buffer[0:68])
			if(Peer.recv_handshake(data, self.info_hash)):
				print 'HANDSHAKE:' + str(self.addr)
				self.transport.write(PeerMessage.marshalInterested())
				self.interested = True
				#self.transport.write(PeerMessage.marshalBitfield(self.pieces_num))
				self.has_handshake = True
				left_len = self.offset-68
				self.data_buffer[0:left_len] = self.data_buffer[68:self.offset]
				self.offset = left_len
			else:
				print 'INVALID HANDSHAKE'
				self.disconnetFromPeer()
		else:
			print 'ERROR IN extractHandshake()'

	def extractCompleteMsg(self):
		buf = buffer(data)
		return buf

class BitTorrentClientFactory(ClientFactory):
	def __init__(self, torrent):
		self.torrent = torrent
		self.info_hash = hashlib.sha1(bencode.bencode(torrent['info'])).digest()
		self.peer_protocol_dict = {}
		self.pieces_num = len(torrent['info']['pieces'])/20

	def startedConnecting(self, connector):
		print 'STARTED: '+ str(connector.host)

	def clientConnectionFailed(self, connector, reason):
		print 'FAILED: ' + str(connector.host) + ' Reason:' + str(reason)

	def clientConnectionLost(self, connector, reason):
		print 'LOST: ' + str(connector.host) + ' Reason:' + str(reason)


	def buildProtocol(self, addr):
		peer_protocol = BitTorrent(self.torrent, addr, self.info_hash)
		self.peer_protocol_dict[(addr.host, addr.port)] = peer_protocol
		return peer_protocol
