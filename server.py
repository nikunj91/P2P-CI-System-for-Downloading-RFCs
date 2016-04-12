#!/usr/bin/python           # This is server.py file

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

def insert_data_in_dict(intial_data,hostname):
	global peer_info_dict,peer_rfc_dict
	peer_info_dict[hostname]=intial_data[0]
	rfc_list=[]
	for i in range(0,len(intial_data[1])):
		rfc_list.append([intial_data[1][i],intial_data[2][i]])
		print [intial_data[1][i],intial_data[2][i]]
	peer_rfc_dict[hostname]=rfc_list
	print peer_rfc_dict

def create_client_thread(connectionSocket,addr):
	print('Got connection from ', addr)
	intial_data=pickle.loads(connectionSocket.recv(1024))   #upload_port,RFC_numbers,RFC_titles
	print intial_data[0]
	print intial_data[1]
	print intial_data[2]
	insert_data_in_dict(intial_data,addr[0])
	connectionSocket.close()

while 1:
    connectionSocket, addr = serverSocket.accept()
    start_new_thread(create_client_thread, (connectionSocket, addr))
    #sentence = connectionSocket.recv(2048)
    #capitalizedSentece = sentence.upper()
    #connectionSocket.send(capitalizedSentece)
    #connectionSocket.close()
