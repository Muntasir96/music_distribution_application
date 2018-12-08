import geocoder

# pip3 install geocoder
# python3 geo.py

g = geocoder.ip('me')
x = "Latitude: " + str(g.latlng[0]) + " Longitutde: " + str(g.latlng[1])
print(x)