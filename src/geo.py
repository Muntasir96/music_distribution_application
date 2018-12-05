import geocoder

# pip3 install geocoder
# python3 geo.py

g = geocoder.ip('me')
print(g.latlng)
