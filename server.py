#!/usr/bin/python           # This is server.py file
#Author Nikunj Shah
#Author Aparna Patil

import socket               # Import socket module
import time					# Import time module
import platform				# Import platform module to get our OS
from thread import *
import pickle

serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverPort = 7734
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print 'The server is ready to receive'

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

def create_lookup_response(peer_list,rfc_number,rfc_title,client_host_name,client_port_number):
	return '1'

def lookup_peer(rfc_number,rfc_title,client_host_name,client_port_number):
	global peer_rfc_dict,rfc_number_title_dict
	if rfc_number_title_dict[rfc_number]==rfc_title:
		message=create_lookup_response(peer_rfc_dict[rfc_number],rfc_number,rfc_title,client_host_name,client_port_number)
		return message



def create_client_thread(connectionSocket,addr):
	print('Got connection from ', addr)
	intial_data=pickle.loads(connectionSocket.recv(1024))   #upload_port,RFC_numbers,RFC_titles
	print intial_data[0]
	print intial_data[1]
	print intial_data[2]
	insert_data_in_dict(intial_data,addr[0])

	while(1):
		temp=connectionSocket.recv(1024)
		data = pickle.loads(temp)
		if data[0]=='EXIT':
			print 'exit'
			break
		elif data[0][0]=='A':
			print 'A'
		elif data[0][0]=='L':
			if data[0][1]=='O':
				split_data=data[0].split('\n')
				rfc_number=split_data[0][split_data[0].find("C ")+2:split_data[0].find(" P")]
				client_host_name=split_data[1][split_data[1].find("Host: ")+6:]
				client_port_number=split_data[2][split_data[2].find("Port: ")+6:]
				rfc_title=split_data[3][split_data[3].find("Title: ")+7:]
				p2p_version=split_data[0][split_data[0].find(" P")+1:]
				print rfc_number
				print client_host_name
				print client_port_number
				print rfc_title
				print p2p_version
				#message=lookup_peer(rfc_number,rfc_title,client_host_name,client_port_number)
	connectionSocket.close()

while 1:
    connectionSocket, addr = serverSocket.accept()
    start_new_thread(create_client_thread, (connectionSocket, addr))
    #sentence = connectionSocket.recv(2048)
    #capitalizedSentece = sentence.upper()
    #connectionSocket.send(capitalizedSentece)
serverSocket.close()
