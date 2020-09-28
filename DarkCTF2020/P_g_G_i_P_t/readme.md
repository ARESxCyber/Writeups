# P_g_G_i_P_t

> Category: Misc
> Description: ```Some basics of Cryptography and git. Detailed description in the files.```

# Analysis $ Solve

Description on the zip file for the challenge material contain the following long description:

```
P_g_G_i_P_t
===========
A DarkArmy newbie pulled out some files from an old vulnerable machine 
that belonged to the great sage "karma".

He grabbed the following info:

PGP Fingerprint: 
5071 62CE 550A 9B5D

Signature File: 
a.sig

Find the first part of flag using above info and 10k.tar.zst


Password format for the prrotected git1.1.7z archive: 

<(6-digit-number-from-10k.tar.zst)_(first-3-char/num-of-the-public-key)>

Note: 
Password is free of any angle brackets and parantheses, 
those are for explaination purpose only.
Do remember the _ it's in the password.
```

## Step 1 - find the public key

So, this step should be pretty easy but due to several hickups I got stuck on this a bit more time than necessary.

I found that the author uploaded the public key to the PGP public server: https://keys.openpgp.org
Using the fingerprint (`5071 62CE 550A 9B5D`) I was able to find it: https://keys.openpgp.org/search?q=5071+62CE+550A+9B5D

Problem #1 - this PGP key server stripes out the author ID, and due to that the key cannot be imported (I spent a bit trying to fix this but eventually I moved on to try finding it somehow).

![image](https://user-images.githubusercontent.com/69213271/94382143-a769e300-0109-11eb-8ef7-75d56544a2fd.png)

I found that the key was also published to the mit one: https://pgp.mit.edu/pks/lookup?op=get&search=0x507162CE550A9B5D

![image](https://user-images.githubusercontent.com/69213271/94382305-2e1ec000-010a-11eb-9a9a-c9b5e0dc5a19.png)

With this I saved the public key to a file and imported the key manually:

```
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: SKS 1.1.6
Comment: Hostname: pgp.mit.edu

mI0EX2isUAEEAMrhmSxi09RxVL0QT8N7HF/1/u7E7Zb6IRJBYrJCBtbbD86tenJb1BNwbcDs
pp6NTZs+lqx0/Qh2V87LQIiJLhs9FH3yP9NhamFCD3jDPAsoUIqbaEr6ExJrVCnI3LN1wWq5
OAlkLkiMckfcSV1Mv/QVoHc14m7BdhkyAH7gDsChABEBAAG0M2Rhcmthcm15J3MgUG90YXRv
UEMgKGZvciBDVEYpIDxwb3RhdG9AZGFya2FybXkueHl6PojUBBMBCAA+FiEEU0zAZCaKVjhX
ojJ0UHFizlUKm10FAl9orFACGwMFCQAbr4AFCwkIBwIGFQoJCAsCBBYCAwECHgECF4AACgkQ
UHFizlUKm13IFAQAk1ruyHNKkb6VPDqXxdElDFBC/dQzm4XU+cLzfOUVmAlqhHj6bg31/Xy9
v90OyUSVPYrCFxsEQHu+2NDy+jZ4fbPSTihOTvFkJyBY+xS7nPCVVH6Itl0sQdmxYa1H4h14
j6VnW3s5qgXDvUPoOr70DNbcAwMpqATtcSJAFX8NzxK4jQRfaKxQAQQAvaGroaPvLM/QiMzY
0XZk5pT+vRvaHr+4STkh1wEo/BErzJx3HhWXNjYh/Y7MJMzMl76R9sXvMOc4mW0vVd0yl3M/
vPxLVo/GOqFbGM7fvYu+Hi17bRtl1zKsoIi45WAil4tiA9ku1zjmuq20YbmrUXJZk5eOWOVa
floCdvVeko0AEQEAAYi8BBgBCAAmFiEEU0zAZCaKVjhXojJ0UHFizlUKm10FAl9orFACGwwF
CQAbr4AACgkQUHFizlUKm13kUQQAkl/YbupM23RHAhbYDRTNJsI/OdPjp6vUUgZS9uSXahV3
EoxHaNGwnTGpmrXZi54P6SUiVfxWJHsM5Lp6dLR1x3gZNqNEbo+tK0sl0A7iyzh7dGOEwrZF
ho0Pvggzb8JCHfZx5ZHxjMgg9e0S14n+eADWxHx2x5WllT5F64wmeZg=
=QPzO
-----END PGP PUBLIC KEY BLOCK-----
```

> We found part of the password for the next level, (first 3 chars of the pub key), so we now know this from the password: `xxxxxxx_mI0` (where x are still not known).

![image](https://user-images.githubusercontent.com/69213271/94382401-8ce43980-010a-11eb-92a5-2954586065bb.png)

Looking at the `10k.tar.zst` file this looks a different compression tool `zstd`, after installing it and decompress the file using `zstd -d 10k.tar.zst` I got a `10k.tar` file, decompressed with `tar -xvf 10k.tar` showed finally a folder `10k` with literally 10k text files inside, each one with a 7 char text (except the last one :) ).

To proceed forward the idea is to find the key that allows for the following gpgp command to succeed `gpg --output a --decrypt a.sig`

![image](https://user-images.githubusercontent.com/69213271/94383061-f2d1c080-010c-11eb-9f0b-304f518cdf6a.png)


At this point I went rogue and decided to take a shortcut, the idea of the challenge was to validate the decryption key using one of the key files (provided on the challenge) BUT ... there are 10K files and I was not able to quickly find the command lines of gpg to accept the password file on a single command line, so this was causing me issues to script the execution.


What I did instead (as the time was running short) was the following:

- all the files in the 10K folder contained exactly 7 chars, and we also know that because the password is 7 chars
- coded a quick py script to create a dictionary of all values inside the files (you can probably see where this is going now)
- created the hash of the 7z file using (7z2hashcat.pl)
- hashcat buteforce the 7z file
- validate the actual found password was validating the pgp key (just to use the proper expected tools for this challenge)

Dictionary code:

```python

yourpath = './P_g_G_i_P_t/10k'
import os
with open('./dic.txt', 'w') as dic:

    for root, dirs, files in os.walk(yourpath, topdown=True):
        files.sort()
        for name in files:
            #print(os.path.join(root, name))
            with open(os.path.join(root, name), 'r') as f1:
                
                str = '{}_mI0\n'.format(f1.readline())
                dic.write(str)
```

Generate the 7z Hash:

![image](https://user-images.githubusercontent.com/69213271/94382766-eef16e80-010b-11eb-9042-df0d2d5d4f73.png)

Creating the dictionary:

![image](https://user-images.githubusercontent.com/69213271/94383143-2f9db780-010d-11eb-8f3f-537b2a2be9a5.png)

Putting it all together and running hashcat:

![image](https://user-images.githubusercontent.com/69213271/94383296-99b65c80-010d-11eb-9583-7b38a765e9c8.png)

And in few seconds I got the password `2766951_mI0`.

Now, before I moved on I just wanted to confirm the previous gpg command was indeed correct, so I need to find on which file is this password `2766951`.

![image](https://user-images.githubusercontent.com/69213271/94383389-e69a3300-010d-11eb-8593-994ba9c4b348.png)

File `1235`, let's validate the previous gpg command then:

![image](https://user-images.githubusercontent.com/69213271/94383436-0c273c80-010e-11eb-868a-e7611dbaf6a4.png)

So, right no we have the password to decrypt the next phase of the challenge.

## Step 2 - GIT

Decompressing the git repo using the found password `2766951_mI0` showed a git repo:

![image](https://user-images.githubusercontent.com/69213271/94383513-47297000-010e-11eb-81a9-bae46982d124.png)

I took also a considerable amount of time on this part of the challenge as I was looking to `git branch` and `git checkout` and `git log` trying to make some sense out of the history and determine on which branch was the damn file ... turns out I was on a rabbits hole.

Once I read a bit more about git I found `git reflog`, and something very odd was presented:

![image](https://user-images.githubusercontent.com/69213271/94383632-9c658180-010e-11eb-8712-188dbbe3f420.png)

which was not consistent with :

![image](https://user-images.githubusercontent.com/69213271/94383659-b0a97e80-010e-11eb-8f2f-3a88bdf6d6cb.png)

It turns out that there was a deleted branch, and that was why I couldn't find it on the git log and branch/checkout party.

From this reflog I can issue a straight `git checkout 40a3658` and then, we get our flag:

![image](https://user-images.githubusercontent.com/69213271/94383777-f9f9ce00-010e-11eb-8871-868dd026a730.png)

