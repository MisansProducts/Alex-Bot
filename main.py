#======Libraries======
import asyncio
import json
import logging
import os
import sys

import discord
from discord.ext import commands

#======Config File======
#Opens config file
if os.path.exists("config.json"):
    with open("config.json", encoding = "UTF-8") as myConfigFile:
        configData = json.load(myConfigFile) #Gets data
else: #Creates config file if one does not exist
    configTemplate = {
        "myToken": "",
        "myPrefix": "!",
        "myPrefixPrivate": "?"
        }
    with open("config.json", "w+", encoding = "UTF-8") as myConfigFile:
        json.dump(configTemplate, myConfigFile, indent = 4) #Writes template

#======Variables======
myToken = configData["myToken"] #Token for Discord API connection
handler = logging.FileHandler(filename = "discord.log", encoding = "UTF-8", mode = "w") #Handler for logging
myIntents = discord.Intents.default() #Defines intents for the bot
myIntents.message_content = True

#======Alex Bot======
class Alex(commands.Bot):
    #Constructor
    def __init__(self):
        #Shared Variables
        self.myPrefix = configData["myPrefix"] #Prefix for bot commands
        self.myPrefixPrivate = configData["myPrefixPrivate"] #Prefix for private bot commands
        self.tylerFolderPath = os.path.join(os.path.dirname(__file__), "Tyler\\") #File path for tyler command

        #commands.Bot() constructor
        super().__init__(
            command_prefix = self.myPrefix,
            case_insensitive = True,
            intents = myIntents,
            activity = discord.Activity(type = discord.ActivityType.listening, name = f"{self.myPrefix}help | {self.myPrefixPrivate}help")
        )

    #Setup Hook
    async def setup_hook(self):
        await self.load_extension("myCommands")
        print(f"{self.user.name} ({self.user.id})")
        print(f"Running on Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print(f"Discord version {discord.__version__}")
        asyncio.create_task(self.wait_for_bot_to_be_ready())
    
    #For cache that needs to be loaded but executed only once
    async def wait_for_bot_to_be_ready(self) -> None:
        await self.wait_until_ready() #Waits until bot cache has been loaded
        print("Connected to:")
        for guild in self.guilds:
            print(guild.name)
        print("---------------------")

#Creates the bot
bot = Alex()

#Runs the bot using the token
bot.run(myToken, reconnect = False, log_handler = handler, log_level = logging.INFO)