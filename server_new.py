#!/usr/bin/python           
# This is the server
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

peer_info_dict={}   #key:hostname value:upload_port_number
peer_rfc_dict={} #key: rfc_number value:list of host_names
rfc_number_title_dict={} #key:rfc_number value:rfc_title

def insert_data_in_dict(initial_data):
	global peer_info_dict,peer_rfc_dict
	hostname=initial_data[3]+":"+str(initial_data[0])
	peer_info_dict[hostname]=initial_data[0]
	rfc_list=[]
	for i in range(0,len(initial_data[1])):
		if peer_rfc_dict.has_key(initial_data[1][i]):
			peer_rfc_value=peer_rfc_dict.get(initial_data[1][i])
			peer_rfc_value.append(hostname)
		else:
			peer_rfc_dict[initial_data[1][i]]=[hostname]
		rfc_number_title_dict[initial_data[1][i]]=initial_data[2][i]
		print [initial_data[1][i],initial_data[2][i]]
	
	print peer_rfc_dict
	print rfc_number_title_dict

def add_peer_rfc(rfc_number,rfc_title,client_host_name,client_port_number):
	global peer_rfc_dict,rfc_number_title_dict
	if not rfc_number_title_dict.has_key(rfc_number):
		rfc_number_title_dict[rfc_number]=rfc_title
		peer_rfc_dict[rfc_number]=[client_host_name]
	else:
		rfc_host_list=peer_rfc_dict.get(rfc_number)
		rfc_host_list.append(client_host_name)
		peer_rfc_dict[rfc_number]=rfc_host_list
	print rfc_number_title_dict
	print peer_rfc_dict

def lookup_peer(rfc_number,rfc_title,client_host_name,client_port_number):
	global peer_rfc_dict,rfc_number_title_dict
	if rfc_number_title_dict.has_key(rfc_number) and rfc_number_title_dict[rfc_number]==rfc_title:
		message = "P2P-CI/1.0 200 OK"
		rfc_host_list=peer_rfc_dict.get(rfc_number)
		for host in rfc_host_list:
			temp = "RFC "+str(rfc_number)+" "+str(rfc_title)+" "+str(host[0:host.find(":")])+" "+str(peer_info_dict.get(host))
			message = message + "\n" + temp
	else:
		message = "P2P-CI/1.0 404 Not Found"
	return message

def list_peer(client_host_name):
	global peer_rfc_dict,rfc_number_title_dict
	rfc_list=peer_rfc_dict.keys()
	if len(rfc_list)==0:
		message = "P2P-CI/1.0 404 Not Found"
	else:
		message = "P2P-CI/1.0 200 OK"
		for rfc in rfc_list:
			rfc_host_list=peer_rfc_dict.get(rfc)
			for host in rfc_host_list:
				temp = "RFC "+str(rfc)+" "+str(rfc_number_title_dict.get(rfc))+" "+str(host[host.find(":")+1:])+" "+str(peer_info_dict.get(host))
				message = message + "\n" + temp
	return message

def client_init(connectionsocket, addr):
	#global active_peer_dict, index_dict, rfc_title_dict
	print('Got connection from ', addr)
	initial_data = pickle.loads(connectionsocket.recv(1024))
	print initial_data[0]
	print initial_data[1]
	print initial_data[2]
	print initial_data[3]
	host_name=initial_data[3]+":"+str(initial_data[0])
	insert_data_in_dict(initial_data)

	while 1:
		message_received = connectionsocket.recv(1024)
		message_list = pickle.loads(message_received)
		if message_list[0][0]== 'E':
			break
		#if type(message_list) == str:
		elif message_list[0][0] == 'A':
			split_data=message_list[0].split('\n')
			rfc_number=split_data[0][split_data[0].find("C ")+2:split_data[0].find(" P")]
			client_host_name=split_data[1][split_data[1].find("Host: ")+6:]
			client_port_number=split_data[2][split_data[2].find("Port: ")+6:]
			rfc_title=split_data[3][split_data[3].find("Title: ")+7:]
			p2p_version=split_data[0][split_data[0].find(" P")+1:]
			add_peer_rfc(rfc_number,rfc_title,client_host_name+":"+client_port_number)
			connectionsocket.send(message_list[0])

		elif message_list[0][0] == "L":
			if message_list[0][1] == "I":
				#print message_list[0]
				split_data=message_list[0].split('\n')
				p2p_version=split_data[0][split_data[0].find(" P")+1:]
				client_host_name=split_data[1][split_data[1].find("Host: ")+6:]
				client_port_number=split_data[2][split_data[2].find("Port: ")+6:]
				message=list_peer(client_host_name+":"+client_port_number)
				connectionsocket.send(message)
			else:
				#print message_list[0]
				split_data=message_list[0].split('\n')
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
				message=lookup_peer(rfc_number,rfc_title,client_host_name+":"+client_port_number,client_port_number)
				connectionsocket.send(message)

		elif message_list[0][0] == "G":
				print message_list[0]	


	
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
				print host_name
				rfc_host_list.remove(host_name)
				peer_rfc_dict[rfc]=rfc_host_list

	print peer_info_dict
	print peer_rfc_dict
	print rfc_number_title_dict

	connectionsocket.close()

while 1:
	connectionsocket, addr = serverSocket.accept()
	start_new_thread(client_init, (connectionsocket, addr))
serverSocket.close()