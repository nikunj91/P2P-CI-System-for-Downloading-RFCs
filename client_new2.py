#!/usr/bin/python           
# This is the client
#Author Nikunj Shah
#Author Aparna Patil

import socket
import os
import cPickle as pickle
import random
from thread import *
import platform
import time

# Server Information
serverPort = 7734
serverName = socket.gethostname()
print "serverName "+serverName

client_RFC_list = {}	# The RFCs that the client has currently

# Connecting to Server
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

# Making RFC list
#rfcs = [f for f in os.listdir(os.getcwd()+'/RFC/')]


def create_add_request(client_rfc_num,client_rfc_title):

	message = "ADD RFC "+str(client_rfc_num)+" P2P-CI/1.0\n"\
			  "Host: "+str(client_hostname)+"\n"\
			  "Port: "+str(upload_client_port_number)+"\n"\
			  "Title: "+str(client_rfc_title)+"\n"\

	print message

	return message

def create_lookup_request(client_rfc_num, client_rfc_title):

	message = "LOOKUP RFC "+str(client_rfc_num)+" P2P-CI/1.0\n"\
			  "Host: "+str(client_hostname)+"\n"\
			  "Port: "+str(upload_client_port_number)+"\n"\
			  "Title: "+str(client_rfc_title)+"\n"\

	print message
	return message

# def create_get_request(client_rfc_num):

# 	message = "GET "+str(client_rfc_num)+" P2P-CI/1.0\n"\
# 			  "Host: "+str(client_hostname)+"\n"\
# 			  "OS: "+platform.platform()+"\n"\

# 	print message
# 	return message

def create_list_request():

	message = "LIST ALL P2P-CI/1.0\n"\
			  "Host: "+str(client_hostname)+"\n"\
			  "Port: "+str(upload_client_port_number)+"\n"\

	print message

	return message

def user_input():
	print "Enter if you want to: ADD, GET, LIST, LOOKUP or EXIT:"
	service = raw_input()

	if service == "ADD":
		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()
		req_message = create_add_request(client_rfc_num,client_rfc_title)
		information_list = [req_message]
		info_add = pickle.dumps(information_list,-1)
		clientSocket.send(info_add)
		response_received = clientSocket.recv(1024)
		print response_received
		user_input()

	elif service == "GET":
		print "Enter RFC number to download"
		download_rfc_num = raw_input()
		print "Enter RFC title to download"
		download_rfc_title = raw_input()
		
		req_message = create_lookup_request(download_rfc_num, download_rfc_title)
		information_list = [req_message]
		info_add = pickle.dumps(information_list, -1)
		clientSocket.send(info_add)
		response_received = clientSocket.recv(1024)
		split_response=response_received.split('\n')
		if '200 OK' not in split_response[0]:
			print 'P2P-CI/1.0 404 Not Found'
		else:
			split_lookup_response=split_response[1].split(' ')
			download_host_name=split_lookup_response[3]
			download_host_number=split_lookup_response[4]
			message="GET RFC "+download_rfc_num+" P2P-CI/1.0\n"\
					"Host: "+download_host_name+"\n"\
					"OS: "+platform.platform()+"\n"
			download_RFC_Socket_P2P = socket.socket()
			print download_host_number
			print download_host_name
			download_RFC_Socket_P2P.connect((socket.gethostname(),int(download_host_number)))
			pickle_message = pickle.dumps([message], -1)
			download_RFC_Socket_P2P.send(pickle_message)
			pickled_response=download_RFC_Socket_P2P.recv(1024)
			response=pickle.loads(pickled_response)
			print response[0]
			download_RFC_Socket_P2P.close()
		user_input()

	elif service == "LIST":
		req_message = create_list_request()
		information_list = [req_message]
		info_add = pickle.dumps(information_list,-1)
		clientSocket.send(info_add)
		response_received = clientSocket.recv(1024)
		print response_received
		user_input()

	elif service == "LOOKUP":
		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()
		req_message = create_lookup_request(client_rfc_num, client_rfc_title)
		information_list = [req_message]
		info_add = pickle.dumps(information_list, -1)
		clientSocket.send(info_add)
		response_received = clientSocket.recv(1024)
		print response_received
		user_input()

	elif service == "EXIT":
		message = "EXIT"
		exit_message=pickle.dumps([message],-1)
		clientSocket.send(exit_message)
		clientSocket.close()

def get_rfc_details():
	rfc_numbers=[]
	rfc_titles=[]
	rfc_storage_path = os.getcwd()+"/RFC2"
	for file_name in os.listdir(rfc_storage_path):
		if 'RFC' in file_name:
			rfc_number=file_name[file_name.find("C")+1:file_name.find(".")]
			rfc_title=file_name
			rfc_numbers.append(rfc_number)
			rfc_titles.append(rfc_title)
	return rfc_numbers,rfc_titles

def send_peer_info(client_hostname):
	rfc_numbers,rfc_titles=get_rfc_details()
	return [upload_client_port_number,rfc_numbers,rfc_titles,client_hostname]

upload_client_port_number = 60000 + random.randint(1,1000)
client_hostname = socket.gethostname()#+str(upload_client_port_number)
print "client_hostname "+client_hostname

send_data=send_peer_info(client_hostname)
data = pickle.dumps(send_data)
clientSocket.send(data)
clientSocket.close

def client_upload():
	clientUploadSocket = socket.socket()
	uploadSocket.bind((client_hostname,upload_client_port_number))
	uploadSocket.listen(5)
	while 1:
		download_connection_socket, download_addr = clientUploadSocket.accept()
		request_received = download_connection_socket.recv(1024)
		download_request = pickle.loads(request_received)
		print download_request[0]
		download_connection_socket.close()

user_input()
start_new_thread(client_upload,())
