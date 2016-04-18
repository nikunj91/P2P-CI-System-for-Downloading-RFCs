#!/usr/bin/python           # This is client.py file

import socket               # Import socket module
import time					# Import time module
import platform				# Import platform module to get our OS
import os
import pickle
import random
from thread import *

def send_peer_info():
	rfc_numbers,rfc_titles=get_rfc_details()
	return [upload_client_port_number,rfc_numbers,rfc_titles]

def get_rfc_details():
	rfc_numbers=[]
	rfc_titles=[]
	rfc_storage_path = os.getcwd()+"/rfc"
	for file_name in os.listdir(rfc_storage_path):
		if 'RFC' in file_name:
			rfc_number=file_name[file_name.find("C")+1:file_name.find(".")]
			rfc_title=file_name
			rfc_numbers.append(rfc_number)
			rfc_titles.append(rfc_title)
	return rfc_numbers,rfc_titles

serverName = 'localhost'
serverPort = 7734
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
upload_client_port_number = 65000+random.randint(1, 500)
send_data=send_peer_info()
print send_data
data = pickle.dumps(send_data)
clientSocket.send(data)
clientSocket.close()

#message = "EXIT"
#data = pickle.dumps([message])
#clientSocket.send(data)


#sentence = raw_input('Input lowercase sentence:')
#clientSocket.send(sentence)
#modifiedSentence = clientSocket.recv(1024)
#print 'From Server:',modifiedSentence
clientSocket.close()



