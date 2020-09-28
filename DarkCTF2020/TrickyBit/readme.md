# Tricky Bit
> Category: Forensics
> Description: I always hated to be that last one, At least i should be in the second least place.

# Initial analysis

This challenge provides a `lsb1.bmp` file and an `Encrypt.py` file. Opening up the bmp immediatly points us to something messing up the image data (the "noise" and the missing color pixels are usually an indication of img manipulation).

Checking the logic on the `Encrypt.py` I was able to spot the following behavior (comments added for better understanding):

```python

    def run(self, stega_text):
        self.text_to_hide = stega_text  # this is the data the code is hidding, in this scenario the flag
        self.open_image()               # refer to the function below, nothing abnormal so far
        self.read_header()              # refer to the function below, nothing abnormal so far
        self.hide_text_size()           # this is the first algorithm we'll have to revert, more details on the actual function
        self.do_steg(self.text_to_hide) # this is the second algorithm, which will be similar to first one with some minor changes
        self.copy_rest()                # copy the rest of the original image data
        self.close_file()               # regular cleanup

    def open_image(self):
        with open(ImageFile, "rb") as f:
            self.original_image = f.read() # read the entire file to bytearray variable

    def read_header(self): 
        for x in range(0, HEADER_SIZE): # reading the header size, which is 54 as indicated in the code and store it on memory
            self.new_image_data += self.original_image[x]
            self.image_byte_counter += 1        # increase the internal byte counter variable

```

Now for the actual interesting part:;

```python
    def hide_text_size(self):
        sz = len(self.text_to_hide)
        s_sz = str(sz)
        s_sz += DELIMITER # up to this line we will have a string with the length of the message we are hidding and terminated by the char `$`
        self.do_steg(s_sz) # will call the steg algorithm with this information, example: if the string to hide is `thisisit` the data calculated on this method is `8$`

    def do_steg(self, steg_text):

        # iterate all characters
        for ch in range(0, len(steg_text)):

            current_char = steg_text[ch]
            current_char_binary = '{0:08b}'.format(ord(current_char))

            # iterate all the bits from the byte representing the current character of the message to hide
            for bit in range(0, len(current_char_binary)):
                new_byte_binary = ''

                # this will read the next byte from the original image data
                current_image_binary = '{0:08b}'.format(ord(self.original_image[self.image_byte_counter]))

                new_byte_binary = current_image_binary[:7] # extract the leftmost 7 bits from that byte

                new_byte_binary += current_char_binary[bit] # store the bit from the byte of the character we are hiding

                # replace the new image byte with the manipulated one
                new_byte = chr(int(new_byte_binary, 2)) 

                self.new_image_data += new_byte
                self.image_byte_counter += 1 # increment the 'consumed' byte from the original image

```

So, if you can keep up with the comments you'll figure it out that the steg algorithm is basically replacing the least significant bit from each byte and hidding data on it.


The header will be saved using this method and then immediatly after the text will also be hidden using this method:

```python
    # sequence of the steg algorithm
    self.hide_text_size() # header
    self.do_steg(self.text_to_hide) # actual data aka flag
```

# Solve

To solve this we need to revert the algorithm and try to reverse the data for the length, to understand how much data we need to read, and then read the actual data.

```python
c = open("lsb1.bmp","rb").read()

numbits = 0
part = ''
length = []


currentByte = 54 # we want to skip the header sizz N first bytes (54 as per the encryption code) 

guess = 5 # 5 will most likely be too much but it's fine as I'll stop once I get enough data

# each character will waste 8 bytes to store 1 byte of data, so we need to consumer N times 8 where N is the tentative guess of the len string terminated by $
for byt in range(currentByte, (currentByte + (8 * guess ))):        
    # for debug purposes to understand the current byte being processed
    #print('Currently at bit {}'.format(byt))
    
    # extract the least significant bit using the logical and with the mask 00000001
    currbit = int(c[byt]) & 0b00000001
    numbits = numbits + 1 # keep tabs on the number of bits
    part = part + str(currbit)  # store the current bit on a temporary string  
    
    currentByte = currentByte + 1 # keep tabs on the current byte

    if numbits == 8: # if we have 8 bits we have our next byte, so we retrieved one more character
        length.append(chr(int(part, 2))) # store found character in array
        
        if chr(int(part, 2)) == '$': # if we find the delimiter we are done with first part
            break

        numbits = 0
        part = ''        

len = int(''.join(length[:2]))
print('Found length {}'.format(len))

length = []
numbits = 0
part = ''
# we now know that we need to start at next byte from the previous cycle and we know we need 37 chars ( or in other words 8 * 37 bytes)
for byt in range(currentByte, (currentByte + 8 * len)):
    # for debug purposes to understand the current byte being processed
    #print('Currently at bit {}'.format(byt))

    # extract the least significant bit using the logical and with the mask 00000001
    currbit = int(c[byt]) & 0b00000001
    numbits = numbits + 1 # keep tabs on the number of bits
    part = part + str(currbit)  # store the current bit on a temporary string  

    if numbits == 8: # if we have 8 bits we have our next byte, so we retrieved one more character
        length.append(chr(int(part, 2))) # store found character in array
        
        # cleanup the temporary bits holder and proceed
        numbits = 0 
        part = ''        

# we finally have all the characters from the hidden message, just print it
print(''.join(length))

```

The above code has enough comments to guide the logic used, finally the result of the execution is:

```
Found length 37
DarkCTF{7H!5_0n3_was_4_l!ttl3_TRICKY}
```
