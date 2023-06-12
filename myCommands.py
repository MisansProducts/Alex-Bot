#======Libraries======
import io
import os
import random
import re
from typing import Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context, Greedy

#Sync Command
class SyncCommand(commands.Cog):
    #Constructor
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    #Syncs slash commands to Discord's servers
    @commands.command(description = "ALEX BOT SYNCS UP THE COMMANDS TO DISCORD'S SERVERS", hidden = True)
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object] = None, spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild = ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild = ctx.guild)
                synced = await ctx.bot.tree.sync(guild = ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild = ctx.guild)
                await ctx.bot.tree.sync(guild = ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()
            
            return await ctx.send(f"SYNCED {len(synced)} COMMANDS {'GLOBALLY!' if spec is None else 'TO THE CURRENT GUILD!'}")
        
        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild = guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1
            
        await ctx.send(f"SYNCED THE TREE TO {ret}/{len(guilds)}")

#Subclassed Help Command
class MyHelp(commands.MinimalHelpCommand):
    #Constructor
    def __init__(self):
        super().__init__(
            command_attrs = {"help": "ALEX BOT DISPLAYS A LIST OF COMMANDS"}
        )
    
    #Help Command (prefix)
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title = "ALEX BOT INFORMATION", description = "Created by abacus_paradox", color = 0xf600ff)
        author_file = discord.File("server_icon.png", filename = "server_icon.png")
        embed.set_author(name = "SUPPORT SERVER", url = "https://discord.com/invite/9zHWtZr", icon_url = "attachment://server_icon.png")
        thumbnail_file = discord.File("avatar.png", filename = "avatar.png")
        embed.set_thumbnail(url = "attachment://avatar.png")
        footer_file = discord.File("help_icon.png", filename = "help_icon.png")
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands)
            command_docs = [f"`{self.get_command_signature(c)}`\n{c.help}\n" for c in filtered]
            if command_docs:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.set_footer(text = re.sub(r"`", r"", "\n".join(command_docs)), icon_url = "attachment://help_icon.png") if not cog else embed.add_field(name = cog_name, value = re.sub(r" `", r"`", "\n".join(command_docs)), inline = True)
        await self.context.send(files = (author_file, thumbnail_file, footer_file), embed = embed)

#======General Commands======
class GeneralCommands(commands.Cog, name = "GENERAL COMMANDS"):
    #Constructor
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.bot.help_command = MyHelp()
    
    #Help Command (slash)
    @app_commands.command(name = "help")
    async def slash_help(self, interaction: discord.Interaction, *, command: Optional[str]):
        """ALEX BOT DISPLAYS A LIST OF COMMANDS"""
        my_help = MyHelp()
        my_help.context = ctx = await commands.Context.from_interaction(interaction)
        await my_help.command_callback(ctx, command = command)

    #Hello Command
    @commands.hybrid_command()
    async def hello(self, ctx: commands.Context):
        """ALEX BOT GREETS YOU"""
        responses = [
            "BEEP BEEP BOOP! I'M ALEX BOT!",
            "ALEX BOT HERE!",
            "ALEX BOT, REPORTING FOR DUTY!",
            "NO NEED FOR DRIPPIN' SAUCE, JUST ALEX BOT!"
        ]
        response = random.choice(responses)
        await ctx.send(response)
    
    #Ping Command
    @commands.hybrid_command()
    async def ping(self, ctx: commands.Context):
        """PINGS ALEX BOT"""
        await ctx.send("PONG!")

    #Tyler Command
    @commands.hybrid_command()
    async def tyler(self, ctx: commands.Context):
        """ALEX BOT DISPLAYS A TYLER OF HIS CHOICE"""
        messages_basic = [
        "THIS IS TYLER!",
        "HELLO TYLER!",
        "YOU LOOK CUTE, TYLER!",
        "OH TYLER...",
        "WHAT ARE YOU DOING, TYLER?"
        ]

        #Writes message and uploads file
        my_files = os.listdir(self.bot.tylerFolderPath)
        pick_pic = random.choice(my_files)
        await ctx.send(random.choice(messages_basic), file = discord.File(os.path.join(self.bot.tylerFolderPath, pick_pic)))
    
    #Send Command
    @commands.hybrid_command()
    async def send(self, ctx: commands.Context, user: discord.User, message: str):
        """ALEX BOT SENDS A MESSAGE TO A USER"""
        await ctx.send(f"SENDING MESSAGE TO {user.name}...")
        await user.send(message)
    
    #Avatar Command
    @commands.hybrid_command()
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        """ALEX BOT DISPLAYS THE PROFILE PICTURE OF A USER"""
        #Defaults to the author when no argument is given
        if user == None:
            user = ctx.author

        buffer = io.BytesIO()
        await user.display_avatar.save(buffer) #Saves avatar in a buffer
        avatar = discord.File(buffer, filename = f"{user.name}_avatar.gif") if user.display_avatar.is_animated() else discord.File(buffer, filename = f"{user.name}_avatar.webp")
        await ctx.send(file = avatar)

#Commands Setup
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SyncCommand(bot))
    await bot.add_cog(GeneralCommands(bot))