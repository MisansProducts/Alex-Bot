#======Libraries======
import os
import sys
import json
import discord
import commands

#======Config File======
#Opens config file
if os.path.exists(os.getcwd() + r"\config.json"):
    with open(os.getcwd() + r"\config.json") as myConfigFile:
        configData = json.load(myConfigFile) #Gets data
#Creates config file if one does not exist
else:
    configTemplate = {
        "myToken": "",
        "myPrefix": "!",
        "myPrefixPrivate": "?"
        }
    
    with open(os.getcwd() + r"\config.json", "w+") as myConfigFile:
        json.dump(configTemplate, myConfigFile, indent = 4) #Writes template

#======Execution Loop======
def run_discord_bot():
    #======Variables======
    #Gets values from keys in the config file
    myToken = configData["myToken"] #Token for Discord API connection
    myPrefix = configData["myPrefix"] #Prefix for bot commands
    myPrefixPrivate = configData["myPrefixPrivate"] #Prefix for private bot commands

    client = discord.Client(command_prefix = myPrefix, case_insensitive = True)

    #Bot Start Event Listener
    @client.event
    async def on_ready():
        await client.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f"{myPrefix}help | {myPrefixPrivate}help"))
        print(client.user.name)
        print(f"ID: {client.user.id}")
        print(f"Running on python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print(f"Discord version {discord.__version__}")
        print("Connected to:")
        for guild in client.guilds:
            print(guild.name)
        print("---------------------")
    
    #Gets User Message
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f"{username} ({message.author.id}) said: '{user_message}' ({channel})")
        user_message = user_message.lower()

        if user_message[0] == myPrefix:
            user_message = user_message[1:]
            await commands.command(message, user_message, False)
        elif user_message[0] == myPrefixPrivate:
            user_message = user_message[1:]
            await commands.command(message, user_message, True)
        elif not message.guild:
            await commands.command(message, user_message, False)
        else:
            pass
    
    #Runs the Discord bot using the token
    client.run(myToken, reconnect = False)