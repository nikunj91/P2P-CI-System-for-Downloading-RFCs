#!/usr/bin/python           
# This is the server file code
#Author Nikunj Shah
#Author Aparna Patil

import socket
import cPickle as pickle
import random
from thread import *
import platform
import time

#Starting the TCP server socket 
serverPort = 7734
serverName = socket.gethostname()
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverName,serverPort))
serverSocket.listen(5)

print 'The server is ready and up'

#Data Structures maintaing the peer data

#key:ip_value 
#value:upload_port_number
peer_info_dict={}

#key: rfc_number 
#value:list of host_names
peer_rfc_dict={}

#key:rfc_number 
#value:rfc_title
rfc_number_title_dict={}

# Insert the intial data into the data structures
def insert_data_in_dict(initial_data,hostname):
	global peer_info_dict,peer_rfc_dict
	peer_info_dict[hostname]=initial_data[0]
	rfc_list=[]
	for i in range(0,len(initial_data[1])):
		if peer_rfc_dict.has_key(initial_data[1][i]):
			peer_rfc_value=peer_rfc_dict.get(initial_data[1][i])
			peer_rfc_value.append(hostname)
		else:
			peer_rfc_dict[initial_data[1][i]]=[hostname]
		rfc_number_title_dict[initial_data[1][i]]=initial_data[2][i]

#Add the RFC to the data structures
def add_peer_rfc(rfc_number,rfc_title,client_host_name):
	global peer_rfc_dict,rfc_number_title_dict
	if not rfc_number_title_dict.has_key(rfc_number):
		rfc_number_title_dict[rfc_number]=rfc_title
		peer_rfc_dict[rfc_number]=[client_host_name]
	else:
		rfc_host_list=peer_rfc_dict.get(rfc_number)
		rfc_host_list.append(client_host_name)
		peer_rfc_dict[rfc_number]=rfc_host_list

#Looksup the RFC and forms the response having the information of the peers holding it
def lookup_peer(rfc_number,rfc_title,client_host_name,client_port_number):
	global peer_rfc_dict,rfc_number_title_dict
	if rfc_number_title_dict.has_key(rfc_number) and rfc_number_title_dict[rfc_number]==rfc_title:
		message = "P2P-CI/1.0 200 OK"
		rfc_host_list=peer_rfc_dict.get(rfc_number)
		for host in rfc_host_list:
			temp = "RFC "+str(rfc_number)+" "+str(rfc_title)+" "+str(host[:host.find(":")])+" "+str(peer_info_dict.get(host))
			message = message + "\r\n" + temp
		message=message+"\r\n"
	else:
		message = "P2P-CI/1.0 404 Not Found\r\n"
	return message

#Creates a list of all the RFC and forms the response with the information of the peers holding it
def list_peer(client_host_name):
	global peer_rfc_dict,rfc_number_title_dict
	rfc_list=peer_rfc_dict.keys()
	if len(rfc_list)==0:
		message = "P2P-CI/1.0 404 Not Found\r\n"
	else:
		message = "P2P-CI/1.0 200 OK"
		for rfc in rfc_list:
			rfc_host_list=peer_rfc_dict.get(rfc)
			for host in rfc_host_list:
				temp = "RFC "+str(rfc)+" "+str(rfc_number_title_dict.get(rfc))+" "+str(host[:host.find(":")])+" "+str(peer_info_dict.get(host))
				message = message + "\r\n" + temp
		message=message+"\r\n"
	return message

#Main server thread function that handles all the requests for ADD< LOOKUP, LIST and EXIT and responds to them
def client_init(connectionsocket, addr):
	
	#Get the initial data sent by client containing its stored RFC infomation 
	initial_data = pickle.loads(connectionsocket.recv(1024))
	host_name=addr[0]+":"+str(initial_data[0])

	#Insert the information into data structures
	insert_data_in_dict(initial_data,host_name)

	while 1:
		#Request received from client for a service
		message_received = connectionsocket.recv(1024)
		message_list = pickle.loads(message_received)

		print "Request received from the client"
		print message_list[0]

		#EXIT Request
		if message_list[0][0]== 'E':
			break

		#ADD Request
		elif message_list[0][0] == 'A':
			split_data=message_list[0].split('\r\n')
			#Check for BAD REQUEST case
			if len(split_data)==5 and "ADD RFC " in split_data[0] and "Host: " in split_data[1] and "Port: " in split_data[2] and "Title: " in split_data[3]:
				#Check for VERSION NOT SUPPORTED case
				#If proper then add the data from the request and echo back the same request with OK Response
				if 'P2P-CI/1.0' in split_data[0]:
					#Retrieve the newly added RFC file information from request
					rfc_number=split_data[0][split_data[0].find("C ")+2:split_data[0].find(" P")]
					client_host_name=split_data[1][split_data[1].find("Host: ")+6:]
					client_port_number=split_data[2][split_data[2].find("Port: ")+6:]
					rfc_title=split_data[3][split_data[3].find("Title: ")+7:]
					p2p_version=split_data[0][split_data[0].find(" P")+1:]
					
					#Add the RFC file information into the data structures
					add_peer_rfc(rfc_number,rfc_title,client_host_name+":"+client_port_number)
					
					#Echo back the request with OK response to the client
					message = "P2P-CI/1.0 200 OK\r\n"+split_data[1]+"\r\n"+split_data[2]+"\r\n"+split_data[3]+"\r\n"
					connectionsocket.send(message)
				else:
					message="505 P2P-CI Version Not Supported\r\n"
					connectionsocket.send(message)
			else:
				message="400 Bad Request\r\n"
				connectionsocket.send(message)

		#LIST Request
		elif message_list[0][0] == "L":
			if message_list[0][1] == "I":
				split_data=message_list[0].split('\r\n')
				#Check for BAD REQUEST case
				if len(split_data)==4 and "LIST ALL " in split_data[0] and "Host: " in split_data[1] and "Port: " in split_data[2]:
					p2p_version=split_data[0][split_data[0].find(" P")+1:]
					#Check for VERSION NOT SUPPORTED case
					#If proper then reply with the list of RFC and their peer information
					if p2p_version=='P2P-CI/1.0':
						#Retrieve information from request
						client_host_name=split_data[1][split_data[1].find("Host: ")+6:]
						client_port_number=split_data[2][split_data[2].find("Port: ")+6:]
						#Reply to the request by sending the response to client
						message=list_peer(client_host_name+":"+client_port_number)
						connectionsocket.send(message)
					else:
						message="505 P2P-CI Version Not Supported\r\n"
						connectionsocket.send(message)
				else:
					message="400 Bad Request\r\n"
					connectionsocket.send(message)

			#LOOKUP Request
			else:
				split_data=message_list[0].split('\r\n')
				#Check for BAD REQUEST case
				if len(split_data)==5 and "LOOKUP RFC " in split_data[0] and "Host: " in split_data[1] and "Port: " in split_data[2] and "Title: " in split_data[3]:
					p2p_version=split_data[0][split_data[0].find(" P")+1:]
					#Check for VERSION NOT SUPPORTED case
					#If proper then reply with the requested RFC file information
					if p2p_version=='P2P-CI/1.0':
						#Retrieve requested RFC file information from request
						rfc_number=split_data[0][split_data[0].find("C ")+2:split_data[0].find(" P")]
						client_host_name=split_data[1][split_data[1].find("Host: ")+6:]
						client_port_number=split_data[2][split_data[2].find("Port: ")+6:]
						rfc_title=split_data[3][split_data[3].find("Title: ")+7:]
						#Reply to the request by sending the RFC file information response to client
						message=lookup_peer(rfc_number,rfc_title,client_host_name+":"+client_port_number,client_port_number)
						connectionsocket.send(message)
					else:
						message="505 P2P-CI Version Not Supported\r\n"
						connectionsocket.send(message)
				else:
					message="400 Bad Request\r\n"
					connectionsocket.send(message)
	
	#When the client EXITS, remove all the information for that client from the data structures maintained
	if peer_info_dict.has_key(host_name):
		peer_info_dict.pop(host_name,None)
	rfc_list=peer_rfc_dict.keys()
	for rfc in rfc_list:
		rfc_host_list=peer_rfc_dict.get(rfc)
		if host_name in rfc_host_list:
			if len(rfc_host_list)==1:
				rfc_number_title_dict.pop(rfc,None)
				peer_rfc_dict.pop(rfc,None)
			else:
				rfc_host_list.remove(host_name)
				peer_rfc_dict[rfc]=rfc_host_list
	#Close the connection thread for that client
	connectionsocket.close()

#Keep the server socket always up and running
while 1:
	#Receive incoming connection request from client
	connectionsocket, addr = serverSocket.accept()
	print 'Got incoming connection request from ', addr
	#Thread will handle all the incoming requests from clients and respond back to them
	start_new_thread(client_init, (connectionsocket, addr))

serverSocket.close()