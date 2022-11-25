
a = ""
l = []
x = []
y = []
while True:
    a = input()
    if a == "EXIT":
        break
    b = a.split(" ")
    # print(b)
    if b[1] in l:
        # print("come" ,b)
        # print(" ... ", x[l.index(b[1])], int(b[0]))
        y.append(-x[l.index(b[1])] + int(b[0]))
        # x[l.index[b[1]]] = x[l.index(b[1])] - int(b[0])
    else:
        l.append(b[1])
        x.append(int(b[0]))
    # print(x)

for i in y[:-1]:
    print(i,end=" ")
print(y[-1],end="")
            
        