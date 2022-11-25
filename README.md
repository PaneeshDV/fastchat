# Fastchat
# CS251 Project

## Running the Project:
1) Databases need to be created initialy
2) Dont run both server1 and server2 simultaneously because server1 is main server
* $1 ,$2 , $3 are 3 ports
* Run python3 server1.py $1 $3 
* next Run python3 server2.py $2 $3
* next Run python3 client.py $1 $2
3) Next instructions will be given in the terminal.
4) Final commit contains 3 folders
* Fastchat contains all the implementation
* Performance analysis on 1st implementation
* Performance analysis on 2nd implementation

## Main Features Implemented
1) Direct Messaging 
2) Group Chats 
3) Creating and Adding participants
3) Chat Histories
4) Unread Messages
5) Active and Non Active participants


## Socket Programming
1) We create a listening socket at server,and bind it to port
2) When the client connects to server he chooses an id and a password.
3) We start a receive and a write thread in client,and on ehandle thread in server

## Direct Messaging
1) If Client-A wants to send a message to B, Client-A sends message B:XXXX to server(XXXX is encrypted msg using B's public key).
2) Server sends message to B in the format A:XXXX. Server stores the message in both A and B's history.If B is offline we store the message with a tag of not sent.
3) B decryptes the message using its private key.

## Group Messages
1) Interface allows the user to create a group with admin as user. An option of adding participants is provided for admin of group.
2) When a group is created we generate public and private keys for the group.
3) Whenever user wants to send a message in the group
* Encrypt the message with groups public key.
* Server sends to all users which are online. Receivers decrypt using groups private keys.
* Messages will be stored in offline_msgs if the user is offline

## Chat Histories
1) We have a user specific table in the databases.We store all his chats(irrespective of unseen msgs and seen msgs)
2) Whenever the user comes online we collect all unseen messages from the table and display them. We show difference between DM's and Groupchats in unread messages
3) When user asks for history we collect the last 5 messages and display them

## RSA-Encryption
1) We generate a pubic and private key for every client
2) Whenever a user wants to send a message he should encrypt with receivers public key
3) Message will be set in the format such that server knows whom to send.Receiver decrptes it using its private key
4) Server has all the public keys

## DataBase-Management
1) We create a database which stores all user-ids,online(bool),public keys.
2) For everyuser we create a seperate table having offline_msgs,chat histories.
3) When a new group is created we create two tables on having participants and the other having chats.
4) Function of adding user,finding user,removing user,get_unread_msgs,get_history_user,display_online_users,display_all_grps are implemented
5) A total of 30 functins were implemented 

### Contributions
* *210050048-Paneesh* DataBase, RSA-Encryption, Image sending, Group Chats ,Chat History, Multiple servers ,Sphinx documentation
* *210050069-Nikhil* Socket programming, Direct messages, Group Chats, Multiple servers, Interface, Performance Analysis
* *210050096-Pranay* DataBase, Chat Histories, Interface, Load-Balance, Presentation ,Multiple servers, Performance Analysis
 
## Multiple Servers-Load Balance
### Round Robin Method:
#### Implementation 1:
* Whenever a user logs in,we decide the server to which he should connect by checking the load on both servers.
* If A and B are 2 clients and are connected to the same server chatting will be similar to single server mechanism.If the user B is not connected to same server server1 sends a message to server2 and server2 sends to B.
* When user logs out we decrease the load on server.
* *Advantages*:When more active clients are present on different server,the load will be equally distributed on both servers
#### Implementation 2:
* We randomly select the server and assign it.
#### Implementation 3:
* We assign server1 and server2 alternatively irrespective of users logging out.
##### We use a mix of all these implementation so that active clients are equally scattered.

### Performance Analysis:
* [performance_analysis_pdf](http://shorturl.at/fvR19)
