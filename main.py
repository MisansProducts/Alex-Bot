#======Libraries======
import asyncio
import json
import logging
import logging.handlers
import os
import sys

import discord
from discord.ext import commands

#======Alex Bot======
class Alex(commands.Bot):
    #Constructor
    def __init__(self, myIntents, *args):
        #Shared Variables
        self.myPrefix = args[0] #Prefix for bot commands
        self.myPrefixPrivate = args[1] #Prefix for private bot commands
        self.tylerFolderPath = args[2] #File path for tyler command

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
    
    #On Message Event
    async def on_message(self, message):
        #Bot is not the sender
        if message.author.id != self.user.id:
            ctx = await self.get_context(message)
            if ctx.valid: #Message is a command
                await self.process_commands(message)
            if (ctx.channel.type == discord.ChannelType.private): #Message is a private message
                print(f"{message.author.name} said: {message.content}")

#======Main======
async def main():
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
        return print("Config file created... please provide your Discord bot's token.")

    #======Variables======
    myPrefix = configData["myPrefix"] #Prefix for bot commands
    myPrefixPrivate = configData["myPrefixPrivate"] #Prefix for private bot commands
    myToken = configData["myToken"] #Token for Discord API connection
    tylerFolderPath = os.path.join(os.path.dirname(__file__), "Tyler\\") #File path for tyler command
    myIntents = discord.Intents.default() #Defines intents for the bot
    myIntents.message_content = True
    handler = logging.handlers.RotatingFileHandler(filename = "discord.log", maxBytes = 32 * 1024 * 1024, backupCount = 5, encoding = "UTF-8") #Handler for logging
    handler.setFormatter(logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style = "{")) #Sets up the formatter for logging
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    #Creates the bot
    bot = Alex(myIntents, myPrefix, myPrefixPrivate, tylerFolderPath)
    
    #Runs the bot using the token
    await bot.start(myToken)

#======Execution Check======
if __name__ == "__main__":
    asyncio.run(main())