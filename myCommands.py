#======Libraries======
from datetime import datetime
import io
import os
from PIL import Image, ImageDraw, ImageSequence
import random
import re
from typing import Literal, Optional, List

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
    @commands.command(hidden = True)
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
            command_attrs = {"help": "Alex Bot displays a list of commands!"}
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

class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int, a: discord.User, p1: discord.User, p2: discord.User):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y
        self.a = a
        self.p1 = p1
        self.p2 = p2

        # Creates the embed
        self.embed = discord.Embed(title="TIC-TAC-TOE", color=0xf600ff, timestamp=datetime.now())
        self.embed.set_author(name=f"Challenged by {self.a.name}", icon_url=self.a.display_avatar.url)

    async def set_button(self, view: 'TicTacToe', style: discord.ButtonStyle, label: str, players: tuple[discord.User, discord.User]) -> discord.File | None:
        self.style = style
        self.label = label
        self.disabled = True
        self.embed.set_footer(text=f"{players[1].name}", icon_url=players[1].display_avatar)
        view.board[3 * self.y + self.x] = view.current_player
        view.current_player = -view.current_player
        thumbnail_file = None
        winner = view.check_board_winner()
        if winner is not None:
            if winner:
                self.embed.description = f"{players[1].name} WON!"
                self.embed.set_thumbnail(url=players[1].display_avatar)
            else:
                self.embed.description = "TIE!"
                thumbnail_file: discord.File = await self.merge_images()
                self.embed.set_thumbnail(url=f"attachment://{thumbnail_file.filename}")
            for child in view.children:
                child.disabled = True
            self.view.stop()
            return thumbnail_file
        self.embed.description = f"{players[0].name}'s turn"
        self.embed.set_thumbnail(url=players[0].display_avatar)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[3 * self.y + self.x]
        if state in (view.X, view.O):
            return
        
        img = await self.set_button(view, discord.ButtonStyle.danger, 'X', (self.p2, self.p1)) if view.current_player == view.X else await self.set_button(view, discord.ButtonStyle.success, 'O', (self.p1, self.p2))
        await interaction.response.edit_message(attachments=(img,), embed=self.embed, view=view) if img is not None else await interaction.response.edit_message(embed=self.embed, view=view)
    
    async def merge_images(self, size: int=512) -> discord.File: # Only for tied games
        # Creates buffers and loads the images of player 1 and player 2
        buffer_input1 = io.BytesIO()
        buffer_input2 = io.BytesIO()

        await self.p1.display_avatar.save(buffer_input1)
        await self.p2.display_avatar.save(buffer_input2)

        image1 = next(ImageSequence.Iterator(Image.open(buffer_input1))).resize((size, size)).convert("RGBA") if self.p1.display_avatar.is_animated() else Image.open(buffer_input1).resize((size, size)).convert("RGBA")
        image2 = next(ImageSequence.Iterator(Image.open(buffer_input2))).resize((size, size)).convert("RGBA") if self.p2.display_avatar.is_animated() else Image.open(buffer_input2).resize((size, size)).convert("RGBA")

        merged_image = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        # Create masks
        mask1 = Image.new("L", (size, size), 0)
        mask2 = Image.new("L", (size, size), 0)
        draw1 = ImageDraw.Draw(mask1)
        draw2 = ImageDraw.Draw(mask2)

        # Draw diagonal masks using triangles
        draw1.polygon([(0, 0), (size, 0), (0, size)], fill=255)
        draw2.polygon([(size, size), (0, size), (size, 0)], fill=255)

        # Apply masks and paste images
        merged_image.paste(image1, (0, 0), mask1)
        merged_image.paste(image2, (0, 0), mask2)

        # Draws a black diagonal line with a white border separating both images
        draw = ImageDraw.Draw(merged_image)
        draw.line([(0, size), (size, 0)], fill=(255, 255, 255), width=7)
        draw.line([(0, size), (size, 0)], fill=(0, 0, 0), width=6)

        # Save the result to a BytesIO buffer
        buffer = io.BytesIO()
        merged_image.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename = "ttt_thumb.webp")

class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton] # Type hints that all our children will be TicTacToeButtons
    X, O, Tie = -1, 1, 2 # Constants defining X and O labels as integers as well as the Tie condition
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Horizontals
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Verticals
        [0, 4, 8], [2, 4, 6]             # Diagonals
    ]

    def __init__(self, a: discord.User, p1: discord.User, p2: discord.User):
        super().__init__()
        self.current_player = self.X # X starts first
        self.board = [0] * 9 # 1D array representing a 3x3 board
        [self.add_item(TicTacToeButton(x, y, a, p1, p2)) for x in range(3) for y in range(3)] # 3x3 matrix of TicTacToeButtons

    def check_board_winner(self) -> bool:
        for combo in self.winning_combinations:
            value = sum(self.board[i] for i in combo)
            if abs(value) == 3: return True              # Win condition
        if all(i != 0 for i in self.board): return False # Tie condition
        return None                                      # No condition

#======General Commands======
class GeneralCommands(commands.Cog, name = "GENERAL COMMANDS"):
    #Constructor
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.bot.help_command = MyHelp()
    
    #Help Command (slash)
    @app_commands.command(name = "help")
    async def slash_help(self, interaction: discord.Interaction, *, command: Optional[str]):
        """Alex Bot displays a list of commands!"""
        my_help = MyHelp()
        my_help.context = ctx = await Context.from_interaction(interaction)
        await my_help.command_callback(ctx, command = command)

    #Hello Command
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
    
    #Ping Command
    @commands.hybrid_command()
    async def ping(self, ctx: Context):
        """Pings Alex Bot!"""
        await ctx.send("PONG!")

    #Tyler Command
    @commands.hybrid_command()
    async def tyler(self, ctx: Context):
        """Alex Bot displays a Tyler of his choice!"""
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
    async def send(self, ctx: Context, user: discord.User, message: str):
        """Alex Bot sends a message to a user!"""
        await ctx.send(f"SENDING MESSAGE TO {user.name}...")
        try:
            await user.send(message)
        except Exception as e:
            print(e)
            await ctx.send("ERROR! ERROR! CAN'T DO IT!!!")
    
    #Avatar Command
    @commands.hybrid_command()
    async def avatar(self, ctx: Context, user: discord.User = commands.Author):
        """Alex Bot displays the profile picture of a user!"""

        buffer = io.BytesIO()
        await user.display_avatar.save(buffer) #Saves avatar in a buffer
        avatar = discord.File(buffer, filename = f"{user.name}_avatar.gif") if user.display_avatar.is_animated() else discord.File(buffer, filename = f"{user.name}_avatar.webp")
        await ctx.send(file=avatar)
    
    # Color Command
    @commands.hybrid_command()
    async def color(self, ctx: Context, color: str):
        """Alex Bot gives you a color!"""

        if color[0] == "#":
            color = color[1:].upper()
        elif color[0:2] == "0x":
            color = color[2:].upper()
        else:
            return await ctx.send("ERROR, COLOR MUST START WITH #")
        if len(color) != 6:
            return await ctx.send("ERROR, COLOR MUST be 6 HEXADECIMAL DIGITS LONG")
        role_name = "0x" + color
        position = ctx.me.top_role.position
        print("Color command")
        # role = await ctx.guild.create_role(name=role_name, color=int(color, 16))
        # await role.edit(position=position)
        # await ctx.author.add_roles(role)
        # await ctx.send(f"YOUR COLOR IS {role_name}")
    
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
        """Alex bot plays Tic-tac-toe!"""

        # Randomly picks a player to go first
        player_1: discord.User = random.choice([ctx.author, user])
        player_2: discord.User = user if player_1 == ctx.author else ctx.author

        # Creates the embed
        embed = discord.Embed(title="TIC-TAC-TOE", description=f"{player_1.name}'s turn", color=0xf600ff, timestamp=datetime.now())
        embed.set_author(name=f"Challenged by {ctx.author}", icon_url=ctx.author.display_avatar)
        embed.set_thumbnail(url=player_1.display_avatar)
        embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)

        # Sends the message with the embed and the view
        await ctx.send(embed=embed, view=TicTacToe(ctx.author, player_1, player_2))

#Commands Setup
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SyncCommand(bot))
    await bot.add_cog(GeneralCommands(bot))