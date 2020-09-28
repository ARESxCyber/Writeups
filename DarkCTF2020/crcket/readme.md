# crcket

> Category: Forensics
> Description: ``` DarkArmy's openers bagging as many runs as possible for our team.
    1st over: 86 runs
    2nd over: 37 runs
    3rd over: 4 runs
    4th over: 52 runs```


# Analysis & Solve

Trying to open the image returns an error stating that the image cannot be displayed because it contained errors.
Initial thought, title points to 'crc' so we must be looking at a corrupted png, and damn was it corrupted.

Looking at the output of hexedit we can see that the usual 'IHDR' chunk is instead 'DARK' and no information about the size or the checksum for it.

![image](https://user-images.githubusercontent.com/69213271/94381005-c0709500-0105-11eb-9e92-f189ee96bd57.png)

Running pngcheck also gives the same info:

![image](https://user-images.githubusercontent.com/69213271/94381032-d4b49200-0105-11eb-80cc-2ed8d6f647e1.png)

So, let's fix this chunk ...

The descripton of the challenge points out to 4 bytes and wanna guess how many bytes is the 'crc', yeah 4 - there is a slight evil thing here though (in my opinion but well), the numbers on the description are in decimal format and we need to convert them to 'hex'.

That will help us getting the correct crc, which is `0x56250434` (86=56, 37=25, 04=04, 52=34)

Changing it using hexeditor we now have:

![image](https://user-images.githubusercontent.com/69213271/94381357-1e51ac80-0107-11eb-9672-a7cff733e9b0.png)


Why are we adding the crc on that position? This contains good info on PNG format and the chunks: http://www.libpng.org/pub/png/spec/1.2/PNG-Chunks.html (shot answer is, IHDR starts at byte 12, it is 17 bytes in length, with the last 4 being the checksum).

Let's run now pngcheck again:

![image](https://user-images.githubusercontent.com/69213271/94381378-2dd0f580-0107-11eb-9009-8de872b8d71b.png)


Humm, the bytes responsible for the size of the image are also part of the IHDR, and they are empty, how can we guess this though?
Bruteforce is the key, we know the checksum, so let's get some code running to bruteforce the size for us:

```python
from zlib import crc32

data = open("crcket1.png",'rb').read()
index = 12

ihdr = bytearray(data[index:index+17])
width_index = 7
height_index = 11

for x in range(1,2000):
	height = bytearray(x.to_bytes(2,'big'))
	for y in range(1,2000):
		width = bytearray(y.to_bytes(2,'big'))
		for i in range(len(height)):
			ihdr[height_index - i] = height[-i -1]
		for i in range(len(width)):
			ihdr[width_index - i] = width[-i -1]
		if hex(crc32(ihdr)) == '0x56250434':
			print("width: {} height: {}".format(width.hex(),height.hex()))
	for i in range(len(width)):
			ihdr[width_index - i] = bytearray(b'\x00')[0]

```

Running the script gives:

![image](https://user-images.githubusercontent.com/69213271/94381401-3f1a0200-0107-11eb-9bb5-3d5aa99725a1.png)

Lucky for us the only possibility is width: 0320 and height 0190, otherwise we would have needed to trying all options.

Time to again edit the png on hexeditor:

![image](https://user-images.githubusercontent.com/69213271/94381472-82747080-0107-11eb-9c19-3795d5c182b9.png)

One more time pngcheck:

![image](https://user-images.githubusercontent.com/69213271/94381497-9cae4e80-0107-11eb-8dce-c3ad89da7fe0.png)

Alrigth, so another error but the IHDR chunk is now fixed, let's analyze and try to find what that DARK chunk can be.

At this point I stopped a second and found out this awesome tool: https://github.com/Hedroed/png-parser

Running this on the current png gives me this:

![image](https://user-images.githubusercontent.com/69213271/94381596-ef880600-0107-11eb-8f14-7fdc2144f225.png)

So, looking at the unkown chunks (2 times DARK), and looking at the ammount of data on the chunks these must be IDAT chunks (they can be repeated and need to be together - which they are).

One more round of hexeditor:

![image](https://user-images.githubusercontent.com/69213271/94381713-4261bd80-0108-11eb-9bff-a3876d5b389f.png)

And:

![image](https://user-images.githubusercontent.com/69213271/94381757-5d343200-0108-11eb-9047-392f8be29108.png)


Another round of pngcheck:

![image](https://user-images.githubusercontent.com/69213271/94381774-6f15d500-0108-11eb-95ab-337ca9bec485.png)

And we are done, finally opening the png we get:

![image](https://user-images.githubusercontent.com/69213271/94380790-f7927680-0104-11eb-9995-c0231ee1ed74.png)

