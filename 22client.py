import socket
import time
import threading
import rsa
from  database import insert_user
from database import find_user
from database import recvPubKey
from database import recvPrivKey
from database import update_status
from database import check_status
from database import store_msg
from database import store_offline_msg
# take the server name and port name
LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'
#host = '192.168.126.212'
host = 'localhost'
port = 5555

# create a socket at client side
# using TCP / IP protocol
client = socket.socket(socket.AF_INET,
                  socket.SOCK_STREAM)

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
    client.connect((host, port))
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
    client.connect((host, port))
    client.send(nickname.encode('ascii'))
    print_unread_msgs()

def print_unread_msgs():   
    # print("---------------------------------INSTRUCTIONS----------------------------------")
    message = client.recv(1024).decode('ascii')
    chat=(eval(message))
    if chat!=[]:
        print("----------------------------------------------------------")
        print("UNREAD MESSAGES:\n")
        for i in chat:
            if "@" in i[0]:
                        gname = i[0].split("@")[1]
                        PrivKey = recvPrivKey(gname)
                        key = rsa.PrivateKey.load_pkcs1(PrivKey)
                        msgs=rsa.decrypt(i[1],key).decode()
                        print(i[0]+":"+msgs)
            else:
                PrivKey = recvPrivKey(nickname)
                key = rsa.PrivateKey.load_pkcs1(PrivKey)
                msgs=rsa.decrypt(i[1],key).decode()
                print(i[0]+": "+msgs)
        print()
    else:
        print("NO UNREAD MESSAGES")
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
    write_thread = threading.Thread(target=write)
    write_thread.start()

def clear_terminal(i):
    for i in range(0,i):
        print(LINE_UP, end=LINE_CLEAR)
        
def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            msg=eval(message)
            if msg[0]=="GRP":
                gname = msg[1].split('@')[1]
                PrivKey = recvPrivKey(gname)
                key = rsa.PrivateKey.load_pkcs1(PrivKey)
                decmsg = rsa.decrypt(msg[2],key).decode()
                print(msg[1]+": "+decmsg)
            elif msg[0]=="HIS":
                for i in msg[1]:
                    if '@' in i[0]:
                        gname = i[0].split("@")[1]
                        PrivKey = recvPrivKey(gname)
                        key = rsa.PrivateKey.load_pkcs1(PrivKey)
                        decmsg = rsa.decrypt(i[1],key).decode()
                        print(i[0]+": "+decmsg)
                    else:
                        PrivKey = recvPrivKey(i[0])
                        key = rsa.PrivateKey.load_pkcs1(PrivKey)
                        decmsg = rsa.decrypt(i[1],key).decode()
                        print(i[0]+": "+decmsg)
            elif msg[0]=="GRP_HIS":
                PrivKey = recvPrivKey(msg[1])
                key = rsa.PrivateKey.load_pkcs1(PrivKey)
                print("Group Name",end=" ")
                print(msg[1])
                for i in msg[2]:
                    print(i[0],end=": ")
                    decmsg = rsa.decrypt(i[1],key).decode()
                    print(decmsg)
            else:
                PrivKey = recvPrivKey(nickname)
                key = rsa.PrivateKey.load_pkcs1(PrivKey)
                decmsg = rsa.decrypt(msg[1],key).decode()
                print(msg[0]+": "+decmsg)
        except:
            print("An error occured!")
            client.close()
            break

def DM_text():
    clear_terminal(3)
    message_to = input("Whom do u want to send\n")
    m=input("type your message\n")
    clear_terminal(4)
    o="YOU: "+m
    print(o)
    PubKey = recvPubKey(message_to)
    key = rsa.PublicKey.load_pkcs1(PubKey)
    encmsg = rsa.encrypt(m.encode('ascii'),key)
    msg_info=["DM",message_to,encmsg]
    client.send(str(msg_info).encode('ascii'))        

def DM_img():
    pass

def GRP_text():
    clear_terminal(3)
    message_to = input("which group do you want to send\n")
    m=input("type your message\n")
    clear_terminal(4)
    PubKey = recvPubKey(message_to)
    key = rsa.PublicKey.load_pkcs1(PubKey)
    encmsg = rsa.encrypt(m.encode('ascii'),key)
    msg_info=["GRP",message_to,encmsg]
    client.send(str(msg_info).encode('ascii'))
    print("YOU"+"@"+message_to+": "+m)

def GRP_img():
    pass

def write():
    print("---------------------------------INSTRUCTIONS----------------------------------\n")
    print('''ENTER:
          1-FOR-DMS,
          2-FOR GROUP CHATS ,
          3-FOR CREATING A GROUP ,
          4-FOR ADDING PARTICIPANT,
          5-FOR HISTORY
          6-FOR GROUP CHAT HISTORY
          CLTRL-C FOR EXIT''')
    while True:
        e=input()
        if int(e)==1:
            cmd=input("ENTER :1 FOR TEXT , 2 FOR IMAGES\n")
            if int(cmd)==1:
                DM_text()
            if int(cmd)==2:
                DM_img()
        if int(e)==2:
            cmd=input("ENTER :1 FOR TEXT , 2 FOR IMAGES\n")
            if int(cmd)==1:
                GRP_text()
            if int(cmd)==2:
                GRP_img()
        if int(e)==3:
            cmd=input("ENTER GROUP NAME\n")
            msg_info=["CREATE",cmd]
            client.send(str(msg_info).encode())
        if int(e)==4:
            group_name=input("ENTER NAME OF GROUP\n")
            paricipant=input("ENTER THE NAME OF PARTICIPANT TO BE ADDED\n")
            msg_info=["ADD",group_name,paricipant]
            client.send(str(msg_info).encode())
        if int(e)==5:
            msg_info=["HIS"]
            client.send(str(msg_info).encode())
        if int(e)==6:
            group_name=input("ENTER GROUP NAME")
            msg_info=["GRP_HIS",group_name]
            client.send(str(msg_info).encode())
# Starting Threads For Listening And Writing


Login()