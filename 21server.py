import socket
import threading
host = ''
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
Dict={}
name_of_rec={}
a={}

def handle(client,name):
    while True:
        message = client.recv(1024)
        if a[name]%2==0:
            print(name,name_of_rec[name],"kj")
            Dict[name_of_rec[name].decode('ascii')].send(message)
            a[name]=a[name]+1
        else:
            name_of_rec[name]=message
            print(name,name_of_rec[name],"ghj ")
            Dict[name_of_rec[name].decode('ascii')].send(name.encode('ascii'))
            a[name]=a[name]+1

def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        Dict[nickname]=client
        print("Nickname is {}".format(nickname))
        a[nickname]=1
        name_of_rec[nickname]=""
        thread = threading.Thread(target=handle, args=(client,nickname,))
        thread.start()
receive()