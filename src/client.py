#!/usr/bin/python
import bencode
import requests
import hashlib
import sys
import os
from twisted.internet import protocol, reactor
import socket
import Protocol

listen_port = 6881#6881
filename = 'project3.torrent'
conn_timeout = 3
read_timeout = 10
def parse_torrent(filename):
	with open(filename, 'rb') as torrent_file:
		torrent_text = torrent_file.read()
	torrent = bencode.bdecode(torrent_text)
	return torrent

def start_from_tracker(torrent, port):
	url_list = [torrent['announce']]
	if torrent.has_key('announce-list'):
		for anounces in torrent['announce-list']:
			for announce in anounces:
				url_list.append(announce)
	print url_list
	parameters = {}
	parameters['info_hash'] = hashlib.sha1(bencode.bencode(torrent['info'])).digest()
	#print parameters['info_hash']
	parameters['peer_id'] = 'clienthaomingzyduan1'
	parameters['port'] = str(port)
	parameters['uploaded'] = '0'
	parameters['downloaded'] = '0'
	parameters['compact'] = '0'
	parameters['event'] = 'started'
	parameters['numwant'] = '100'
	if torrent['info'].has_key('length'):
		total_len = int(torrent['info']['length'])
	else:
		files = torrent['info']['files']
		# compute total length
		total_len = 0
		for file in files:
			total_len += file['length']
	
	parameters['left'] = total_len
	http_response_list = []
	for url in url_list:
		if url.startswith('http'):
			try:
				r = requests.get(url, params=parameters, timeout=(conn_timeout, read_timeout))
			except Exception as e:
				print 'Cannot connect to tracker:' + str(url)
				continue
			if r.status_code==200:
				print 'get peers from' + str(url)
				http_response_list.append(bencode.bdecode(r.content))
			else:
				print 'Cannot connect to tracker:' + str(url) + ' status code:' + r.status_code
		else:
			print 'Ignore non-http tracker:' + str(url)
	return http_response_list

def parse_peers(http_response_list):
	all_peers = []
	for http_response in http_response_list:
		peers = http_response['peers']
		if isinstance(peers,str):
			for i in range(len(peers)):
				if i%6==0:#first ip
					peer = str(ord(peers[i]))
				elif i%6==4:#first port
					port = ord(peers[i]) * 256
				elif i%6==5:#last post
					port += ord(peers[i])
					all_peers.append([peer, port])
				else:
					peer += '.' + str(ord(peers[i]))

		elif isinstance(peers,list):
			for peer in peers:
				all_peers.append([peer['ip'].encode('ascii'), peer['port']])
	return all_peers

def debug(s):
	for i in s:
		print ord(i)

torrent = parse_torrent(filename)
#print torrent
http_response_list = start_from_tracker(torrent, listen_port)
#print http_response_list
all_peers = parse_peers(http_response_list)
print all_peers
#debug(http_response_list[0]['peers'])
for i in range(0,min(10, len(all_peers))):
	one_peer = all_peers[i]
	reactor.connectTCP(host=one_peer[0], port=one_peer[1], factory=Protocol.BitTorrentClientFactory(torrent))
reactor.run()