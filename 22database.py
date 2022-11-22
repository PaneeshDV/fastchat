import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user='dvp',
    password='Idvp@048',
    database='myTestDB'
)

#print(mydb)
cursor=connection.cursor()


#cursor.execute("DROP TABLE IF EXISTS CREDENTIALS")
# cursor.execute('''CREATE TABLE CREDENTIALS
#          (NAME TEXT ,
#          PASSWORD TEXT,
#          ONLINE INT,
#          PUBLIC_KEY BLOB,
#          PRIVATE_KEY BLOB);''')

def find_user(l):
    ''' 0 for no user name,1 for wrong password,2 for succesfull login'''
    
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
    state = "INSERT INTO CREDENTIALS (NAME,PASSWORD,ONLINE,PUBLIC_KEY,PRIVATE_KEY) VALUES (%s,%s,%s,%s,%s)"
    value = tuple(l)
    cursor.execute(state, value)
    create_table_newuser(l[0])
    connection.commit()
    
def get_all_names():
    cursor.execute("SELECT NAME FROM CREDENTIALS")
    names=cursor.fetchall()
    n=[]
    for i in names:
        n.append(i[0])
    return n


def check_status(name):
    cursor.execute("SELECT ONLINE FROM CREDENTIALS WHERE NAME='%s' "% name)
    return int(cursor.fetchall()[0][0])
    
def update_status(l):
    cursor.execute("SELECT ONLINE FROM CREDENTIALS WHERE NAME='%s'" % (l))
    c=1-int(cursor.fetchall()[0][0])
    cursor.execute("UPDATE CREDENTIALS SET ONLINE = %s WHERE NAME ='%s'"% (c,l))
    connection.commit()
    
def recvPubKey(n):
    cursor.execute("SELECT PUBLIC_KEY FROM CREDENTIALS WHERE NAME='%s' " % (n))
    key  = cursor.fetchall()
    #print(key)
    return key[0][0]

def recvPrivKey(n):
    cursor.execute("SELECT PRIVATE_KEY FROM CREDENTIALS WHERE NAME='%s' " % (n))
    key  = cursor.fetchall()
    #print(key)
    return key[0][0]

def create_table_newuser(name):
    cursor.execute('''CREATE TABLE %s
         (SENDER TEXT,
          MESSAGE BLOB,
          SENT INT);'''% name)
    
def store_offline_msg(name,sender,msg):
    state="INSERT INTO "+name+" (SENDER,MESSAGE,SENT) VALUES (%s,%s,%s)"
    value=(sender,msg,0)
    cursor.execute(state,value)
    connection.commit()

def store_msg(name,sender,msg):
    state="INSERT INTO "+name+" (SENDER,MESSAGE,SENT) VALUES (%s,%s,%s)"
    value=(sender,msg,1)
    cursor.execute(state,value)
    connection.commit()

def offline_msgs(name):
    cursor.execute("SELECT SENDER,MESSAGE FROM "+name+" WHERE SENT='0'")
    L= cursor.fetchall()
    cursor.execute("UPDATE "+name+" SET SENT='1'")
    connection.commit()
    return L

def create_grp(grp_name):
    name1=grp_name+"_participants"
    cursor.execute('''CREATE TABLE %s
         (NAME TEXT);'''% name1)
    name2=grp_name+"_chats"
    cursor.execute('''CREATE TABLE %s
         (NAME TEXT,
         MESSAGE BLOB);'''% name2)
    
def get_participants(grp_name):
    name=grp_name+"_participants"
    cursor.execute("SELECT NAME FROM "+name+"")
    L= cursor.fetchall()
    r=[]
    for i in L:
        r.append(i[0])
    return r

def add_participant(name,grp_name):
    n1=grp_name+"_participants"
    state="INSERT INTO "+n1+" (NAME) VALUES (%s)"
    l=[name]
    value=tuple(l)
    cursor.execute(state,value)
    connection.commit()

def history_user(name):
   # SELECT * FROM Student ORDER BY Score DESC LIMIT 2;
   cursor.execute("SELECT SENDER,MESSAGE FROM "+name+"")
   r=cursor.fetchall()
   return r
   
def store_grp_chat(grp_name,name,msg):
    n1=grp_name+"_chats"
    state="INSERT INTO "+n1+" (NAME,MESSAGE) VALUES (%s,%s)"
    l=[name,msg]
    value=tuple(l)
    cursor.execute(state,value)
    connection.commit()
    
def grp_history(grpname):
    n1=grpname+"_chats"
    cursor.execute("SELECT * FROM "+n1+" ")
    r=cursor.fetchall()
    return r
    

    
    