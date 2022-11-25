from pwn import *
import random
import subprocess
import matplotlib.pyplot as plt

i1=process(["./client.py", "5555" ,"5556"])
i2=process(["./client.py","5555","5556"])
i3=process(["./client.py","5555","5556"])
i4=process(["./client.py","5555","5556"])
i5=process(["./client.py","5555","5556"])
i6=process(["./client.py","5555","5556"])

#MESSAGING PATTERN -3 

def login(a,name):
    a.recvline()
    a.sendline(str(1).encode())
    a.recvline()
    a.sendline(name.encode())
    a.recvline()
    a.sendline(name.encode())
def send(a,r,m):
    a.recvline()
    a.sendline(str(1).encode())
    a.recvline()
    a.sendline(str(1).encode())
    a.recvline()
    a.sendline(r.encode())
    a.recvline()
    a.sendline(m.encode())

login(i1,"a1")
time.sleep(0.1)
login(i2,"a2")
time.sleep(0.1)
login(i3,"a3")
time.sleep(0.1)
login(i4,"a4")
time.sleep(0.1)
login(i5,"a5")
time.sleep(0.1)
login(i6,"a6")
time.sleep(0.1)

l1=[i1,i2,i3,i4,i5,i6]
s1=["a1","a2","a3","a4","a5","a6"]
for i in range(30):
    r1=random.randrange(6)
    r2=random.randrange(3)
    send(l1[r1],s1[r2],"h"+str(i))
    time.sleep(0.1)


subprocess.check_call("./a.sh '%s'" % "clients.log", shell=True)

f=open("k.txt").read()
y = f.split(" ")
z = []
for i in y:
    z.append(int(i))
# print(y)
x=range(1,len(z)+1)
c='%.3f' % (sum(z)/len(z))
plt.xlabel("Message No:")
plt.ylim(0,65)
plt.ylabel("latency for a message")
plt.title("Latency for messaging Pattern 3")
plt.text(15,40,"Average Latency: "+str(c),fontsize=10)
plt.plot(x,z)
plt.show()

