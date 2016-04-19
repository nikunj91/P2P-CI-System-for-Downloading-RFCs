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
import email.utils

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

	message = "ADD RFC "+str(client_rfc_num)+" P2P-CI/1.0\r\n"\
			  "Host: "+str(client_hostname)+"\r\n"\
			  "Port: "+str(upload_client_port_number)+"\r\n"\
			  "Title: "+str(client_rfc_title)+"\r\n"\

	print message

	return message

def create_lookup_request(client_rfc_num, client_rfc_title):

	message = "LOOKUP RFC "+str(client_rfc_num)+" P2P-CI/1.0\r\n"\
			  "Host: "+str(client_hostname)+"\r\n"\
			  "Port: "+str(upload_client_port_number)+"\r\n"\
			  "Title: "+str(client_rfc_title)+"\r\n"\

	print message
	return message

def create_get_request(client_rfc_num):

	message = "GET RFC "+str(client_rfc_num)+" P2P-CI/1.0\r\n"\
			  "Host: "+str(client_hostname)+"\r\n"\
			  "OS: "+platform.platform()+"\r\n"\

	print message
	return message

def create_list_request():

	message = "LIST ALL P2P-CI/1.0\r\n"\
			  "Host: "+str(client_hostname)+"\r\n"\
			  "Port: "+str(upload_client_port_number)+"\r\n"\

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
		split_data=message.split('\r\n')
		if len(split_data)==4 and "GET RFC " in split_data[0] and "Host: " in split_data[1] and "OS: " in split_data[2]:
			if 'P2P-CI/1.0' in split_data[0]:
				request=split_data[0].split(" ")
				if request[0]=='GET':
					rfc_number=request[2]
					print rfc_number
					rfc_file_path = os.getcwd()+"/RFC2/RFC"+rfc_number+".txt"
					print rfc_file_path
					opened_file = open(rfc_file_path,'r')
					data = opened_file.read()
					reply_message = "P2P-CI/1.0 200 OK\r\n"\
							  "Date: "+str(email.utils.formatdate(usegmt=True))+"\r\n"\
							  "OS: "+str(platform.platform())+"\r\n"\
							  "Last-Modified: "+str(time.ctime(os.path.getmtime(rfc_file_path)))+"\r\n"\
							  "Content-Length: "+str(len(data))+"\r\n"\
							  "Content-Type: text/plain\r\n"
					reply_message=reply_message+data
					print reply_message
					downloadSocket.sendall(reply_message)
			else:
				reply_message="505 P2P-CI Version Not Supported\r\n"
				downloadSocket.send(reply_message)
		else:
			reply_message="400 Bad Request\r\n"
			downloadSocket.send(reply_message)

def download_rfc_thread(req_message,peer_host_name,peer_port_number,rfc_number):
	requestPeerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	requestPeerSocket.connect((peer_host_name,int(peer_port_number)))
	print 'Connection with peer established'
	requestPeerSocket.sendall(req_message)
	print 'message sent'
	get_reply=""
	get_reply=requestPeerSocket.recv(1024)
	if 'P2P-CI/1.0 200 OK' in get_reply.split("\r\n")[0]:
		print 'P2P-CI/1.0 200 OK'
		print 'File Received'
		content_line=(get_reply.split("\r\n"))[4]
		content_length=int(content_line[content_line.find('Content-Length: ')+16:])
		print content_length
		get_reply=get_reply+requestPeerSocket.recv(content_length)
		#print get_reply
		#print 'yaaaay'
		rfc_file_path = os.getcwd()+"/RFC2/RFC"+rfc_number+".txt"
		print rfc_file_path
		#print '----------------------------------------------'
		#print get_reply
		data=get_reply[get_reply.find('text/plain\r\n')+12:]
		#print '----------------------------------------------'
		#print data
		with open(rfc_file_path,'w') as file:
			file.write(data)
	else:
		print "505 P2P-CI Version Not Supported\r\n"
	requestPeerSocket.close()
	#file.write("xxxxxxxx")

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
		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()
		print client_rfc_num
		print client_rfc_title
		req_message = create_lookup_request(client_rfc_num, client_rfc_title)
		information_list = [req_message]
		info_add = pickle.dumps(information_list, -1)
		clientSocket.sendall(info_add)
		response_received = clientSocket.recv(1024)
		split_data=response_received.split('\r\n')
		if '404 Not Found' in split_data[0]:
			print response_received
		elif 'Version Not Supported' in split_data[0]:
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
			start_new_thread(download_rfc_thread,(req_message,peer_host_name,peer_port_number,client_rfc_num))

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
start_new_thread(upload_thread,())
user_input()

