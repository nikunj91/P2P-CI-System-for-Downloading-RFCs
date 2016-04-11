#!/usr/bin/python           # This is client.py file

import socket
serverName = 'localhost'
serverPort = 12000
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
sentence = raw_input('Input lowercase sentence:')
clientSocket.send(sentence)
modifiedSentence = clientSocket.recv(1024)
print 'From Server:',modifiedSentence
clientSocket.close()
