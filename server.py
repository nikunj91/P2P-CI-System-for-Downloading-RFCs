#!/usr/bin/python           # This is server.py file

import socket
serverPort = 12000
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print 'The server is ready to receive'
while 1:
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(2048)
    capitalizedSentece = sentence.upper()
    connectionSocket.send(capitalizedSentece)
    connectionSocket.close()
