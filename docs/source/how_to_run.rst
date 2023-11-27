.. _how_to_run:

How to run the p2p-network: 
===========================
Starting the MetadataServer
---------------------------
1. From the terminal, type `python3 metadata_server.py` to start the MetadataServer

Starting the Servers
---------------------
1. For each server you wish to add to the p2p network, open a new terminal and do the following: 
    i. type `python3 server.py` to create a new server and follow the prompts on the terminal
    * valid server names are: s1, s2, s3, s4, s5, S1, S2, S3, S4, S5
    * valid flags to join the p2p network are: p2p, P2P

Other Important Information
---------------------------
* Type 'TOPO' into any server terminal to print out the current network topology
* Type 'filename' where filename is the name of the file you wish to download (do not include the .txt)
* Type 'Stop' into any server terminal to close all server connections and shutdown the p2p network 
* To shutdown the MetadataServer, use Ctrl-C

.. = indicates the main heading
.. - indicates a subheading
