import socket
import threading
import time
host = ''
port = 5555
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

# Lists For Clients and Their Nicknames
Dict={}
name_of_rec={}
a={}

# def add_clinet(message): 
#     for i in Dict:
#         Dict[i].send(message)

def DM(msg_info,name):
    new_msg_info=str([name,msg_info[2]])
    receiver=msg_info[1]
    if(check_status(receiver)):
        Dict[receiver].send(new_msg_info.encode())
        store_msg(name,name,msg_info[2])
        store_msg(receiver,name,msg_info[2])
    else:
        store_offline_msg(receiver,name,msg_info[2])
        store_msg(name,name,msg_info[2])
        
def GRP(msg_info,name):
    sender=name+"@"+msg_info[1]
    new_msg_info=str(["GRP",sender,msg_info[2]])
    group_members=get_participants(msg_info[1])
    for i in group_members:
        if(i==name):
            store_msg(name,sender,msg_info[2])
            continue
        if check_status(i):
            Dict[i].send(new_msg_info.encode())
            store_msg(i,sender,msg_info[2])
        else:
            store_offline_msg(i,sender,msg_info[2])
    store_grp_chat(msg_info[1],name,msg_info[2])
def handle(client,name):
        while True:
            message = client.recv(1024)
            if not message:
                update_status(name)
                return
            else:
                msg_info=eval(message.decode())
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
    l=offline_msgs(name)
    client.send(str(l).encode())     
    return   

def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))
        nickname = client.recv(1024).decode('ascii')
        Dict[nickname]=client
        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        # add_clinet("{} joined!".format(nickname).encode('ascii'))
        s=""
        for i in Dict:
            s=s+i+","
        s=s[:-1]
        s=s+" are participants "
        a[nickname]=1
        name_of_rec[nickname]=""
        # client.send(s.encode('ascii'))
        send_offline_msgs(client,nickname)
        
        thread = threading.Thread(target=handle, args=(client,nickname,))
        thread.start()
        
receive()
