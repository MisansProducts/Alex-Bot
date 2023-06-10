#======Libraries======
import os
import random
from typing import Literal, Optional

import discord
from discord.ext import commands
from discord.ext.commands import Context, Greedy

#Help Command
class MyHelp(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title = "Help")
        for cog, commands in mapping.items():
           filtered = await self.filter_commands(commands, sort=True)
           command_signatures = [self.get_command_signature(c) for c in filtered]
           if command_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

#======Commands======
class HybridCommands(commands.Cog):
    #Constructor
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.bot.help_command = MyHelp()

    #Syncs slash commands to Discord's servers
    @commands.hybrid_command(description = "Syncs slash commands to Discord's servers")
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
            
            return await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
        
        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild = guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1
            
        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.hybrid_command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("PONG!")

    @commands.hybrid_command()
    async def hhelp(self, ctx: commands.Context):
        embed = discord.Embed(
            title = "ALEX BOT INFORMATION",
            description = "All commands",
            color = 0xf600ff
        )
        #General Commands
        embed.add_field(
            name = "GENERAL COMMANDS",
            value = f"""
            `{self.bot.myPrefix}help`
            Alex Bot displays a list of commands.

            `{self.bot.myPrefix}hello`
            Alex Bot greets you!

            `{self.bot.myPrefix}rank` **(opt: @user)**
            Alex Bot displays the rank of a particular user.

            `{self.bot.myPrefix}refresh`
            Alex Bot refreshes your data in its database.

            `{self.bot.myPrefix}joke`
            Alex Bot tells a funny joke.

            `{self.bot.myPrefix}roast`
            Alex Bot roasts you.

            `{self.bot.myPrefix}countdown` **(1 - 10)**
            Alex Bot counts down to 0.

            `{self.bot.myPrefix}tyler`
            Alex Bot displays a Tyler of his choice.

            `{self.bot.myPrefix}avatar` **(opt: @user)**
            Alex Bot displays the profile picture of a particular user in full resolution. (It might take some time if the picture is a GIF.)

            `{self.bot.myPrefix}info` **(opt: @user)**
            Alex Bot displays information about a particular user.
            """
        )
        #Economy Commands
        embed.add_field(
            name = "ECONOMY COMMANDS",
            value = f"""
            `{self.bot.myPrefix}balance` **(opt: @user)**
            Alex Bot displays the balance of a particular user.

            `{self.bot.myPrefix}deposit` **(amount)**
            You deposit your money into your bank.

            `{self.bot.myPrefix}withdraw` **(amount)**
            You withdraw your money from your bank.

            `{self.bot.myPrefix}transfer` **(@user) (amount)**
            You transfer money from your pocket to a particular user.

            `{self.bot.myPrefix}work`
            You work for money.

            `{self.bot.myPrefix}flip` **(opt: h/t) (opt: amount)**
            Alex Bot flips a coin and you could bet on it.
            """
        )
        
        await ctx.send(embed = embed)
    
    @commands.hybrid_command()
    async def hello(self, ctx: commands.Context):
        responses = [
            "BEEP BEEP BOOP! I'M ALEX BOT!",
            "ALEX BOT HERE!",
            "ALEX BOT, REPORTING FOR DUTY!",
            "NO NEED FOR DRIPPIN' SAUCE, JUST ALEX BOT!"
        ]
        response = random.choice(responses)
        await ctx.send(response)

    @commands.hybrid_command()
    async def tyler(self, ctx: commands.Context):
        messages_basic = [
        "This is Tyler.",
        "Hello Tyler!",
        "You look cute, Tyler!",
        "Oh Tyler...",
        "What are you doing, Tyler?"
        ]

        #Writes message and uploads file
        my_files = os.listdir(self.bot.tylerFolderPath)
        pick_pic = random.choice(my_files)
        await ctx.send(random.choice(messages_basic), file = discord.File(os.path.join(self.bot.tylerFolderPath, pick_pic)))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HybridCommands(bot))