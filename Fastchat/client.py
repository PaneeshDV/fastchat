import socket
import time
import threading
import rsa
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import RSA

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


# take the server name and port name
LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'
#host = '192.168.126.212'
"""Allocating host and port numbers
"""
host = 'localhost'
port1 = 5555
port2 = 5556

# create a socket at client side
# using TCP / IP protocol
client=client = socket.socket(socket.AF_INET,
                    socket.SOCK_STREAM)
def connect():
    """This function takes care of connecting clients to one of the server.
    
    Connecting client with server carrying minimum number of clients. 
    """
    if(clients_s1()<=clients_s2()):  
        client.connect((host, port1))
        change_clients_s1(1)
        
    else:
        client.connect((host,port2))
        change_clients_s2(1)

global w
w=-1
global r
r=-1
def Login():
    """User performing login tasks until the login is complete
    """
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
    """Sigin Part: Performing login task of already existing users.
    """
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

    salt = "pandas" 
    master_key = PBKDF2(password, salt, count=1)  # bigger count = better
    def myrand(n):
        """Recreating the encryption keys

        Args:
            n (int): sets seed

        Returns:
            rsa key: keyset of a particular user
        """
        myrand.counter += 1
        return PBKDF2(master_key, "my_rand:%d" % myrand.counter, dkLen=n, count=1)
    myrand.counter = 0
    key = RSA.generate(1024, randfunc=myrand)
    global decryptor
    decryptor = PKCS1_OAEP.new(key)
    """private decryptor to decrypt the incoming messages. 
    """
    global nickname
    nickname=id    
    logging.basicConfig(filename=nickname+".log",
                    format='%(asctime)s ## %(message)s'
                    )
    global logger
    """Generating the logfile to note inputs and outputs from the client
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    connect()
    client.send(nickname.encode('ascii'))
    update_status(nickname)
    print_unread_msgs()
   

def sign_up():
    """Singing up for new user storing the login credentials and creating public and private keys based on the password of user
    """
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

    salt = "pandas" 
    master_key = PBKDF2(password, salt, count=1)  # bigger count = better
    def my_rand(n):
        """Recreating the encryption keys

        Args:
            n (int): sets seed

        Returns:
            rsa key: keyset of a particular user
        """
        my_rand.counter += 1
        return PBKDF2(master_key, "my_rand:%d" % my_rand.counter, dkLen=n, count=1)
    my_rand.counter = 0
    key = RSA.generate(1024, randfunc=my_rand)
    PubKey = key.publickey().exportKey('PEM')
    insert_user([id,password,1,PubKey,b'dummy'])
    """Storing credentials and Public Key of user in the database."""
    global decryptor
    decryptor = PKCS1_OAEP.new(key)
    """private decryptor to decrypt the incoming messages. 
    """
    global nickname
    nickname=id
    logging.basicConfig(filename=nickname+".log",
                    format='%(asctime)s ## %(message)s'
                    )
    """Generating the logfile to note inputs and outputs from the client
    """
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    connect()
    client.send(nickname.encode('ascii'))
    print_unread_msgs()

def print_unread_msgs():   
    """When an already existing user connects to the server, all the messages sent to user either DM or in a group while user was offline are displayed.

    The messages stored in database are in encrypted form, messages will be displayed after decrypting on client's side. 

    This function starts the client's receive thread and write thread.
    """
    message = client.recv(1024).decode('ascii')
    chat=(eval(message))
    if chat!=[]:
        print("----------------------------------------------------------")
        print("UNREAD MESSAGES:\n")
        logger.info("UNREAD MESSAGES:")
        for i in chat:
            if "@" in i[0]:
                        gname = i[0].split("@")[1]
                        PrivKey = recvPrivKey(gname)
                        key = rsa.PrivateKey.load_pkcs1(PrivKey)
                        msgs=rsa.decrypt(i[1],key).decode()
                        print(i[0]+":"+msgs)
                        logger.info(i[0]+":"+msgs)
            else:
                msgs=decryptor.decrypt(i[1]).decode()
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
    """This will clear lines in terminal of client's interface.

    Args:
        i (integer): Number of lines to be cleared.
    """
    for i in range(0,i):
        print(LINE_UP, end=LINE_CLEAR)
        
def receive():
    """This function receives messages from the servers and decrypts it based on the first keyword received from server.

    Images are received in chunks of size 1024 bytes.

    Messages received directly and that from group are seperated.

    Chat history with group or each user can also be displayed after decrypting messages stored in database. 
    """
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            msg=eval(message)
            if "Image" in eval(message)[0]:
                print(eval(message)[1], end=": ")
                filename = eval(message)[1]+"@"+nickname+"_"+eval(message)[2]
                img_copy = open(filename,'wb')
                while True:
                    recv_img = client.recv(1024)
                    if recv_img == b"%Image_Sent%":
                        break
                    img_copy.write(recv_img)     
                img_copy.close()
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
                            # recvname = i[0].split("-")[1]
                            # PrivKey = recvPrivKey(recvname)
                            # key = rsa.PrivateKey.load_pkcs1(PrivKey)
                            # decmsg = rsa.decrypt(i[1],key).decode()
                            # print(i[0]+": "+decmsg)
                            # logger.info(i[0]+": "+decmsg)
                            pass
                        else:
                            # PrivKey = recvPrivKey(nickname)
                            # key = rsa.PrivateKey.load_pkcs1(PrivKey)
                            # decmsg = rsa.decrypt(i[1],key).decode()
                            decmsg = decryptor.decrypt(i[1]).decode()
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
                decmsg = decryptor.decrypt(msg[2]).decode()
                print(msg[1]+": "+decmsg)
                logger.info(msg[1]+": "+decmsg)
        except:
            print("An error occured!")
            client.close()
            break

def DM_text():
    """This function sends text messages to server.

    Takes input message and receiver from the terminal. 

    Encrypts the message to be sent with receiver's PublicKey.
    """
    clear_terminal(3)
    while True:
        message_to = input("Whom do u want to send\n")
        logger.info("Whom do u want to send")
        logger.info(message_to)
        if not(message_to in available_users()):
            print("NO USER NAMED "+message_to+" EXISTS")
            logger.info("NO USER NAMED "+message_to+" EXISTS")
            continue
        m=input("type your message\n")
        logger.info("type your message")
        logger.info(m)
        clear_terminal(4)
        o="YOU->"+message_to+": "+m
        print(o)
        logger.info(o)
        PubKey = recvPubKey(message_to)
        enckey = RSA.importKey(PubKey)
        encryptor = PKCS1_OAEP.new(enckey)
        encmsg = encryptor.encrypt(m.encode('ascii'))
        msg_info=["DM",message_to,encmsg]
        client.send(str(msg_info).encode('ascii'))
        break     

def DM_img():
    """This function sends images from client to server.

    Takes the path of image file to be sent as input from the terminal.

    Sends chunks of 1024 bytes of data to server repeatedly until whole file is read. 
    """
    clear_terminal(3)
    while True:
        message_to = input("Whom do u want to send\n")
        logger.info("Whom do u want to send")
        logger.info(message_to)
        if not(message_to in available_users()):
            print("NO USER NAMED "+message_to+" EXIST")
            logger.info("NO USER NAMED "+message_to+" EXIST")
        path=input("type image path\n")
        logger.info("type image path")
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
    """This function sends group text messages to server.

    Takes input message and group to which it should be sent from the terminal.

    Sends message in Username@Groupname format.
    """
    clear_terminal(3)
    while True:
        message_to = input("which group do you want to send\n")
        logger.info("which group do you want to send")
        logger.info(message_to)
        if not(message_to in grp_names()):
            print("GROUP NAMED "+message_to+" DOES NOT EXIST")
            logger.info("GROUP NAMED "+message_to+" DOES NOT EXIST")
            continue
        m=input("type your message\n")
        logger.info("type your message")
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

def write():
    """This function performs task of writing from clients to server and splits the task to different functions and provides the interface.

    1- DM's

    2- Group Chats

    3- Creating a new group

    4- Adding participant to a group

    5- Display chat history with the specified user

    6- Display chat history from a specified group

    7- Displays all online users

    8- Displays all groups user present in

    9- Displays all users available 
    """
    print("---------------------------------INSTRUCTIONS----------------------------------\n")
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
          CLTRL-C FOR EXIT''')
    while True:
        e=input()
        logger.info(e)
        if int(e)==1:
            while True:
                cmd=input("ENTER :1 FOR TEXT , 2 FOR IMAGES\n")
                logger.info("ENTER :1 FOR TEXT , 2 FOR IMAGES")
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
                logger.info("ENTER :1 FOR TEXT , 2 FOR IMAGES")
                logger.info(cmd)
                if int(cmd)==1:
                    GRP_text()
                    break
                if int(cmd)==2:
                    break
                else:
                    print("ENTER ONLY 1 OR 2")
        elif int(e)==3:
            cmd=input("ENTER GROUP NAME\n")
            logger.info("ENTER GROUP NAME")
            logger.info(cmd)
            msg_info=["CREATE",cmd]
            client.send(str(msg_info).encode())
            print("CREATED GROUP NAMED "+cmd)
            logger.info("CREATED GROUP NAMED "+cmd)
        elif int(e)==4:
            while True:
                group_name=input("ENTER NAME OF GROUP\n")
                logger.info("ENTER NAME OF GROUP")
                logger.info(group_name)
                if group_name in grp_names():
                    break
                else:
                    print("GROUP NAMED "+group_name+" DOES NOT EXISTS")
                    logger.info("GROUP NAMED "+group_name+" DOES NOT EXISTS")
            while True:
                paricipant=input("ENTER THE NAME OF PARTICIPANT TO BE ADDED\n")
                logger.info("ENTER THE NAME OF PARTICIPANT TO BE ADDED")
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
                logger.info("ENTER NAME OF GROUP")
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
        else:
            print("PLEASE ENTER NUMBER BETWEEN 1 AND 9 ONLY")
        
# Starting Threads For Listening And Writing


Login()

