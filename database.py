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
#          PUBLIC_KEY INT,
#          PRIVATE_KEY INT);''')

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
    connection.commit()
    #print("inserted")
    
def get_all_names():
    cursor.execute("SELECT NAME FROM CREDENTIALS")
    names=cursor.fetchall()
    n=[]
    for i in names:
        n.append(i[0])
    return n

def recvPubKey(n):
    cursor.execute("SELECT PUBLIC_KEY FROM CREDENTIALS WHERE NAME='%s' " % (n))
    key  = cursor.fetchall()
    print(key)
    return key[0][0]

def recvPrivKey(n):
    cursor.execute("SELECT PRIVATE_KEY FROM CREDENTIALS WHERE NAME='%s' " % (n))
    key  = cursor.fetchall()
    print(key)
    return key[0][0]

# insert_user(["A","1",0,"A","A"])
# insert_user(["B","1",0,"B","B"])
# insert_user(["c","3",0,"C","C"])
