#======Libraries======
import os
import random
from typing import Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context, Greedy

#Help Command
class MyHelp(commands.MinimalHelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs = {"help": "ALEX BOT DISPLAYS A LIST OF COMMANDS"}
        )
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title = "ALEX BOT INFORMATION", description = "Created by abacus_paradox", color = 0xf600ff)
        all_commands = []
        #Adds all commands to a single list instead of multiple depending on the cog (i.e., HybridCommands, MyHelp)
        for cog, commands in mapping.items():
            for command in commands:
                all_commands.insert(0, command) if str(command) == "help" else all_commands.append(command)
        filtered = await self.filter_commands(all_commands)
        command_docs = [f"{self.get_command_signature(c)}\n{c.help}" for c in filtered]
        embed.add_field(name = "ALL COMMANDS", value = "\n".join(command_docs), inline = True)
        await self.context.send(embed = embed)

#======Commands======
class HybridCommands(commands.Cog):
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

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HybridCommands(bot))