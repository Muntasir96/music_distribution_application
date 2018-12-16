# music_distribution_application

## Docker
docker build -t largescale .

docker run -p 8080:8080 largescale .

## Important info for Prof Sovran
- Each QR code will count as only one download increment to the number of downloads. 
- Each QR code will expire in 120 seconds after being scanned by a phone according to Professor Sovran's instructions.  
- Register an account to upload a song
- You don't need to register/log in for a song
- Have a qr reader from your phone to get a song
- Each QR code represents one download 
- Iphones won't download a file, their browser will just play the song (This is out of our control)
- Androids will actually download the file
- The redirect from the QR will get a song from the amazon s3 bucket but wont show the actual s3 url to users.


Project design: https://docs.google.com/document/d/1GXpyyZPDEBjHcwhGG0eT3h6RPVGWMpEicTgdTP0ZNK8/edit

