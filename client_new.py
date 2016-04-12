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
		information_list = [req_message,upload_client_port_number,client_hostname,client_rfc_num,client_rfc_title]
		info_add = pickle.dumps(information_list,-1)
		clientSocket.send(info_add)
		#response_received = clientSocket.recv(1024)
		#print response_received
		user_input()

	# elif service == "GET":
	# 	print "Enter RFC Number"
	# 	client_rfc_num = raw_input()
	# 	print "Enter Title"
	# 	client_rfc_title = raw_input()
	# 	#req_message = create_get_request(client_rfc_num, client_rfc_title)
	# 	information_list = ["GET",client_rfc_num, client_hostname, client_port_num, client_rfc_title]
	# 	info_add = pickle.dumps(information_list, -1)
	# 	clientSocket.send(info_add)
	# 	print "Get Request Sent"
	# 	response_received = clientSocket.recv(1024)
	# 	print "Get Response Received from Server"
	# 	response_list = pickle.loads(response_received)
	# 	if len(response_list) == 1:
	# 		print response_list
	# 	else:
	# 		print "Generating P2P Request Message"
	# 		p2p_get_request(client_rfc_num,client_rfc_title,response_list[1],response_list[2])

	# 	user_input()

	elif service == "LIST":
		req_message = create_list_request()
		information_list = [req_message, upload_client_port_number, client_hostname]
		info_add = pickle.dumps(information_list,-1)
		clientSocket.send(info_add)
		#response_received = clientSocket.recv(1024)
		#print response_received
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
		#response_received = clientSocket.recv(1024)
		#print response_received
		user_input()

	elif service == "EXIT":
		message = "EXIT"
		exit_message=pickle.dumps([message],-1)
		clientSocket.send(exit_message)
		clientSocket.close()

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

def send_peer_info():
	rfc_numbers,rfc_titles=get_rfc_details()
	return [upload_client_port_number,rfc_numbers,rfc_titles]

upload_client_port_number = 60000 + random.randint(1,1000)
client_hostname = socket.gethostname()#+str(upload_client_port_number)


send_data=send_peer_info()
data = pickle.dumps(send_data)
clientSocket.send(data)
clientSocket.close

user_input()

