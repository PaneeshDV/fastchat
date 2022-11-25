import socket
import threading
import time
host = ''
port = 5556
port_server=5557
import rsa
from database import insert_user
from database import update_status
from database import check_status
from database import store_msg
from database import store_offline_msg
from database import offline_msgs
from database import get_participants
from database import add_participant
from database import create_grp
from database import history_user
from database import store_grp_chat
from database import grp_history
# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.connect((host,port_server))
# Lists For Clients and Their Nicknames
Dict={}
name_of_rec={}
a={}


def server_recv():
    """This function receives images sent by client to the server
    
     reads chunks of size 1024 bytes at a time.
    """
    while True:
        msg=s2.recv(1024)
        message=eval(msg.decode())
        if "Image" in message[0]:
            receiver=message[3]
            new_msg_info=str([message[0],message[1],message[2]])
            Dict[receiver].send(new_msg_info.encode())
            img_cpy=open("s",'wb')
            while True:
                img = s2.recv(1024)
                if img == b"%Image_Sent%":
                    break
                Dict[receiver].send(img)
                img_cpy.write(img)               
            time.sleep(0.1)
            Dict[receiver].send(b"%Image_Sent%")
            img_cpy.close()      
        else:
            new_msg=str(message[1:])
            Dict[message[0]].send(new_msg.encode())

def DM(msg_info,name):
    """This handle's the DM text messages to be sent from server to a client in encrypted form

    Args:
        msg_info (list): contains receiver username and encrypted message to be sent
        name (string): Username of receiver
    """
    new_msg_info=str(["DM",name,msg_info[2]])
    receiver=msg_info[1]
    store_msg(name,"YOU"+"-"+receiver,msg_info[2])
    if(check_status(receiver)):
        if receiver in Dict:
            Dict[receiver].send(new_msg_info.encode())
        else:
            msg=str([receiver,"DM",name,msg_info[2]])
            s2.send(msg.encode())
        store_msg(receiver,name,msg_info[2])
    else:
        store_offline_msg(receiver,name,msg_info[2])

def DM_IMG(msg_info,name,client):
    """This handle's the DM images to be sent from server to a client

    Args:
        msg_info (list): contains Keyword and name of sender
        client (socket): socket object of client who sent the request
        name (string): Username of receiver
    """
    receiver=msg_info[1]
    #sz = int(msg_info[0][5:])
    if(check_status(receiver)):
            new_msg_info=str([msg_info[0],name,msg_info[2]])
            if receiver in Dict:
                Dict[receiver].send(new_msg_info.encode())
                img_cpy=open("s",'wb')
                while True:
                    img = client.recv(1024)
                    if img == b"%Image_Sent%":
                        break
                    Dict[receiver].send(img)
                    img_cpy.write(img)
                time.sleep(0.1)
                Dict[receiver].send(b"%Image_Sent%")
                img_cpy.close()
            else:
                msg=str([msg_info[0],name,msg_info[2],receiver])
                s2.send(msg.encode())
                img_cpy=open("s",'wb')
                while True:
                    img = client.recv(1024)
                    if img == b"%Image_Sent%":
                        break
                    s2.send(img)
                    img_cpy.write(img) 
                time.sleep(0.1)
                s2.send(b"%Image_Sent%")
                img_cpy.close()
                
    else:
            while True:
                img = client.recv(1024)
                if img == b"%Image_Sent%":
                    break
        
        
def GRP(msg_info,name):
    """This function sends the message sent by a user to all participants of group

    Args:
        msg_info (list): contains Keyword and name of sender
        name (string): Name of the group
    """
    sender=name+"@"+msg_info[1]
    new_msg_info=str(["GRP",sender,msg_info[2]])
    group_members=get_participants(msg_info[1])
    for i in group_members:
        if(i==name):
            store_msg(name,sender,msg_info[2])
            continue
        if check_status(i):
            store_msg(i,sender,msg_info[2])
            if i in Dict:
                Dict[i].send(new_msg_info.encode())
            else:
                msg=str([i,"GRP",sender,msg_info[2]])
                s2.send(msg.encode())
        else:
            store_offline_msg(i,sender,msg_info[2])
    store_grp_chat(msg_info[1],name,msg_info[2])

def handle(client,name):
    """This is main function of server.

    It handles all the requests made by client to the server.

    This splits the task of handling requests to different functions based on the type of requests.

    Args:
        client (socket): socket object of client who sent the request
        name (string): Username of receiver
    """
    while True:
            message = client.recv(1024)
            if not message:
                update_status(name)
                return
            else:
                msg_info=eval(message.decode())
                if "Image" in msg_info[0]:
                    DM_IMG(msg_info,name,client)
                if msg_info[0]=="DM":
                    DM(msg_info,name)
                if msg_info[0]=="GRP":
                    GRP(msg_info,name)
                if msg_info[0]=="CREATE":
                    create_grp(msg_info[1])
                    pubKey, privKey = rsa.newkeys(512)
                    insert_user([msg_info[1],"GROUP",2,pubKey.save_pkcs1("PEM"),privKey.save_pkcs1("PEM")])
                    add_participant(name,msg_info[1])
                if msg_info[0]=="ADD":
                    add_participant(msg_info[2],msg_info[1])
                if msg_info[0]=="HIS":
                    msgs=history_user(name)
                    new_msg_info=str(["HIS",msgs])
                    client.send(new_msg_info.encode())
                if msg_info[0]=="GRP_HIS":
                    msgs=grp_history(msg_info[1])
                    new_msg_info=str(["GRP_HIS",msg_info[1],msgs])
                    client.send(new_msg_info.encode())

def send_offline_msgs(client,name):
    """This function sends messages to a user while user was offline.

    It gets messages stored from the database.

    Args:
        client (socket): socket object of client who sent the request
        name (string): Username of receiver
    """
    l=offline_msgs(name)
    client.send(str(l).encode())     
    return   

def receive():
    """This function accepts connection from the client.

    Also starts the handle thread, one for each client connected.
    """
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))
        nickname = client.recv(1024).decode('ascii')
        Dict[nickname]=client
        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        # add_clinet("{} joined!".format(nickname).encode('ascii'))
        a[nickname]=1
        send_offline_msgs(client,nickname)
        
        thread = threading.Thread(target=handle, args=(client,nickname,))
        thread.start()
server_thr=threading.Thread(target=server_recv)
server_thr.start()
receive()