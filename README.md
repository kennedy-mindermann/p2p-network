## Implementing a Peer-to-Peer network
##### Kennedy Mindermann
##### minde024

### There are two main parts to my program:
**MetadataServer**:
The MetatdataServer is implemented as a class using multithreading. I decided on this because there only needs to be one MetadataServer for each peer-to-peer network so using a class makes it simple and efficient to create an instance of the MetatdataServer when need be. Creating it to be multithreaded allows for multiple incoming connections to be handled at the same time.
On initialization, the MetadataServer creates a new socket, binds
to its port number, and creates a queue to keep track of servers currently in the
network. It then starts listening for incoming connections. When it gets a new incoming connection, it will create a new thread to handle the
connection, connect to the incoming server, wait for the flag "P2P" or "p2p".
Once a valid flag is received, it will assign it a port number and refer it to
the first server in its cache (so the first server already in the network). The
maximum number of servers that the MetatdataServer can assign port numbers to is
ten. Once it has done so, it will close its connection with the server and continue listening for new connections.

**Server**:
This is the peer server in a peer-to-peer network. I did not implement it as a
class; however, I did make it multithreaded. I made this decision because the
server must listen on multiple sockets and listen for user input at the same time. These are all blocking, so by having each of them run on separate threads,
the server is able to carry on with program execution and handle input when
necessary. When initialized, the server first connects to the MetatdataServer where it receives a its own port number as well as a port number of a server already in the peer-to-peer network. The server then handles
the message from the MetatdataServer appropriately. If it did not receive a referred port number, it knows it is the first server in the network so it creates a new server socket with a new thread. If the server did receive a port number, it first creates a client socket, in a new thread, where it connects to the server with the referred port number and listens for incoming messages. It then creates a server socket using another thread and listens for incoming messages on the server socket. Finally, in the main thread, it listens for user input and handles it. The three main messages that it can handle are 'Stop', which closes all neighbor sockets and shuts down itself, 'TOPO', which lists the current network topology, and a filename, for downloading.


### How I implemented file downloading:
When a server requests to download a file, it first checks its own directory to see if it already has the file, if so, it will print a message to the terminal saying the file already exists in the server's directory. If not, it will send a message to its neighbors with its port number and the name of the file it wishes to download. If no neighbors have the file, nothing will print to the terminal and the file will not be downloaded. If another server has the file, it will first check if the requesting server is its neighbor, if so it will simply open the file, read the file contents, and send them to the other server. If it is not already connected to the requesting server, it will create a non-persistent connection with the requesting server, open the file, read the contents, send the file contents, and close the connection. When the requesting server is receiving a file to download, it will first move into its Downloads folder, create a file with the same name as the file it is going to receive, receive data from the server sending the file contents, write them to the file, and close the file when done.

### How to run:
* from the terminal, type 'python3 metatdata_server.py' to start the MetadataServer
* for each server you wish to add to the p2p network open a new terminal and do the following:
* type 'python3 server.py' to create a new server and follow the prompts on the terminal
* valid server names are: s1, s2, s3, s4, s5, S1, S2, S3, S4, S5
* valid flags to join the p2p network are: p2p, P2P
* type 'TOPO' into any server terminal to print out the current network topology
* type 'filename' where filename is the name of the file you wish to download (do not include the .txt)
* type 'Stop' into any server terminal to close all server connections and shutdown the p2p network
* to shutdown the MetadataServer use Ctrl-C

### Assumptions:
* Server names will always be of the specified format
* After all servers are closed, the user will close and restart the MetatdataServer before attempting to create a new p2p network
* All filenames will have the '.txt' extension and the user will not type that extension when requesting to download a file
* All files that will be downloaded will only have one line of data
* Downloads folders are only visible to the server to which they belong (so if S2 downloaded f1.txt and S3 requests f1.txt from S2, it will not get it from S2)
* The max number of servers that will contact the MetatdataServer to join the network is 10
