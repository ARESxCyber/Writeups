# misc - electric-bovine 
![](https://codimd.s3.shivering-isles.com/demo/uploads/upload_43146d63a13ab237450a54486d95442b.png)

## The start of the story - josefk

### Discovering the source code

I've first joined the discord server and sent message to the bot, after sending `!help` it answered with:
```
Help Menu
-------------
 - !help    Displays this message.
 - !ping    Pong??
 - !about    Displays information about this bot.
 - !resource    Links you to a random resource.
 - !cowsay <text>    Displays your text in cowsay format. Requires greater permissions than user in the guild to use.
 - !list_users     Lists all users in channel.
 - !send_msg <text>    (when used from DMs) sends a message in the #botspam channel in the guild.
 - !role_add <user> <role>    Attempt to add role to user. May only be used from within guild.
```

After trying few commands, I've noticed that `!about` returns link to the bot's source. (The token link is RickRoll on youtube)
```
About Me
----------
I'm a bot. On the weekends, I'm a huge fan.
My name is Secure Permissions Bot#7351
You may find my source code here:https://beav.es/o7y
You may find my bot token here https://beav.es/o7r
License: None.
```
### Finding the vulnerability
Looking at the code, we can see an `os.popen` call with user supplied argument, however the possible characters are strictly limited.
```python=
if message.content.startswith("!cowsay"):
    if message.guild:
        await message.channel.send(
            "Sorry, but `!cowsay` is only available for use in dm channels."
        )
        return

    else:
        if message.author == client.user:
            return
        elif (
            client.guilds[0].get_member(message.author.id).guild_permissions
            >= client.guilds[0].get_role(763128087226351638).permissions
        ):
            # accept, do cowsay.
            try:
                arg = message.content.split("!cowsay ")[1]
            except:
                message.author.send("Bad arguments to !cowsay")
                return

            for char in arg:
                if char in " `1234567890-=~!@#$%^&*()_+[]\\{}|;':\",./?":
                    await message.author.send("Invalid character sent. Quitting.")
                    return

            cow = "```\n" + os.popen("cowsay " + arg).read() + "\n```"

            await message.author.send(cow)

        else:
            await message.author.send(
                "You do not have the requisite roles to use !cowsay. Sorry."
            )
```

### The Cowfail

But sending `!cowsay foo` to the bot responded with
```
You do not have the requisite roles to use !cowsay. Sorry.
```

Hmm, lets investigate other functions, looks like we need to escalate roles in order to execute `cowsay`. 
### Possible "priviledge escalation"
The next interesting function is `!role_add <user> <role>`.
```python=
if message.content.startswith("!role_add"):
    if message.guild:
        content = message.content

        try:
            args = content.split("!role_add ")[1].split(" ")
        except:
            await message.channel.send(f"Too few values to !role_add")
            return

        if len(args) != 2:
            return

        try:
            member = message.guild.get_member(int(args[0][3:-1]))
            user = client.get_user(int(args[0][3:-1]))
            role = message.guild.get_role(int(args[1][3:-1]))
        except:
            await message.channel.send(
                f"You passed a bad user or role to !role_add"
            )
            return

        await message.channel.send(
            f"Hmmm... { member.name } wants to add role { role.name }. Interesting. . . "
        )
        await user.send(
            f"Hmmm... { member.name } wants to add role { role.name }. Interesting. . . ",
        )

        auth = authenticate(member, message.guild.get_member(client.user.id), role,)

        if auth and role.name != "bot":
            await member.add_roles(role)
            await message.channel.send(
                f"Granted role {role.name} to member {member.name}. Well Done!"
            )
            await user.send(
                f"Granted role {role.name} to member {member.name}. Well Done!"
            )
        else:
            await message.channel.send(
                f"Denied role {role.name} to member {member.name}. Gotta hack harder than that!"
            )
            await user.send(
                f"Denied role {role.name} to member {member.name}. Gotta hack harder than that!",
            )
    else:
        await message.author.send("You are forbidden from invoking that here.")
```

The first thing it checks is that if this message comes from a channel - so sending this to the bot as private message has no value. We need to send this message to the channel, but how? We cannot post messages to any channel. 


### Finding !send_msg
Fortunately there is another handy function `!send_msg`, lets look at that one.

```python=
if message.content.startswith("!send_msg"):
    try:
        message_to_send = message.content.split("!send_msg ")[1]
    except:
        return

    if message.guild:
        await message.author.send(
            f"**The following was sent from {message.author.name} in {message.guild.name}**"
        )
        await message.author.send(message_to_send)
    else:
        await client.guilds[0].text_channels[1].send(
            f"**The following message was sent from {message.author.name} in DMs**"
        )
        await client.guilds[0].text_channels[1].send(message_to_send)
```

Sending `!send_msg` command forwards anything that is after that to a channel! Now we are going somewhere. Since we had the bot's source, we decided to create our own discord server and add this bot to it so we can debug what is happening in the channel we would normally not see.
### Triggering the "privilege escalation" but failing
First thing we tried was to send the `!ping` as according to the code, should behave differently, so we tried sending `!send_msg !ping` to the bot, this is the response from the "hidden" channel.

![](https://i.ibb.co/9vbzPwM/Screenshot-from-2020-10-11-16-24-24.png)

So our theory with `!send_msg` forwarding any arbitrary command is valid

#### Discord ClientID and RoleID
Ever tried sending `\@myname` to a discord channel? It will respond with your client id in format `<@&1234567890>`, and you may notice that sending it back without the `\` symbol it will transform back into the usual format of a ping. 

Same thing applies to getting ID of role, however we ended up getting the role id using developer mode in discord (more on that later). You can notice the similarity with this piece of code from `!add_role` command.

```python=
member = message.guild.get_member(int(args[0][3:-1]))
user = client.get_user(int(args[0][3:-1]))
role = message.guild.get_role(int(args[1][3:-1]))
```

That looks very connected, it strips the special characters from the beginning and from the end to get the integer representation of the ID. Great

We tried many variants of sending this ID to the client, most of which failed, as you for example could not see the role tagged,since it showed up as @deleted-role,but it was actually the correct solution.


![](https://i.ibb.co/F7LQN1g/Screenshot-from-2020-10-15-15-07-22.png)


Why isnt this going through? Since this bot is running locally, we can edit its code however we like. So we decided to add few debug messages about the authentication outcome, and indeed, the authentication was failing.

![](https://i.ibb.co/qmmhG1M/Screenshot-from-2020-10-15-15-26-27.png)
### The fiasco
But after that message we got this
![](https://i.ibb.co/Bqqb4qJ/upload-50e5a3e1e1ec1dfa5c3b8c592cbb0507.png)
Soon after that we discovered the par in the code where everything fails: the `authenticate` function.
```python=
def authenticate(author, authorizer, role):

    # Derive a variant to make auth requests resolve uniquely
    variant = author.discriminator
    variant = int(variant * 4)

    # Add author's name to their credential set
    author_credentials = [author.nick]
    # Add perms
    author_credentials.extend([str(int(y.id) + variant) for y in author.roles])
    author_credentials.extend([y.name.lower() for y in author.roles])

    # Add authorizer's name
    authorizer_credentials = [authorizer.name]
    # Add perms
    authorizer_credentials.extend([str(int(y.id) + variant) for y in authorizer.roles])
    authorizer_credentials.extend([y.name.lower() for y in authorizer.roles])

    # Add role name
    role_information = [role.name, str(int(role.id) + variant)]

    permset = list(
        (set(author_credentials) & set(authorizer_credentials)) & set(role_information)
    )

    if len(permset) >= 1:
        return True
    else:
        return False
```

## The part where i joined - NOT_MASTER09
### Exploring the source code
I first started looking at what are the arguments passed to the function, specifically `author, authorizer, role`
I quickly found that 
`author == Member object of the person to which to add the role`
`authorizer == User object of the same person`
`role == Role object of the role to add`

After which i was able to look at the end result of what the function returned
```python=
if len(permset) >= 1:
        return True
    else:
        return False
```
You may ask what is permset?It's a variable defined by
```python=
permset = list(
        (set(author_credentials) & set(authorizer_credentials)) & set(role_information)
    )
```
One element must be same in all three sets
To elaborate on the `author/authorizer_credentials` and `role_information` they're are an array consisting of base information of their objects.

By some debugging we discovered that `author_credentials` and `authorizer_credentials` where equal

So what the base information is?It's an array of the name of the role/user and it's ids+variant
```python=
    variant = author.discriminator
    variant = int(variant * 4)
```
### Eureka!
But,i noticed a bug,the output of the bot(e.g the fiasco at the start of the previous section) used `author.name` while the `author/authorizer_credentials` array used author.nick,where `author.name` corresponds to the real discord username of author,and `author.nick` to it's discord nickname!

By setting your discord nickname to `private`,the name of the role,we can fool the `authenticate` function into outputing True(which was discovered by josefk)
![](https://i.ibb.co/kXsMvxP/upload-efc94635c945442f866ba4fc8abf7619.png)
> Note: to get the role id of private role on the remote discord server,we used discord developer mode, right click on role
> ![](https://i.ibb.co/GJfpCRC/Screenshot-from-2020-10-15-15-13-30.png)

## Exploiting `!cowsay`... again - josefk,NOT_MASTER
Now that we can execute `!cowsay`, we need to find out how to exploit it, since there is alot of forbidden characters I've checked what printable characters are usable with
```python=
>>> import string
>>> chars = " `1234567890-=~!@#$%^&*()_+[]\\{}|;':\",./?"
>>> "".join([ch for ch in string.printable if ch not in chars])
'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ<>\t\n\r\x0b\x0c'
```
So we can only use letters, `<` and `>`.

After some fiddling around on my local terminal we found that you can pass file to cowsay by just `cowsay <file` without the need have spaces, cat the file etc.

So we thought that the flag is probably stored in the same place with the bot,so we used `!cowsay <flag` and got the flag!


![](https://i.ibb.co/k413mQg/upload-6834c2efc294ccc3587eaedc7a169959.png)






