#======Libraries======
import io
import os
import random
import re
from typing import List, Literal, Mapping, Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context, Greedy

from commands.TicTacToe import TicTacToe
from commands.Color import Color

# Syncs slash commands to Discord's servers
class SyncCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object]=None, spec: Optional[Literal["~", "*", "^"]]=None) -> None:
        bot: commands.Bot = ctx.bot
        if not guilds:
            if spec == "~":
                synced = await bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                bot.tree.copy_global_to(guild=ctx.guild)
                synced = await bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                bot.tree.clear_commands(guild=ctx.guild)
                await bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await bot.tree.sync()
            
            return await ctx.send(f"SYNCED {len(synced)} COMMANDS {'GLOBALLY!' if spec is None else 'TO THE CURRENT GUILD!'}")
        
        ret = 0
        for guild in guilds:
            try:
                await bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1
            
        await ctx.send(f"SYNCED THE TREE TO {ret}/{len(guilds)}")

# Subclassed Help Command
class MyHelp(commands.MinimalHelpCommand):
    # Constructor
    def __init__(self):
        super().__init__(
            command_attrs = {"help": "Alex Bot displays a list of commands!"}
        )
    
    # Help Command (prefix)
    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]):
        author_file = discord.File(os.path.join("src", "assets", "server_icon.png"), filename="server_icon.png")
        thumbnail_file = discord.File(os.path.join("src", "assets", "avatar.png"), filename="avatar.png")
        footer_file = discord.File(os.path.join("src", "assets", "help_icon.png"), filename="help_icon.png")

        embed = discord.Embed(title="ALEX BOT INFORMATION", description="Created by misansproducts", color=0xf600ff)
        embed.set_author(name="SUPPORT SERVER", url="https://discord.gg/Pcfurfyggr", icon_url="attachment://server_icon.png")
        embed.set_thumbnail(url="attachment://avatar.png")

        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands)
            command_docs = [f"`{self.get_command_signature(c)}`\n{c.help}\n" for c in filtered]
            if command_docs:
                cog_name = getattr(cog, "qualified_name", "No Category")
                if not cog:
                    embed.set_footer(text=re.sub(r"`", r"", "\n".join(command_docs)), icon_url="attachment://help_icon.png")
                else:
                    embed.add_field(name=cog_name, value=re.sub(r" `", r"`", "\n".join(command_docs)), inline=True)
        await self.context.send(files=(author_file, thumbnail_file, footer_file), embed=embed)

#======General Commands======
class GeneralCommands(commands.Cog, name="GENERAL COMMANDS"):
    # Constructor
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.bot.help_command = MyHelp()
    
    # Help Command (slash)
    @app_commands.command(name = "help")
    async def slash_help(self, interaction: discord.Interaction, *, command: Optional[str]):
        """Alex Bot displays a list of commands!"""

        my_help = MyHelp()
        my_help.context = ctx = await Context.from_interaction(interaction)
        await my_help.command_callback(ctx, command=command)

    # Hello Command
    @commands.hybrid_command()
    async def hello(self, ctx: Context):
        """Alex Bot greets you!"""

        responses = [
            "BEEP BEEP BOOP! I'M ALEX BOT!",
            "ALEX BOT HERE!",
            "ALEX BOT, REPORTING FOR DUTY!",
            "NO NEED FOR DRIPPIN' SAUCE, JUST ALEX BOT!"
        ]
        response = random.choice(responses)
        await ctx.send(response)
    
    # Ping Command
    @commands.hybrid_command()
    async def ping(self, ctx: Context):
        """Pings Alex Bot!"""

        await ctx.send("PONG!")

    # Tyler Command
    @commands.hybrid_command()
    async def tyler(self, ctx: Context):
        """Alex Bot displays a Tyler of his choice!"""
        tyler_folder_path: str = self.bot.tyler_folder_path

        messages_basic = [
            "THIS IS TYLER!",
            "HELLO TYLER!",
            "YOU LOOK CUTE, TYLER!",
            "OH TYLER...",
            "WHAT ARE YOU DOING, TYLER?"
        ]

        # Writes message and uploads file
        my_files = os.listdir(tyler_folder_path)
        pick_pic = random.choice(my_files)
        await ctx.send(random.choice(messages_basic), file=discord.File(os.path.join(tyler_folder_path, pick_pic)))
    
    # Send Command
    @commands.hybrid_command()
    async def send(self, ctx: Context, user: discord.User, message: str):
        """Alex Bot sends a message to a user!"""

        await ctx.send(f"SENDING MESSAGE TO {user.name}...")
        try:
            await user.send(message)
        except Exception as e:
            print(e)
            await ctx.send("ERROR! ERROR! CAN'T DO IT!!!")
    
    # Avatar Command
    @commands.hybrid_command()
    async def avatar(self, ctx: Context, user: discord.User = commands.Author):
        """Alex Bot displays the profile picture of a user!"""

        buffer = io.BytesIO()
        await user.display_avatar.save(buffer) # Saves avatar in a buffer
        avatar = discord.File(buffer, filename=f"{user.name}_avatar.gif") if user.display_avatar.is_animated() else discord.File(buffer, filename=f"{user.name}_avatar.webp")
        await ctx.send(file=avatar)
    
    # Color Command
    @commands.hybrid_command()
    async def color(self, ctx: Context, color: str):
        """Alex Bot gives you a color!"""

        await Color(ctx).run(ctx, color)

    # Delete Command
    @commands.hybrid_command()
    async def delete(self, ctx: Context, num: int):
        """Alex Bot deletes his own messages!"""

        async for message in ctx.history(limit=num):
            if message.author.id == self.bot.application_id:
                await message.delete()

    # Tic-tac-toe Command
    @commands.hybrid_command()
    async def ttt(self, ctx: Context, user: discord.User=commands.Author):
        """Alex Bot sets up a game of Tic-tac-toe!"""

        await TicTacToe().run(ctx, user)

# Commands Setup
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SyncCommand(bot))
    await bot.add_cog(GeneralCommands(bot))
