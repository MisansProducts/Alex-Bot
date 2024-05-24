#======Libraries======
import asyncio
import logging
import logging.handlers
import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

#======Custom Context======
class CustomContext(commands.Context):
    async def send(self, *args, **kwargs): # Send Response Function
        ref = self.message.to_reference(fail_if_not_exists=False)
        bot: Alex = self.bot
        # Sends a private response to the user
        if self.prefix == bot.my_prefix_private:
            return await super().author.send(*args, **kwargs)
        # Sends a regular response
        return await super().send(*args, **kwargs, reference=ref)

#======Alex Bot======
class Alex(commands.Bot):
    # Constructor
    def __init__(self, my_intents: discord.Intents, *args):
        # Shared Variables
        self.my_prefix         = args[0] # Prefix for bot commands
        self.my_prefix_private = args[1] # Prefix for private bot commands
        self.tyler_folder_path = args[2] # File path for Tyler command

        # commands.Bot() constructor
        super().__init__(
            command_prefix = (self.my_prefix, self.my_prefix_private),
            case_insensitive = True,
            intents = my_intents,
            activity = discord.Activity(type=discord.ActivityType.listening, name=f"{self.my_prefix}help | {self.my_prefix_private}help")
        )

    # Setup Hook
    async def setup_hook(self):
        await self.load_extension("myCommands")
        print(f"{self.user.name} ({self.user.id})")
        print(f"Running on Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print(f"Discord version {discord.__version__}")
        asyncio.create_task(self.wait_for_bot_to_be_ready())
    
    # For cache that needs to be loaded but executed only once
    async def wait_for_bot_to_be_ready(self) -> None:
        await self.wait_until_ready() # Waits until bot cache has been loaded
        print("Connected to:")
        for guild in self.guilds:
            print(guild.name)
        print("---------------------")
    
    # On Message Event
    async def on_message(self, message: discord.Message):
        # Bot is not the sender
        if message.author.id != self.user.id:
            ctx = await self.get_context(message)
            # Message is a command
            if ctx.valid:
                await self.process_commands(message)
            # Message is a private message
            if (ctx.channel.type == discord.ChannelType.private):
                print(f"{message.author.name} said: {message.content}")
    
    # Get Context
    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CustomContext)

#======Main======
async def main():
    # Creates .env file if one does not exist
    if not os.path.exists(".env"):
        with open(file=".env", mode='w', encoding='UTF-8', newline='\n') as my_env:
            my_env.write("MY_TOKEN=\n")
            my_env.write("MY_PREFIX=!\n")
            my_env.write("MY_PREFIX_PRIVATE=?\n")
        return print(".env file created... please provide your Discord bot's token.")
    
    # Load environment variables from .env file
    load_dotenv()

    #======Variables======
    my_token = os.getenv('MY_TOKEN')
    my_prefix = os.getenv('MY_PREFIX')
    my_prefix_private = os.getenv('MY_PREFIX_PRIVATE')
    tyler_folder_path = os.path.join(os.path.dirname(__file__), "assets", "Tyler") # File path for tyler command
    my_intents = discord.Intents.default() # Defines intents for the bot
    my_intents.message_content = True
    handler = logging.handlers.RotatingFileHandler(filename="../discord.log", maxBytes=32 * 1024 * 1024, backupCount=5, encoding='UTF-8') # Handler for logging
    handler.setFormatter(logging.Formatter(fmt="[{asctime}] [{levelname:<8}] {name}: {message}", datefmt="%Y-%m-%d %H:%M:%S", style='{')) # Sets up the formatter for logging
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Creates the bot
    bot = Alex(my_intents, my_prefix, my_prefix_private, tyler_folder_path)
    
    # Runs the bot using the token
    await bot.start(my_token)

#======Execution Check======
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting Alex Bot...")
        sys.exit(0)
