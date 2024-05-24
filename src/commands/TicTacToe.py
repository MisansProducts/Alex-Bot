from datetime import datetime
import io
import random
from typing import List

from PIL import Image, ImageDraw, ImageSequence
import discord
from discord.ext import commands
from discord.ext.commands import Context

class TicTacToeButton(discord.ui.Button['TicTacToeGame']):
    def __init__(self, x: int, y: int, author: discord.User, p1: discord.User, p2: discord.User):
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y
        self.p1 = p1
        self.p2 = p2

        # Creates the embed
        self.embed = discord.Embed(title="TIC-TAC-TOE", color=0xf600ff, timestamp=datetime.now())
        self.embed.set_author(name=f"Challenged by {author.name}", icon_url=author.display_avatar.url)
    
    # Function to set button properties
    async def set_button(self, view: 'TicTacToeGame', style: discord.ButtonStyle, label: str, players: tuple[discord.User, discord.User]) -> discord.File | None:
        # Properties before the game continues
        self.style = style
        self.label = label
        self.disabled = True # Button cannot be clicked again after being set
        view.board[3 * self.y + self.x] = view.current_player # Converting a 2D 3x3 board to a 1D array is 3 x ROW + COL
        view.current_player = -view.current_player # -1 -> 1 -> -1 or X -> O -> X
        thumbnail_file: discord.File = None
        self.embed.set_footer(text=f"{players[1].name}", icon_url=players[1].display_avatar)

        # Properties after the game is over
        winner = view.check_board_winner()
        if winner is not None:
            # Win
            if winner:
                self.embed.description = f"{players[1].name} WON!"
                self.embed.set_thumbnail(url=players[1].display_avatar)
            # Tie
            else:
                self.embed.description = "TIE!"
                thumbnail_file = await self.merge_images()
                self.embed.set_thumbnail(url=f"attachment://{thumbnail_file.filename}")
            
            # Disables every button
            for child in view.children:
                child.disabled = True
            
            self.view.stop() # Ends the interaction

            return thumbnail_file
        
        # Properties after the game continues
        self.embed.description = f"{players[0].name}'s turn"
        self.embed.set_thumbnail(url=players[0].display_avatar)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToeGame = self.view
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

class TicTacToeGame(discord.ui.View):
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
    
class TicTacToe():
    async def run(self, ctx: Context, user: discord.User=commands.Author):
        # Randomly picks a player to go first
        player_1: discord.User = random.choice([ctx.author, user])
        player_2: discord.User = user if player_1 == ctx.author else ctx.author

        # Creates the embed
        embed = discord.Embed(title="TIC-TAC-TOE", description=f"{player_1.name}'s turn", color=0xf600ff, timestamp=datetime.now())
        embed.set_author(name=f"Challenged by {ctx.author}", icon_url=ctx.author.display_avatar)
        embed.set_thumbnail(url=player_1.display_avatar)
        embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.display_avatar)

        # Sends the message with the embed and the view
        await ctx.send(embed=embed, view=TicTacToeGame(ctx.author, player_1, player_2))
