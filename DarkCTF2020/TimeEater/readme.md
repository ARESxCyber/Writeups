# Time Eater

> Category: Linux
> Description: ```This room requires account on Try Hack Me tryhackme.com/jr/darkctflo```

# User

Regular enumeration with nmap and gobuster:

```
# Nmap 7.80 scan initiated Sun Sep 27 22:20:56 2020 as: nmap -sC -sV -oN nmapInitial 10.10.202.112
Nmap scan report for 10.10.202.112
Host is up (0.27s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 64:60:d1:e5:39:96:90:b9:3c:72:b0:35:c2:2a:e4:f9 (RSA)
|   256 3c:07:fb:86:de:65:9b:52:59:70:de:06:2e:58:21:48 (ECDSA)
|_  256 b7:ed:d9:dd:40:46:b4:dc:c8:c3:5c:a1:28:78:73:f7 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Dimension by HTML5 UP
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Sun Sep 27 22:21:42 2020 -- 1 IP address (1 host up) scanned in 45.62 seconds
```

Exploring the site while gobuster runs and gong through the paths found turns out to be a major rabbit hole hunt, quite literally indeed:

```
/images (Status: 301)
/info (Status: 301)
/assets (Status: 301)
/test (Status: 301)
/cd (Status: 301)
/git (Status: 301)
/rabbit (Status: 301)
/uniqueroot (Status: 301)
```

At this point, I was starting to be a bit lost as I was not finding much to proceed, until magically gobuster found `/uniqueroot` and this was the game changer I was waiting for. (note to self never stop gobuster before it finishes)

![image](https://user-images.githubusercontent.com/69213271/94384282-2eba5500-0110-11eb-808e-22de86d0c203.png)

![image](https://user-images.githubusercontent.com/69213271/94384296-3b3ead80-0110-11eb-8d65-9ef9653cdbbb.png)

And finally:

![image](https://user-images.githubusercontent.com/69213271/94384326-50b3d780-0110-11eb-9d40-0e15f5b8d379.png)

So the way to gain initial access is to hydra ssh using rockyou, now the way the text is written is a bit confusing and indeed I ended up trying both `wolfie` and `elliot` as users.

`hydra -l elliot -P /opt/rockyou.txt ssh://10.10.202.112 -t 60`

Found password `godisgood`

![image](https://user-images.githubusercontent.com/69213271/94384736-49d99480-0111-11eb-83f5-12659b8f5666.png)


SSH to the box `ssh elliot@10.10.202.112`:

![image](https://user-images.githubusercontent.com/69213271/94384570-e51e3a00-0110-11eb-99df-ce94cd8ad6b0.png)

`sudo -l ` showed somthing pretty usefull:

![image](https://user-images.githubusercontent.com/69213271/94384604-f49d8300-0110-11eb-80a0-a1a57482b0df.png)

And we have user flag:

![image](https://user-images.githubusercontent.com/69213271/94384647-1991f600-0111-11eb-8abc-880b66a03d70.png)

`flag{user_flag_for_this_challenge}`


# Root

After we gained access as `dark` we now need to find a privesc way to root.

At this point I was going for `linpeas.sh` but something caught my attention on `dark` user, he's on group `docker`, that is 99% a priesc vector.

This was probably not supposed to be on the machine but it proved my theory:

![image](https://user-images.githubusercontent.com/69213271/94384886-b2c10c80-0111-11eb-8fe9-8054c4f70002.png)

So can I just resume this and get done with it?

Yep !!!

![image](https://user-images.githubusercontent.com/69213271/94385067-2400bf80-0112-11eb-9e11-f7dbbd571ea3.png)

![image](https://user-images.githubusercontent.com/69213271/94385106-3f6bca80-0112-11eb-8b42-6b5c3b3509fb.png)

And I am root in a docker container with the filesystem of `/root` mounted on `/mnt`, so I can just go and fetch the flag right?
Wrong ... apparently there is no flag at the `/root/root.flag`, well nothing that a find cannot solve and it found the flag at `/mnt/root/.rootflag/root.txt`

![image](https://user-images.githubusercontent.com/69213271/94385212-907bbe80-0112-11eb-9c38-b649a00bd58d.png)


`darkCTF{Escalation_using_D0cker_1ss_c00l}`
