import qrcode
import random
import string


# pip3 install qrcode
# pip3 install Image
# python3 qrgen.py

clist = string.ascii_lowercase + string.ascii_uppercase + string.digits 
n = 4
gencode = ''
for i in range(n):
    gencode = gencode + random.choice(clist)
img = qrcode.make("http://192.168.1.213:8080/downloadfile/GGVIjrFm76dJr7TG") # img is a png image
img.show()