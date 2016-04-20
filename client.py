#!/usr/bin/python           
# This is the client file code
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
import sys

# Server Information

#Server IP Address from command line
serverPort = int(sys.argv[1])
#Server Port from command line
serverName = sys.argv[2]

# Will store the RFCs that the client has currently at the time of coming up
client_RFC_list = {}	

# Connecting to Server using Socket and TCP
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
print 'Connected to server at address: '+str(serverName)+" and port: "+str(serverPort)
client_hostname=clientSocket.getsockname()[0]
#Create the ADD Request message
def create_add_request(client_rfc_num,client_rfc_title):
	message = "ADD RFC "+str(client_rfc_num)+" P2P-CI/1.0\r\n"\
			  "Host: "+str(client_hostname)+"\r\n"\
			  "Port: "+str(upload_client_port_number)+"\r\n"\
			  "Title: "+str(client_rfc_title)+"\r\n"
	return message

#Create the LOOKUP Request message
def create_lookup_request(client_rfc_num, client_rfc_title):
	message = "LOOKUP RFC "+str(client_rfc_num)+" P2P-CI/1.0\r\n"\
			  "Host: "+str(client_hostname)+"\r\n"\
			  "Port: "+str(upload_client_port_number)+"\r\n"\
			  "Title: "+str(client_rfc_title)+"\r\n"
	return message

#Create the GET Request message
def create_get_request(client_rfc_num):
	message = "GET RFC "+str(client_rfc_num)+" P2P-CI/1.0\r\n"\
			  "Host: "+str(client_hostname)+"\r\n"\
			  "OS: "+platform.platform()+"\r\n"
	return message

#Create the LIST Request message
def create_list_request():
	message = "LIST ALL P2P-CI/1.0\r\n"\
			  "Host: "+str(client_hostname)+"\r\n"\
			  "Port: "+str(upload_client_port_number)+"\r\n"
	return message

#This will keep the client upload socket on the randomly generated port number.
#This upload server socket is always running to listen for incoming file upload requests from other peers
#It will accept the request
#If the request is proper then it replies with the required RFC file data
def upload_thread():
	
	#Create a upload server socket
	uploadSocket = socket.socket()
	host='0.0.0.0'
	uploadSocket.bind((host,upload_client_port_number))
	uploadSocket.listen(5)
	while 1:
		#Accept an incoming request for upload
		downloadSocket,downloadAddress = uploadSocket.accept()
		message = downloadSocket.recv(1024)
		split_data=message.split('\r\n')
		
		#Check for BAD REQUEST case
		if len(split_data)==4 and "GET RFC " in split_data[0] and "Host: " in split_data[1] and "OS: " in split_data[2]:
			#Check for VERSION NOT SUPPORTED case
			if 'P2P-CI/1.0' in split_data[0]:
				#Else reply to the request with the requested file data
				request=split_data[0].split(" ")
				if request[0]=='GET':

					#Get the request RFC number
					rfc_number=request[2]

					#Locate the file and get its data
					rfc_file_path = os.getcwd()+"/RFC/RFC"+rfc_number+".txt"
					opened_file = open(rfc_file_path,'r')
					data = opened_file.read()

					#Formulate the reply to be sent to the requesting peer
					reply_message = "P2P-CI/1.0 200 OK\r\n"\
							  "Date: "+str(email.utils.formatdate(usegmt=True))+"\r\n"\
							  "OS: "+str(platform.platform())+"\r\n"\
							  "Last-Modified: "+str(time.ctime(os.path.getmtime(rfc_file_path)))+"\r\n"\
							  "Content-Length: "+str(len(data))+"\r\n"\
							  "Content-Type: text/plain\r\n"
					reply_message=reply_message+data
					
					#Send the reply
					downloadSocket.sendall(reply_message)
			else:
				reply_message="505 P2P-CI Version Not Supported\r\n"
				downloadSocket.send(reply_message)
		else:
			reply_message="400 Bad Request\r\n"
			downloadSocket.send(reply_message)

#Does all the handling for sending the GET request and receiving the RFC file from it 
def download_rfc_thread(req_message,peer_host_name,peer_port_number,rfc_number):

	#Connect to the upload server socket of the peer holding the required file
	requestPeerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	requestPeerSocket.connect((peer_host_name,int(peer_port_number)))
	
	print 'Connection with peer established'

	#Send the GET request to the peer
	requestPeerSocket.sendall(req_message)
	
	#Receive the reply from the peer with the data in it.
	get_reply=""
	get_reply=requestPeerSocket.recv(1024)
	if 'P2P-CI/1.0 200 OK' in get_reply.split("\r\n")[0]:
		print 'P2P-CI/1.0 200 OK'
		content_line=(get_reply.split("\r\n"))[4]
		content_length=int(content_line[content_line.find('Content-Length: ')+16:])
		get_reply=get_reply+requestPeerSocket.recv(content_length)
		rfc_file_path = os.getcwd()+"/RFC/RFC"+rfc_number+".txt"
		data=get_reply[get_reply.find('text/plain\r\n')+12:]

		#Writing the file data to a file
		with open(rfc_file_path,'w') as file:
			file.write(data)
		print 'File Received from peer and stored locally now'
	elif 'Version Not Supported' in get_reply.split("\r\n")[0]:
		print get_reply
	elif 'Bad Request' in get_reply.split("\r\n")[0]:
		print get_reply

	#Closing the socket connection
	requestPeerSocket.close()

# This function will do all code handling for GET,ADD,LOOKUP,LIST and EXIT
def user_input():

	#Get the raw input from user
	print "Enter if you want to: ADD, GET, LIST, LOOKUP or EXIT:"
	service = raw_input()

	if service == "ADD":

		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()

		rfc_file_path = os.getcwd()+"/RFC/RFC"+client_rfc_num+".txt"
		if os.path.isfile(rfc_file_path):
			#Create the ADD Request message and send it to server using the socket
			req_message = create_add_request(client_rfc_num,client_rfc_title)

			print "ADD Request to be sent to the server"
			print req_message

			information_list = [req_message]
			info_add = pickle.dumps(information_list,-1)
			clientSocket.send(info_add)
			
			#Receive the response from server and print the same
			response_received = clientSocket.recv(1024)
			print "ADD Response sent from the server"
			print response_received
		else:
			print "File Not Present in the directory"

		user_input()

	elif service == "GET":

		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()

		#Create a LOOKUP request to find the peer holding the requesting RFC. Send it to the server
		req_message = create_lookup_request(client_rfc_num, client_rfc_title)

		print "LOOKUP Request to be sent to the server for completing the GET request"
		print req_message

		information_list = [req_message]
		info_add = pickle.dumps(information_list, -1)
		clientSocket.sendall(info_add)

		#Receive the LOOKUP response from the server
		response_received = clientSocket.recv(1024)

		#Based on server response, verify the response for FILE NOT FOUND, BAD REQUEST or WRONG VERSION
		split_data=response_received.split('\r\n')

		print "LOOKUP Response sent from the server"
		
		if '404 Not Found' in split_data[0]:
			print response_received
		elif 'Version Not Supported' in split_data[0]:
			print response_received
		elif 'Bad Request' in split_data[0]:
			print response_received
		else:
			print response_received

			#Retrieve the HOSTNAME and PORT NUMBER of the first peer in the response holding the RFC file
			split_data=split_data[1].split(" ")
			peer_host_name=split_data[3]
			peer_port_number=split_data[4]

			#Create the GET request to be sent to the peer
			req_message = create_get_request(client_rfc_num)
			
			print "GET Request to be sent to the peer holding the RFC File"
			print req_message

			#start a new thread that will do all the handling for sending the GET request and receiving the RFC file from it
			start_new_thread(download_rfc_thread,(req_message,peer_host_name,peer_port_number,client_rfc_num))

		user_input()

	elif service == "LIST":

		#Create a LIST request to be sent to the server
		req_message = create_list_request()

		print "LIST Request to be sent to the server"
		print req_message

		#Send the request to the server
		information_list = [req_message]
		info_add = pickle.dumps(information_list,-1)
		clientSocket.send(info_add)

		#Receive the response from the server
		response_received = clientSocket.recv(1024)

		print "LIST Response sent from the server"
		print response_received

		user_input()

	elif service == "LOOKUP":

		print "Enter RFC Number"
		client_rfc_num = raw_input()
		print "Enter Title"
		client_rfc_title = raw_input()

		#Create a LOOKUP request to be sent to the server
		req_message = create_lookup_request(client_rfc_num, client_rfc_title)

		print "LOOKUP Request to be sent to the server"
		print req_message

		#Send the request to the server
		information_list = [req_message]
		info_add = pickle.dumps(information_list, -1)
		clientSocket.send(info_add)

		#Receive the response from the server
		response_received = clientSocket.recv(1024)

		print "LOOKUP Response sent from the server"		
		print response_received

		user_input()

	elif service == "EXIT":
		#Handle the case when the user wants to stop the client by sending EXIT command
		#The information will be relayed to the server
		#The server will then remove information related to all the files that this client had
		#The client socket connection to the server is closed
		message = "EXIT"
		exit_message=pickle.dumps([message],-1)
		clientSocket.send(exit_message)
		clientSocket.close()
	else:
		print 'Wrong input. Please try again.'
		user_input()

#Generating the initial peer file data from the specified directory
#Returns 2 lists, one each for RFC numbers and RFC titles
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

#Generating the initial peer file data to send over to the server
def send_peer_info():
	rfc_numbers,rfc_titles=get_rfc_details()
	return [upload_client_port_number,rfc_numbers,rfc_titles]

#Generating the random client port number it will use for uploading
upload_client_port_number = 60000 + random.randint(1,1000)

#Generating the initial peer file data to send over to the server and sending the same to server
send_data=send_peer_info()
data = pickle.dumps(send_data)
clientSocket.send(data)
clientSocket.close

#Starts a new thread that maintain the upload server socket over the random upload port generated
start_new_thread(upload_thread,())
# This function will do all code handling for GET,ADD,LOOKUP,LIST and EXIT
user_input()

