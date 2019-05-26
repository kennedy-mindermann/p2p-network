''' server.py
author: Kennedy Mindermann

This file creates a new server that can join a peer-to-peer network. It has
functionality to connect to a MetadataServer to join the network and receive
both user input and messages from other servers in the network. '''

import socket
import tty
import sys
import termios
import select
import threading
import os

neighbors = {}
localhost = '127.0.0.1'


def hasFile(my_id, file):
    '''this checks for a file in the server's directory'''
    path = "./ServerFiles/" + my_id.upper()
    for dir, dirnames, files in os.walk(path):
        for f in files:
            if f == file:
                return True
        break
    return False


def sendToNeighbors(message):
    '''this sends message to all current neighbors of the server'''
    for connection in list(neighbors.values()):
        connection[1].send(message.encode())


def waitOnSocket(sock, my_id):
    '''This method is for handling any incoming messages the server may receive.
        It does a blocking receive on the socket passed in and handles any
        received message appropriately'''
    while True:
        data = sock.recv(1024).decode()
        if data != '':
            data = data.split()
            recv_id = data[0]
            data = data[1]
            if recv_id == 'found':
                # this server is going to receive a file... handle download
                print("downloading file: ", data)
                path = './ServerFiles/'+my_id.upper()+'/Downloads'
                os.chdir(path)
                new_file = open(data, 'w+')
                file_contents = sock.recv(1024).decode()
                new_file.write(file_contents)
                new_file.close()
                print("closed file")
                os.chdir('../../../')

            elif data == 'TOPO':
                print("*** Current Network Topology: ")
                if len(neighbors) == 0:
                    print(my_id, ": ")
                elif len(neighbors) == 1:
                    print(my_id, ": ", list(neighbors.keys())[0])
                else:
                    print(my_id, ": ", list(neighbors.keys())[0], list(neighbors.keys())[1])
                for key in neighbors:
                    if key != recv_id:
                        message = my_id + ' TOPO'
                        neighbors[key][1].send(message.encode())

            elif data == 'Stop':
                for key in neighbors:
                    if key != recv_id:
                        message = my_id + ' Stop'
                        neighbors[key][1].send(message.encode())
                        neighbors[key][1].close()
                        print("*** Closed connection with ", key, "***")
                    else:
                        neighbors[key][1].close()
                        print("*** Closed connection with ", key, "***")

                print("***Server Closed***")
                os._exit(0)

            else:
                # received request for file download
                print("*** Received ", data, " from ", recv_id, " ***")
                port, file = data.split(":")
                found = hasFile(my_id, file)
                if found:
                    print(file, " found")
                    connected = False
                    connection = None
                    for neighbor in list(neighbors.values()):
                        if int(neighbor[0]) == int(port):
                            connection = neighbor[1]
                            connected = True

                    if not connected:
                        # not already connected to requesting server
                        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        connection.connect((localhost, int(port)))

                    connection.send(('found ' + file).encode())
                    path = './ServerFiles/'+my_id.upper()
                    os.chdir(path)
                    with open(file) as f:
                        line = f.readline()
                        connection.send(line.encode())
                    os.chdir('../../')

                    if not connected:
                        connection.close()
                    print(file, " sent")

                else:
                    for key in neighbors:
                        if key != recv_id:
                            message = my_id + ' ' + str(port) +':' + file
                            neighbors[key][1].send(message.encode())


def listenForUserInput(my_id, my_port):
    ''' The sole purpose of this is to listen for user input from the
        terminal. Once user input it received, it will handle it accordingly'''
    while True:
        print("\n type...\n     'TOPO' to see the current network topology, \n     'Stop' to terminate all socket connections \n     Otherwise, enter file name to download\n")
        u_input = input() # get the user input from the terminal
        u_input= u_input.strip()

        if u_input == 'Stop':
            sendToNeighbors(my_id + ' Stop')
            for n_id in neighbors:
                neighbors[n_id][1].close()
                print("*** Closed connection with ", n_id, "***")

            print("**Server Closed**")
            os._exit(0)

        elif u_input == 'TOPO':
            print("\n *** Current Network Topology: ")
            if len(neighbors) == 0:
                print(my_id, ": ")
            elif len(neighbors) == 1:
                print(my_id, ": ", list(neighbors.keys())[0])
            else:
                print(my_id, ": ", list(neighbors.keys())[0], list(neighbors.keys())[1])
            message = my_id + ' ' + 'TOPO'
            sendToNeighbors(message)

        else:
            # this is the case where the user types a filename... try to download
            print("file to download: ", u_input+'.txt')
            u_input = u_input + '.txt'
            found = hasFile(my_id, u_input)

            if found:
                print("** File already exists in your directory")
            else:
                sendToNeighbors(my_id + ' ' + str(my_port) + ':' + u_input)


def createServerSocket(my_port, my_id, firstServer):
    ''' this creates a new server socket that will first be bound and then will
    continue to listen and handle new connections throughout the lifetime
    of the server'''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((localhost, my_port))
    sock.listen(5)
    print("listening for peers")

    while True:
        peersock, peeraddr = sock.accept()
        sid = peersock.recv(1024).decode()

        if sid.startswith('found'):
            # temporary connection to download a file
            flag, file = sid.split(' ')
            print("** downloading ", file)
            path = './ServerFiles/'+my_id.upper()+'/Downloads'
            os.chdir(path)
            new_file = open(file, 'w+')
            file_contents = peersock.recv(1024).decode()
            new_file.write(file_contents)
            new_file.close()
            print("closed file")
            os.chdir('../../../')

        else:
            # a new, persistent connection
            print("accepted connection from ", sid)
            if (len(neighbors) == 0):
                neighbors[sid] = (peeraddr[1], peersock)
                peersock.send((my_id + "#" + str(my_port)).encode())
                print("*** Connected to ", sid, " ***")
                T = threading.Thread(target = waitOnSocket, args=[peersock, my_id]).start()

            elif (len(neighbors) == 1):
                neighbors[sid] = (peeraddr[1], peersock)
                peersock.send((my_id + "#" + str(peeraddr[1])).encode())
                print("*** Connected to ", sid, " ***")
                T = threading.Thread(target = waitOnSocket, args=[peersock, my_id]).start()

            else:
                if (firstServer):
                    # this is the first server in the network so both its neighbors can have another connection
                    peersock.send((my_id + "#" + str(list(neighbors.values())[0][0])).encode())
                else:
                    # send the second port in the dictionary...
                    # the first would be the one this server is connected to which already has two connections
                    peersock.send((my_id + "#" + str(list(neighbors.values())[1][0])).encode())
                peersock.close()
                print("peer socket with ", sid, " closed")

def createMServerSocket(M_server_ip, M_server_port):
    ''' this creates a new socket and uses it to connect to the
        Metatdata Server'''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((M_server_ip, M_server_port))
    return sock

def createClientSocket(my_port, ref_port_num, my_id):
    ''' This creates a new socket and binds to the server's port number. It
        then connects to the referred port number. If the server at the
        referred port already has two connections it will send back a
        new port number. If a port number is received that does not equal the
        server's own port number or does not equal the referred port number,
        it will connect with the server at that port instead.'''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0', my_port))
    sock.connect((localhost, ref_port_num))
    sock.send(my_id.encode())

    response_msg = sock.recv(1024).decode()
    response_msg = response_msg.split("#")
    server_id = response_msg[0]
    port_num = response_msg[1]
    print("received ", port_num, " from ", server_id)

    while (int(port_num) != my_port and int(port_num) != int(ref_port_num)):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0', my_port))
        sock.connect((localhost, int(port_num)))
        sock.send(my_id.encode())
        response_msg = sock.recv(1024).decode()
        response_msg = response_msg.split("#")
        server_id = response_msg[0]
        port_num = response_msg[1]
        print("received ", port_num, " from ", server_id)

    print("*** Connected to ", server_id, " ***")
    neighbors[server_id] = (port_num, sock)
    waitOnSocket(sock, my_id)


def mainloop( M_server_ip, M_server_port, id):
    ''' This is the main loop of the server program. It first connects to
        the Metatdata Server to get a port number and a referred port number.
        It then creats muliple threads to handle setting up the server socket
        and the client socket '''
    M_server_ip = M_server_ip
    M_server_port = int(M_server_port) #port number of MetadataServer
    id = id
    port = None
    client_sock = None
    firstServer = False

    sock = createMServerSocket(M_server_ip, M_server_port)
    buf = 1024
    data = "send valid flag"
    while (data == "send valid flag"):
        flag = input("enter valid flag to send to Metadata Server (ex: P2P to join network): ")
        sock.send((flag+'#'+id).encode())
        data = sock.recv(buf).decode()

    # the data we recieved is of the form <Port Number, Referred Port Number>
    data = data.replace("<", "")
    data = data.replace(">", "")
    data = data.split()

    port = int(data[0])
    referred_port = data[1]

    if (referred_port != 'None'):
        # the server received a port number to connect to
        T = threading.Thread(target = createClientSocket, args = (port, int(referred_port), id)).start()
    else:
        # this is the first server in the network
        firstServer = True

    T = threading.Thread(target = createServerSocket, args = (port, id, firstServer)).start()
    listenForUserInput(id, port)


if __name__ == "__main__":
    action = ""
    while (action != "1"):
        action = input("\ntype 1 to add a server to the p2p network: ")
    servername = input("\nID of the server? ")
    mainloop(localhost, 9011, servername)
