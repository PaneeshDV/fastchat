#!/usr/bin/env python3
import socket
import time
import threading
import rsa
from  database import insert_user
from database import find_user
from database import recvPubKey
from database import recvPrivKey
from database import update_status
from database import online_users
from database import grp_names
from database import available_users
from database import members
import logging
from database import clients_s1
from database import change_clients_s1
from database import clients_s2
from database import change_clients_s2
import sys
import random
# Create and configure logger


# take the server name and port name
LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'
#host = '192.168.126.212'
host = 'localhost'
# port1 = 55555
# port2=55556
port1=int(sys.argv[1])
port2=int(sys.argv[2])
# create a socket at client side
# using TCP / IP protocol
client=client = socket.socket(socket.AF_INET,
                    socket.SOCK_STREAM)
def connect():
    # if(clients_s1()<=clients_s2()):  
    #     client.connect((host, port1))
    #     change_clients_s1(1)
        
    # else:
    #     client.connect((host,port2))
    #     change_clients_s2(1)
    r1=random.randrange(2)
    if(r1==1):
        client.connect((host, port1))
    else:
        client.connect((host,port2))

global w
w=-1
global r
r=-1
def Login():
    print("ENTER:\n    1 FOR OLD USER\n    2 FOR NEW USER")
    i=int(input())
    while(i!=1 and i!=2):
        print("enter only 1 or 2")
        i=int(input())
    if i==1:
        clear_terminal(4)
        sign_in() 
    if i==2:
        clear_terminal(4)
        sign_up()

def sign_in():
    print("Enter your Id:")
    id=input()
    print("Enter your password: ")
    password=input()
    while find_user([id,password,0,0,0])!=2:
        if find_user([id,password,0,0,0])==1:
            print("password is incorrect enter again")
        if find_user([id,password,0,0,0])==0:
            print("Please first signup to enjoy the services")
            sign_up()
            return
        print("Enter your Id:")
        id=input()
        print("Enter your password: ")
        password=input()
    global nickname
    nickname=id    
    logging.basicConfig(filename="clients.log",
                    format='%(asctime)s %(message)s\n'
                    )
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    connect()
    client.send(nickname.encode('ascii'))
    update_status(nickname)
    print_unread_msgs()
   

def sign_up():
    print("choose your id:")
    id=input()
    print("Choose your password:")
    password=input()
    while find_user([id,password,0,0,0])!=0:
        print("choose again:")
        print("choose your id:")
        id=input()
        print("Choose your password:")
        password=input()
    pubKey, privKey = rsa.newkeys(512)
    insert_user([id,password,1,pubKey.save_pkcs1("PEM"),privKey.save_pkcs1("PEM")])
    global nickname
    nickname=id
    logging.basicConfig(filename=nickname+".log",
                    format='%(asctime)s %(message)s\n'
                    )
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info(nickname+"logged_in") #1

    connect()
    client.send(nickname.encode('ascii'))
    print_unread_msgs()

def print_unread_msgs():   
    # print("---------------------------------INSTRUCTIONS----------------------------------")
    message = client.recv(1024).decode('ascii')
    chat=(eval(message))
    if chat!=[]:
        print("----------------------------------------------------------")
        print("UNREAD MESSAGES:\n")
        logger.info("UNREAD MESSAGES:\n")
        for i in chat:
            if "@" in i[0]:
                        gname = i[0].split("@")[1]
                        PrivKey = recvPrivKey(gname)
                        key = rsa.PrivateKey.load_pkcs1(PrivKey)
                        msgs=rsa.decrypt(i[1],key).decode()
                        print(i[0]+":"+msgs)
                        logger.info(i[0]+":"+msgs)
            else:
                PrivKey = recvPrivKey(nickname)
                key = rsa.PrivateKey.load_pkcs1(PrivKey)
                msgs=rsa.decrypt(i[1],key).decode()
                print(i[0]+": "+msgs)
                logger.info(i[0]+": "+msgs)
        print()
    else:
        print("NO UNREAD MESSAGES")
        logger.info("NO UNREAD MESSAGES")
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
    write_thread = threading.Thread(target=write)
    write_thread.start()

def clear_terminal(i):
    for i in range(0,i):
        print(LINE_UP, end=LINE_CLEAR)
        
def receive():
    while True:
        #try:
            message = client.recv(1024).decode('ascii')
            msg=eval(message)
            if "Image" in eval(message)[0]:
                print(eval(message)[1], end=": ")
                #sz=int(eval(message)[0][5:])
                filename = eval(message)[1]+"@"+nickname+"_"+eval(message)[2]
                img_copy = open(filename,'wb')
                #client.send("ffff".encode())
                #recv_img = client.recv(sz*3)
                while True:
                    recv_img = client.recv(1024)
                    if recv_img == b"%Image_Sent%":
                        break
                    img_copy.write(recv_img)     
                img_copy.close()
                    #recv_img=client.recv(1024)
                print("You have an image saved as ",filename)
                logger.info("You have an image saved as "+filename)
            elif msg[0]=="GRP":
                gname = msg[1].split('@')[1]
                PrivKey = recvPrivKey(gname)
                key = rsa.PrivateKey.load_pkcs1(PrivKey)
                decmsg = rsa.decrypt(msg[2],key).decode()
                print(msg[1]+": "+decmsg)
                logger.info(msg[1]+": "+decmsg)
            elif msg[0]=="HIS":
                print("---------------------------")
                for i in msg[1]:
                    if '@' in i[0]:
                        gname = i[0].split("@")[1]
                        PrivKey = recvPrivKey(gname)
                        key = rsa.PrivateKey.load_pkcs1(PrivKey)
                        decmsg = rsa.decrypt(i[1],key).decode()
                        print(i[0]+": "+decmsg)
                        logger.info(i[0]+": "+decmsg)
                    else:
                        if "-" in i[0]:
                            recvname = i[0].split("-")[1]
                            PrivKey = recvPrivKey(recvname)
                            key = rsa.PrivateKey.load_pkcs1(PrivKey)
                            decmsg = rsa.decrypt(i[1],key).decode()
                            print(i[0]+": "+decmsg)
                            logger.info(i[0]+": "+decmsg)
                        else:
                            PrivKey = recvPrivKey(nickname)
                            key = rsa.PrivateKey.load_pkcs1(PrivKey)
                            decmsg = rsa.decrypt(i[1],key).decode()
                            print(i[0]+": "+decmsg)
                            logger.info(i[0]+": "+decmsg)
                print("---------------------------")
                
            elif msg[0]=="GRP_HIS":
                print("---------------------------")
                PrivKey = recvPrivKey(msg[1])
                key = rsa.PrivateKey.load_pkcs1(PrivKey)
                print("Group Name",end=" ")
                print(msg[1])
                logger.info("Group Name "+msg[1])
                for i in msg[2]:
                    print(i[0],end=": ")
                    decmsg = rsa.decrypt(i[1],key).decode()
                    print(decmsg)
                    logger.info(i[0]+": "+decmsg)
                print("---------------------------")
                
            elif msg[0]=="DM":
                PrivKey = recvPrivKey(nickname)
                key = rsa.PrivateKey.load_pkcs1(PrivKey)
                decmsg = rsa.decrypt(msg[2],key).decode()
                if decmsg=="EXIT":
                    # time.sleep(1)
                    break
                #print(msg[1]+": "+decmsg)
                logger.info(decmsg)
        # except:
        #     print("An error occured!")
        #     client.close()
        #     break

def DM_text():
    clear_terminal(3)
    while True:
        message_to = input("Whom do u want to send\n")
        logger.info("Whom do u want to send\n")
        logger.info(message_to)
        if not(message_to in available_users()):
            print("NO USER NAMED "+message_to+" EXISTS")
            logger.info("NO USER NAMED "+message_to+" EXISTS")
            continue
        m=input("type your message\n")
        logger.info("type your message\n")
        logger.info(m)
        clear_terminal(4)
        o="YOU->"+message_to+": "+m
        #print(o)
        # logger.info(o)
        PubKey = recvPubKey(message_to)
        key = rsa.PublicKey.load_pkcs1(PubKey)
        encmsg = rsa.encrypt(m.encode('ascii'),key)
        msg_info=["DM",message_to,encmsg]
        client.send(str(msg_info).encode('ascii'))
        break     

def DM_img():
    clear_terminal(3)
    while True:
        message_to = input("Whom do u want to send\n")
        logger.info("Whom do u want to send\n")
        logger.info(message_to)
        if not(message_to in available_users()):
            print("NO USER NAMED "+message_to+" EXIST")
            logger.info("NO USER NAMED "+message_to+" EXIST")
        path=input("type image path\n")
        logger.info("type image path\n")
        logger.info(path)
        filename = path.split("/")[-1]
        isz = "Image" 
        img_list = [isz,message_to,filename]
        client.send(str(img_list).encode('ascii'))
        imgfile = open(path,'rb')
        image=imgfile.read(1024)
        while image:
            client.send(image)
            image=imgfile.read(1024)
        time.sleep(0.1)
        client.send(b"%Image_Sent%")
        imgfile.close()
        
        
        
        break

def GRP_text():
    clear_terminal(3)
    while True:
        message_to = input("which group do you want to send\n")
        logger.info("which group do you want to send\n")
        logger.info(message_to)
        if not(message_to in grp_names()):
            print("GROUP NAMED "+message_to+" DOES NOT EXIST")
            logger.info("GROUP NAMED "+message_to+" DOES NOT EXIST")
            continue
        m=input("type your message\n")
        logger.info("type your message\n")
        logger.info(m)
        clear_terminal(4)
        PubKey = recvPubKey(message_to)
        key = rsa.PublicKey.load_pkcs1(PubKey)
        encmsg = rsa.encrypt(m.encode('ascii'),key)
        msg_info=["GRP",message_to,encmsg]
        client.send(str(msg_info).encode('ascii'))
        print("YOU"+"@"+message_to+": "+m)
        logger.info("YOU"+"@"+message_to+": "+m)
        break

def GRP_img():
    pass

def write():
    print("---------------------------------INSTRUCTIONS----------------------------------\n")
    # global logger
    logger.info("---------------------------------INSTRUCTIONS----------------------------------\n")
    print('''ENTER:
          1-FOR-DMS,
          2-FOR GROUP CHATS ,
          3-FOR CREATING A GROUP ,
          4-FOR ADDING PARTICIPANT,
          5-FOR HISTORY
          6-FOR GROUP CHAT HISTORY
          7-FOR AVAILABLE ONLINE USERS
          8-FOR AVAILBALE GROUPS
          9-FOR AVAILABE USERS
          10-FOR EXIT
          CLTRL-C FOR EXIT''')
    logger.info('''ENTER:
          1-FOR-DMS,
          2-FOR GROUP CHATS ,
          3-FOR CREATING A GROUP ,
          4-FOR ADDING PARTICIPANT,
          5-FOR HISTORY
          6-FOR GROUP CHAT HISTORY
          7-FOR AVAILABLE ONLINE USERS
          8-FOR AVAILBALE GROUPS
          9-FOR AVAILABE USERS
          10-TO EXIT
          CLTRL-C FOR EXIT''')
    while True:
                e=input()
                logger.info(e)
                if int(e)==1:
                    while True:
                        cmd=input("ENTER :1 FOR TEXT , 2 FOR IMAGES\n")
                        logger.info("ENTER :1 FOR TEXT , 2 FOR IMAGES\n")
                        logger.info(cmd)
                        
                        if int(cmd)==1:
                            DM_text()
                            break
                        elif int(cmd)==2:
                            DM_img()
                            break
                        else:
                            print("ENTER ONLY 1 OR 2")
                elif int(e)==2:
                    while True:
                        cmd=input("ENTER :1 FOR TEXT , 2 FOR IMAGES\n")
                        logger.info("ENTER :1 FOR TEXT , 2 FOR IMAGES\n")
                        logger.info(cmd)
                        if int(cmd)==1:
                            GRP_text()
                            break
                        if int(cmd)==2:
                            GRP_img()
                            break
                        else:
                            print("ENTER ONLY 1 OR 2")
                elif int(e)==3:
                    cmd=input("ENTER GROUP NAME\n")
                    logger.info("ENTER GROUP NAME\n")
                    logger.info(cmd)
                    msg_info=["CREATE",cmd]
                    client.send(str(msg_info).encode())
                    print("CREATED GROUP NAMED "+cmd)
                    logger.info("CREATED GROUP NAMED "+cmd)
                elif int(e)==4:
                    while True:
                        group_name=input("ENTER NAME OF GROUP\n")
                        logger.info("ENTER NAME OF GROUP\n")
                        logger.info(group_name)
                        if group_name in grp_names():
                            break
                        else:
                            print("GROUP NAMED "+group_name+" DOES NOT EXISTS")
                            logger.info("GROUP NAMED "+group_name+" DOES NOT EXISTS")
                    while True:
                        paricipant=input("ENTER THE NAME OF PARTICIPANT TO BE ADDED\n")
                        logger.info("ENTER THE NAME OF PARTICIPANT TO BE ADDED\n")
                        logger.info(paricipant)
                        if paricipant in members():
                            break
                        else:
                            print("COULD NOT FIND USER"+paricipant+"IN DATABASE")
                            logger.info("COULD NOT FIND USER"+paricipant+"IN DATABASE")
                    msg_info=["ADD",group_name,paricipant]
                    client.send(str(msg_info).encode())
                    print("ADDED SUCCESSFULLY "+paricipant+" in "+group_name)
                    logger.info("ADDED SUCCESSFULLY "+paricipant+" in "+group_name)
                elif int(e)==5:
                    msg_info=["HIS"]
                    client.send(str(msg_info).encode())
                elif int(e)==6:
                    while True:
                        group_name=input("ENTER NAME OF GROUP\n")
                        logger.info("ENTER NAME OF GROUP\n")
                        logger.info(group_name)
                        if group_name in grp_names():
                            break
                        else:
                            print("GROUP NAMED "+group_name+" DOES NOT EXISTS")
                            logger.info("GROUP NAMED "+group_name+" DOES NOT EXISTS")
                    msg_info=["GRP_HIS",group_name]
                    client.send(str(msg_info).encode())
                elif int(e)==7:
                    users=online_users()
                    print("-----------------------------")
                    for i in users:
                        print(i)
                        logger.info(i)
                    print("------------------------------")
                elif int(e)==8:
                    grps=grp_names()
                    print("------------------------------")
                    for i in grps:
                        print(i)
                        logger.info(i)
                    print("--------------------------------")
                elif int(e)==9:
                    print("-------------------------------")
                    for i in available_users():
                        print (i)
                        logger.info(i)
                    print("---------------------------------")
                elif int(e)==10:
                    update_status(nickname)
                    client.send(str(["DM",nickname,"EXIT"]).encode())
                    break
                else:
                    print("PLEASE ENTER NUMBER BETWEEN 1 AND 9 ONLY")
        
# Starting Threads For Listening And Writing


Login()

# import socket

# client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# client.connect(('localhost',5555))
# file=open('logo.png','rb')
# image=file.read(1024)
# while image:
#     client.send(image)
#     image=file.read(1024)
# file.close()
