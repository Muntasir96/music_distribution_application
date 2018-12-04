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
img = qrcode.make(gencode) # img is a png image
img.show()