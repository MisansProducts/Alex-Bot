from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
import discord
from discord.ext.commands import Context
import numpy

# FIXES ISSUES WITH COLORMATH: numpy.asscalar() - https://github.com/gtaylor/python-colormath/issues/104
def patch_asscalar(a: numpy.ndarray):
    return a.item()

setattr(numpy, "asscalar", patch_asscalar)

class Color():
    def __init__(self, ctx: Context):
        roles = ctx.guild.roles
        self.all_roles = list(roles)
        self.color_roles = [r for r in roles if r.name.startswith('0x')]
        self.non_color_roles = [r for r in roles if not r.name.startswith('0x')]
        
    async def run(self, ctx: Context, color: str):
        color = color.lower()

        # Handles sorting color roles
        if color == 'sort':
            if not ctx.permissions.administrator:
                return await ctx.send("ERROR! YOU CAN'T MAKE ME DO THAT!!!")
            return await self.sort_colors(ctx)
        # Handles clearing all color roles
        elif color == 'clean':
            if not ctx.permissions.administrator:
                return await ctx.send("ERROR! YOU CAN'T MAKE ME DO THAT!!!")
            return await self.clear_colors(ctx)
        
        # Parses color
        try:
            color = discord.Color.from_str(color)
        except ValueError:
            return await ctx.send("ERROR! INVALID COLOR!!!")
        
        # Creates color role
        found_role = next((role for role in self.color_roles if role.color == color), None)
        if not found_role:
            return await self.create_color(ctx, color)
        
        # Assigns color role
        await ctx.author.add_roles(found_role)
        return await ctx.send(f"YOUR COLOR IS {found_role}")
        
    async def create_color(self, ctx: Context, color: discord.Color):
        role_name: str = f"0x{hex(color.value)[2:].upper().zfill(6)}"
        new_role = await ctx.guild.create_role(reason=f"COLOR ROLE CREATED BY {ctx.author.name}!", name=role_name, color=color)
        await new_role.move(below=ctx.me.top_role, offset=-1)
        await ctx.author.add_roles(new_role)
        return await ctx.send(f"YOUR COLOR IS {role_name}")
    
    # Code by sinbad (78631113035100160)
    async def sort_colors(self, ctx: Context): # https://gist.github.com/mikeshardmind/85c8afb7a30bbd151fbf3960a34fc917
        def distance(c1: discord.Color, c2: discord.Color):
            c1_lab = convert_color(sRGBColor(*c1.to_rgb()), LabColor)
            c2_lab = convert_color(sRGBColor(*c2.to_rgb()), LabColor)
            return delta_e_cie2000(c1_lab, c2_lab)
        
        def greedy_travelling_salesman(points: list[discord.Role], start=None):
            points = [(r.color, r, idx) for idx, r in enumerate(points)]

            if start is None:
                start = points[0]
            must_visit = points[:]
            path = [start]
            must_visit.remove(start)
            
            while must_visit:
                nearest = min(must_visit, key=lambda x: distance(path[-1][0], x[0]))
                path.append(nearest)
                must_visit.remove(nearest)
            
            return path
        
        def count_swaps(a, b):
            swaps = 0
            for i in range(len(a)):
                if a[i] != b[i]:
                    swaps += 1
            return swaps
        
        # Sorts the color roles by CIELAB color space
        optimal_path = greedy_travelling_salesman(self.color_roles) # Gets optimal color path for smooth gradience based off visual perception
        sorted_color_roles = [role for _, role, _ in optimal_path]  # Extracts sorted roles from the optimal path
        bot_role_pos = self.non_color_roles.index(ctx.me.top_role)  # Gets the position of the bot's role
        final_role_order = self.non_color_roles[:bot_role_pos] + sorted_color_roles + self.non_color_roles[bot_role_pos:]
        
        # Calculates swaps and checks if changes are needed
        swaps = count_swaps(self.all_roles, final_role_order)
        if not swaps:
            return await ctx.send("COLOR ROLES ARE ALREADY SORTED!")
        
        # Updates roles
        await ctx.send("SORTED!!!")
        return await ctx.guild.edit_role_positions(
            {role: idx for idx, role in enumerate(final_role_order)},
            reason=f"SORTING COLORS, MADE {swaps} SWAPS!"
        )
    
    async def clear_colors(self, ctx: Context):
        for role in self.color_roles:
            await role.delete(reason=f"CLEARING ALL COLOR ROLES! INVOKED BY {ctx.author.name}!")
        return await ctx.send("COLORS NO MORE!!!")
