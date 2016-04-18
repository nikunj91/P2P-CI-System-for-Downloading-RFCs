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

def create_get_request(client_rfc_num):

	message = "GET "+str(client_rfc_num)+" P2P-CI/1.0\n"\
			  "Host: "+str(client_hostname)+"\n"\
			  "OS: "+platform.platform()+"\n"\

	print message
	return message

def create_list_request():

	message = "LIST ALL P2P-CI/1.0\n"\
			  "Host: "+str(client_hostname)+"\n"\
			  "Port: "+str(upload_client_port_number)+"\n"\

	print message

	return message

def upload_thread():
	uploadSocket = socket.socket()
	host=socket.gethostname()
	uploadSocket.bind((host,upload_client_port_number))
	uploadSocket.listen(5)
	while 1:
		print "Upload Thread started"
		downloadSocket,downloadAddress = uploadSocket.accept()
		message = downloadSocket.recv(1024)
		print message

def download_rfc_thread(req_message,peer_host_name,peer_port_number):
	requestPeerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	requestPeerSocket.connect((peer_host_name,int(peer_port_number)))
	print 'Connection with peer established'
	requestPeerSocket.sendall(req_message)

def user_input():
	print "Enter if you want to: ADD, GET, LIST, LOOKUP or EXIT:"
	service = raw_input()

	if service == "ADD":
		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()
		req_message = create_add_request(client_rfc_num,client_rfc_title)
		information_list = [req_message,upload_client_port_number,client_hostname,client_rfc_num,client_rfc_title]
		info_add = pickle.dumps(information_list,-1)
		clientSocket.send(info_add)
		response_received = clientSocket.recv(1024)
		print response_received
		user_input()

	elif service == "GET":
		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()
		print client_rfc_num
		print client_rfc_title
		req_message = create_lookup_request(client_rfc_num, client_rfc_title)
		information_list = [req_message, upload_client_port_number, client_hostname, client_rfc_num, client_rfc_title]
		info_add = pickle.dumps(information_list, -1)
		clientSocket.sendall(info_add)
		response_received = clientSocket.recv(1024)
		split_data=response_received.split('\n')
		if '404 Not Found' in split_data[0]:
			print response_received
		else:
			print response_received
			split_data=split_data[1].split(" ")
			peer_host_name=split_data[3]
			peer_port_number=split_data[4]
			print peer_host_name
			print peer_port_number
			req_message = create_get_request(client_rfc_num)
			print req_message
			start_new_thread(download_rfc_thread,(req_message,peer_host_name,peer_port_number))

			
			
		#clientSocket.sendall(req_message)

		# information_list = ["GET",client_rfc_num, client_hostname, client_port_num, client_rfc_title]
		# info_add = pickle.dumps(information_list, -1)
		# clientSocket.send(info_add)
		# print "Get Request Sent"
		# response_received = clientSocket.recv(1024)
		# print "Get Response Received from Server"
		# response_list = pickle.loads(response_received)
		# if len(response_list) == 1:
		# 	print response_list
		# else:
		# 	print "Generating P2P Request Message"
		# 	p2p_get_request(client_rfc_num,client_rfc_title,response_list[1],response_list[2])

		user_input()

	elif service == "LIST":
		req_message = create_list_request()
		information_list = [req_message, upload_client_port_number, client_hostname]
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
		information_list = [req_message, upload_client_port_number, client_hostname, client_rfc_num, client_rfc_title]
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
	rfc_storage_path = os.getcwd()+"/RFC"
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
start_new_thread(upload_thread,())
user_input()

