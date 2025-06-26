#======Libraries======
import asyncio
from datetime import date
import logging
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
        self.logger: logging.Logger = args[3] # Logger
        
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
            # Message is a private message
            if (ctx.channel.type == discord.ChannelType.private):
                self.logger.info(f"{message.author.name} ({message.author.id}) in PRIVATE CHANNEL\n\t\t{message.content}")
                # ...and a command
                if ctx.valid:
                    await self.process_commands(message)
            # Message is a command in a guild
            elif ctx.valid:
                self.logger.info(f"{message.author.name} ({message.author.id}) in {ctx.guild.name} ({ctx.guild.id}):{ctx.channel} ({ctx.channel.id})\n\t\t{message.content}")
                await self.process_commands(message)
    
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

    # Create a logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Create a filename with current date and time
    log_filename = f"logs/{date.today().strftime('%Y-%m-%d')}.log"
    handler = logging.FileHandler(filename=log_filename, encoding='UTF-8', mode='a')
    handler.setFormatter(logging.Formatter(fmt="[{asctime}] [{levelname:<8}] {module}.{funcName}:{lineno}\n\t{message}", datefmt="%Y-%m-%d %H:%M:%S", style='{'))
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    #======Variables======
    my_token = os.getenv('MY_TOKEN')
    my_prefix = os.getenv('MY_PREFIX')
    my_prefix_private = os.getenv('MY_PREFIX_PRIVATE')
    tyler_folder_path = os.path.join(os.path.dirname(__file__), "assets", "Tyler") # File path for tyler command
    my_intents = discord.Intents.default() # Defines intents for the bot
    my_intents.message_content = True
    
    # Creates the bot
    bot = Alex(my_intents, my_prefix, my_prefix_private, tyler_folder_path, logger)
    
    # Runs the bot using the token
    await bot.start(my_token)

#======Execution Check======
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting Alex Bot...")
        sys.exit(0)
