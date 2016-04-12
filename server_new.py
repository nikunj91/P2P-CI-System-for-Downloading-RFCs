#!/usr/bin/python           # This is server.py file
#Author Nikunj Shah
#Author Aparna Patil

import socket
import cPickle as pickle
import random
from thread import *
import platform
import time

serverPort = 7734
serverName = socket.gethostname()
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverName,serverPort))

serverSocket.listen(5)

print 'The server is ready and up'

peer_info_dict={}
peer_rfc_dict={}
rfc_number_title_dict={}

def insert_data_in_dict(intial_data,hostname):
	global peer_info_dict,peer_rfc_dict
	peer_info_dict[hostname]=intial_data[0]
	rfc_list=[]
	for i in range(0,len(intial_data[1])):
		if peer_rfc_dict.has_key(intial_data[1][i]):
			peer_rfc_value=peer_rfc_dict.get(intial_data[1][i])
			peer_rfc_value.append(hostname)
		else:
			peer_rfc_dict[intial_data[1][i]]=[hostname]
		rfc_number_title_dict[intial_data[1][i]]=intial_data[2][i]
		print [intial_data[1][i],intial_data[2][i]]
	peer_rfc_dict[hostname]=rfc_list
	print peer_rfc_dict
	print rfc_number_title_dict

def client_init(connectionsocket, addr):
	#global active_peer_dict, index_dict, rfc_title_dict
	print('Got connection from ', addr)
	intial_data = pickle.loads(connectionsocket.recv(1024))
	print intial_data[0]
	print intial_data[1]
	print intial_data[2]

	insert_data_in_dict(intial_data,addr[0])

	while 1:
		message_received = connectionsocket.recv(1024)
		message_list = pickle.loads(message_received)
		if message_list[0][0]== 'E':
			break
		#if type(message_list) == str:
		elif message_list[0][0] == 'A':
			print message_list[0]

		elif message_list[0][0] == "L":
			if message_list[0][1] == "I":
				print message_list[0]
			else:
				print message_list[0]

		elif message_list[0][0] == "G":
				print message_list[0]	

	connectionsocket.close()

while 1:
	connectionsocket, addr = serverSocket.accept()
	start_new_thread(client_init, (connectionsocket, addr))
serverSocket.close()