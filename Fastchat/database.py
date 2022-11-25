import mysql.connector
"""Connecting to the database in localhost of server
"""
connection = mysql.connector.connect(
    host="localhost",
    user='dvp',
    password='Idvp@048',
    database='myTestDB'
)
cursor=connection.cursor()


#cursor.execute("DROP TABLE IF EXISTS CREDENTIALS")
# cursor.execute('''CREATE TABLE CREDENTIALS
#          (NAME TEXT ,
#          PASSWORD TEXT,
#          ONLINE INT,
#          PUBLIC_KEY BLOB,
#          PRIVATE_KEY BLOB);''')

def find_user(l):
    """This function checks whether a user's details are already available in the database

    Args:
        l (list): Contains ID, Password user entered

    Returns:
        int: 0 for no user name,1 for wrong password,2 for succesfull login
    """    
    cursor.execute("SELECT EXISTS(SELECT * from CREDENTIALS WHERE NAME='%s')" % (l[0]))
    foundname=cursor.fetchall()
    if(foundname[0][0]):
        cursor.execute("SELECT EXISTS(SELECT * from CREDENTIALS WHERE NAME='%s' AND PASSWORD='%s')" % (l[0],l[1]))
        foundpassword=cursor.fetchall()
        if(foundpassword[0][0]):
            return 2
        else:
            return 1
    else:
        return 0
    
    
def insert_user(l):
    """Inserts User Credentials to our Shared database.

    Args:
        l (list): Contains ID, Password and Public Key of user
    """
    state = "INSERT INTO CREDENTIALS (NAME,PASSWORD,ONLINE,PUBLIC_KEY,PRIVATE_KEY) VALUES (%s,%s,%s,%s,%s)"
    value = tuple(l)
    cursor.execute(state, value)
    create_table_newuser(l[0])
    connection.commit()
    
def get_all_names():
    """To get all users from database

    Returns:
        list: List of all users signed up till now
    """
    cursor.execute("SELECT NAME FROM CREDENTIALS")
    names=cursor.fetchall()
    n=[]
    for i in names:
        n.append(i[0])
    return n


def check_status(name):
    """Check online status of a user

    Args:
        name (string): Username for which status is checked

    Returns:
        int: 0 if offline, 1 if user is online
    """
    cursor.execute("SELECT ONLINE FROM CREDENTIALS WHERE NAME='%s' "% name)
    return int(cursor.fetchall()[0][0])
    
def update_status(l):
    """Update online status of a user

    Args:
        l (string): Username of user
    """
    cursor.execute("SELECT ONLINE FROM CREDENTIALS WHERE NAME='%s'" % (l))
    c=1-int(cursor.fetchall()[0][0])
    cursor.execute("UPDATE CREDENTIALS SET ONLINE = %s WHERE NAME ='%s'"% (c,l))
    connection.commit()
    
def recvPubKey(n):
    """Gets Public encryption of user

    Args:
        n (string): Username of user

    Returns:
        bytes: public key of user
    """
    cursor.execute("SELECT PUBLIC_KEY FROM CREDENTIALS WHERE NAME='%s' " % (n))
    key  = cursor.fetchall()
    #print(key)
    return key[0][0]

def recvPrivKey(n):
    """Gets Private encryption of user

    Args:
        n (string): Username of user

    Returns:
        bytes: private key of user
    """
    cursor.execute("SELECT PRIVATE_KEY FROM CREDENTIALS WHERE NAME='%s' " % (n))
    key  = cursor.fetchall()
    #print(key)
    return key[0][0]

def create_table_newuser(name):
    """Creates a new table for user chat history.

    Args:
        name (string): Username of user
    """
    cursor.execute('''CREATE TABLE %s
         (SENDER TEXT,
          MESSAGE BLOB,
          SENT INT);'''% name)
    
def store_offline_msg(name,sender,msg):
    """Stores offline messages to be sent to the user

    Args:
        name (string): Username of user to whom message is to be sent
        sender (string): Username of user who sent the message
        msg (bytes): Encrypted message
    """
    state="INSERT INTO "+name+" (SENDER,MESSAGE,SENT) VALUES (%s,%s,%s)"
    value=(sender,msg,0)
    cursor.execute(state,value)
    connection.commit()
    update_chat_history(name)

def store_msg(name,sender,msg):
    """Store message in the chat history

    Args:
        name (string): Username of user to whom message is to be sent
        sender (string): Username of user who sent the message
        msg (bytes): Encrypted message
    """
    state="INSERT INTO "+name+" (SENDER,MESSAGE,SENT) VALUES (%s,%s,%s)"
    value=(sender,msg,1)
    cursor.execute(state,value)
    connection.commit()
    update_chat_history(name)

def offline_msgs(name):
    """Gets all offline messages stored

    Args:
        name (string): Username of user

    Returns:
        list: list of tuples of encrypted unsent messages
    """
    cursor.execute("SELECT SENDER,MESSAGE FROM "+name+" WHERE SENT='0'")
    L= cursor.fetchall()
    cursor.execute("UPDATE "+name+" SET SENT='1'")
    connection.commit()
    return L

def create_grp(grp_name):
    """Create a new group table

    Args:
        grp_name (string): Name of group table.
    """
    name1=grp_name+"_participants"
    cursor.execute('''CREATE TABLE %s
         (NAME TEXT);'''% name1)
    name2=grp_name+"_chats"
    cursor.execute('''CREATE TABLE %s
         (NAME TEXT,
         MESSAGE BLOB);'''% name2)
    
def get_participants(grp_name):
    """Get participants of a group

    Args:
       grp_name (string): Name of group table.

    Returns:
        list: list of participants
    """
    name=grp_name+"_participants"
    cursor.execute("SELECT NAME FROM "+name+"")
    L= cursor.fetchall()
    r=[]
    for i in L:
        r.append(i[0])
    return r

def add_participant(name,grp_name):
    """Add participants to a group

    Args:
        name (string): Username of participant
        grp_name (string): Name of group table.
    """
    n1=grp_name+"_participants"
    state="INSERT INTO "+n1+" (NAME) VALUES (%s)"
    l=[name]
    value=tuple(l)
    cursor.execute(state,value)
    connection.commit()

def history_user(name):
    """Gets history of a user

    Args:
        name (string): Username of the user

    Returns:
        list: list of tuples of encrypted unsent messages
    """
    cursor.execute("SELECT SENDER,MESSAGE FROM "+name+"")
    r=cursor.fetchall()
    return r
   
def store_grp_chat(grp_name,name,msg):
    """Stores group history

    Args:
        grp_name (string): Name of group table.
        name (string): Username of the user
        msg (bytes): Encrypted message
    """
    n1=grp_name+"_chats"
    state="INSERT INTO "+n1+" (NAME,MESSAGE) VALUES (%s,%s)"
    l=[name,msg]
    value=tuple(l)
    cursor.execute(state,value)
    connection.commit()
    update_chat_history(grp_name)
    
def grp_history(grpname):
    """Gets history of a group

    Args:
        grp_name (string): Name of group table.

    Returns:
        list: list of tuples of encrypted unsent messages
    """
    n1=grpname+"_chats"
    cursor.execute("SELECT * FROM "+n1+" ")
    r=cursor.fetchall()
    return r

def online_users():
    """Gets available online users

    Returns:
        list: list of participants
    """
    cursor.execute("SELECT NAME FROM CREDENTIALS WHERE ONLINE='1'")
    r=cursor.fetchall()
    l=[]
    for i in r:
        l.append(i[0])
    return l

def no_of_msgs(name):
    """Number of messages stored

    Args:
        name (string): Name of table
    """
    cursor.execute("SELECT COUNT(*) FROM "+name+" ")
    return(cursor.fetchall()[0][0])

def update_chat_history(name):
    """Deleting old chat records and adding new records

    Args:
        name (string): Name of table

    Returns:
        list: returns list of chat records
    """
    if no_of_msgs(name)>2:
        cursor.execute("DELETE FROM "+name+" LIMIT 1")
        connection.commit()
        return (cursor.fetchall())

def grp_names():
    """Gets all groups names

    Returns:
        list: list of group names
    """
    cursor.execute("SELECT NAME FROM CREDENTIALS WHERE ONLINE='2'")
    r=cursor.fetchall()
    l=[]
    for i in r:
        l.append(i[0])
    return l
    
def available_users():
    """Gets all user names signed up to the server

    Returns:
        list: list of usernames
    """
    cursor.execute("SELECT NAME FROM CREDENTIALS")
    r=cursor.fetchall()
    l=[]
    for i in r:
        l.append(i[0])
    return l

def members():
    """Gets all user names signed up to the server

    Returns:
                list: list of usernames
    """
    cursor.execute("SELECT NAME FROM CREDENTIALS WHERE NOT ONLINE='2'")
    r=cursor.fetchall()
    l=[]
    for i in r:
        l.append(i[0])
    return l
    
def clients_s1():
    """Gets all clients connected to server 1

    Returns:
        list: list of usernames of clients
    """
    cursor.execute("SELECT SERVER_1 FROM CLIENTS")
    s=cursor.fetchall()[0][0]
    return s
def clients_s2():
    """Gets all clients connected to server 2

    Returns:
        list: list of usernames of clients
    """
    cursor.execute("SELECT SERVER_2 FROM CLIENTS")
    s=cursor.fetchall()[0][0]
    return s
def change_clients_s1(a):
    """Connects client information to server 1

    Args:
        a (int): changing load
    """
    a=int(a)
    cursor.execute("UPDATE CLIENTS SET SERVER_1=SERVER_1+%s"% (a))
    connection.commit()
def change_clients_s2(a):
    """Connects client information to server 2

    Args:
        a (int): changing load
    """
    cursor.execute("UPDATE CLIENTS SET SERVER_2=SERVER_2+%s"%(a))
    connection.commit()
# print(grp_names())
