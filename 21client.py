import socket
import threading
from  database import insert_user
from database import find_user
# take the server name and port name
LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'
#host = '192.168.126.212'
host = 'localhost'
port = 55555

# create a socket at client side
# using TCP / IP protocol
client = socket.socket(socket.AF_INET,
                  socket.SOCK_STREAM)

def Login():
    print("choose whether are an\n 1)old \n 2)new one")
    i=int(input())
    while(i!=1 and i!=2):
        print("enter only 1 or 2")
        i=int(input())
        
    if i==1:
        sign_in() 
    if i==2:
        sign_up()

def sign_in():
    print("Enter your Id:")
    id=input()
    print("Enter your password: ")
    password=input()
    print("user found:--------------")
    print(find_user([id,password,0,0,0]))
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
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
    write_thread = threading.Thread(target=write)
    write_thread.start()


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

    insert_user([id,password,0,0,0])
    global nickname
    nickname=id
    client.connect((host, port))
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
    write_thread = threading.Thread(target=write)
    write_thread.start()
global a           
a=1    
global name_of_rec
name_of_rec="" 
def print_msg(name,message):
    global a
    global name_of_rec
    if(a%2==0):
        print(name+" :"+message)
    else: 
        name_of_rec=message
 
def receive():
    global a
    while True:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                print("nickname")
                client.send(nickname.encode('ascii'))
            else:
                print_msg(name_of_rec,message)
                a=a+1



def write():
    while True:
        message_to = input("Whom do u want to send\n")
        # print(LINE_UP, end=LINE_CLEAR)
        # print(LINE_UP, end=LINE_CLEAR)
        client.send(message_to.encode('ascii'))
        m=input("type your message\n")
        # print(LINE_UP, end=LINE_CLEAR)
        message=message_to+":"+m
        o=nickname+":"+m
        print(o)
        client.send(m.encode('ascii'))
# Starting Threads For Listening And Writing


Login()