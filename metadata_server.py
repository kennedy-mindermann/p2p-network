''' metadata_server.py
author: Kennedy Mindermann

This class creates a Metatdata Server that is responsible for adding new
servers into a peer-to-peer network. '''

import socket
import threading

class MetadataServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.queue = {} # initializes an empty dictionary
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        self.port_nums = [9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009]
        self.port_nums_index = 0


    def listen(self):
        # listen for incoming servers that want to join the network
        print("M is listening for new connections")
        self.sock.listen(5)
        while True:
            server, ip_addr = self.sock.accept()
            server.settimeout(60)
            server_port = self.port_nums[self.port_nums_index]
            self.port_nums_index += 1
            # create a new thread to handle the connection
            threading.Thread(target = self.getInfoFromServer, args = (server, ip_addr, server_port)).start()


    def getInfoFromServer(self, server, ip_addr, server_port):
        buf = 1024
        while True:
            try:
                flag = " "
                first = True
                m = "send valid flag"
                data = server.recv(buf).decode()
                data = data.split("#")
                flag = data[0]
                server_id = data[1]


                while (flag != "P2P" and flag != "p2p"):
                    print("*****Invalid Flag*****")
                    server.send(m.encode())
                    data = server.recv(buf).decode()
                    print("after recv")
                    data = data.split("#")
                    flag = data[0]
                    server_id = data[1]

                    if(flag == "P2P" and flag == "p2p"):
                        m = " "

                print("***Connected to <",server_id, ">***")
                print("***Valid Flag***")

                if (len(self.queue)==0):
                    #this is going to be the first server in network
                    message = '< {} {} >'.format(server_port, None)
                    self.queue[server_id] = server_port

                else:
                    # there's another server  in network, refer it to the first server in queue
                    message = '< {} {} >'.format(server_port, list(self.queue.values())[0])
                    self.queue[server_id] = server_port

                # send message with port number and referred port number to server
                server.send(message.encode())

                server.close()
                print ("peer ", server_id, " disconnected from MetadataServer")
            except: return False


if __name__ == "__main__":
    while True:
        MetadataServer('127.0.0.1', 9011).listen()
