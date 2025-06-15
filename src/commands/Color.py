import colorsys

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
    async def run(self, ctx: Context, color: discord.Color):
        role_name: str = f"0x{hex(color.value)[2:].upper().zfill(6)}"
        # await self.sort_colors(ctx)
        new_role = await ctx.guild.create_role(reason=f"Color role created by {ctx.author}", name=role_name, color=color)

        # Solution by leocx1000 (349373972103561218) - NOT NECESSARY AS OF github.com/Rapptz/discord.py/pull/10100
        # roles = [r for r in ctx.guild.roles if r.id != new_role.id]
        # roles.insert(roles.index(ctx.me.top_role), new_role)
        # await ctx.guild.edit_role_positions({role: idx for idx, role in enumerate(roles)})

        await new_role.move(below=ctx.me.top_role, offset=-1, reason="Adding a color role below the bot's top role.")
        await ctx.author.add_roles(new_role)
        await ctx.send(f"YOUR COLOR IS {role_name}")
    
    # Code by sinbad (78631113035100160)
    async def sort_colors(self, ctx: Context): # https://gist.github.com/mikeshardmind/85c8afb7a30bbd151fbf3960a34fc917
        def distance(c1: discord.Color, c2: discord.Color):
            c1_lab = convert_color(sRGBColor(*c1.to_rgb()), LabColor)
            c2_lab = convert_color(sRGBColor(*c2.to_rgb()), LabColor)
            return delta_e_cie2000(c1_lab, c2_lab)
        
        def greedy_travelling_salesman(points: list, start=None):
            points = [(r_color, r, idx) for idx, (r_color, r) in enumerate(points)]

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

        # Gets non-color roles
        roles = [r for r in ctx.guild.roles if r.name[:2] != '0x']
        bot_role_pos = roles.index(ctx.me.top_role) # Bot role index

        # Gets color roles
        colors = [(r.color, r) for r in ctx.guild.roles if r.name[:2] == '0x'] # List of (role, int_RGB, index)

        # Performs travelling salesman on CIELAB color space for smooth gradience based off visual perception
        path = greedy_travelling_salesman(colors)
        colors_sorted = [color[2] for color in path] # List of sorted indices
        roles_sorted = [colors[index][1] for index in colors_sorted] # List of sorted color roles
        roles_final = roles[:bot_role_pos] + roles_sorted + roles[bot_role_pos:] # Combines lists of non-color roles and sorted color roles

        swaps = self.count_swaps([r for r in ctx.guild.roles], roles_final)
        print("No change; color roles are already sorted!") if not swaps else print(f"Sorted roles! Made {swaps} swaps!")
        
        await ctx.guild.edit_role_positions({role: idx for idx, role in enumerate(roles_final)})
    
    # Original sort function I created - based off sorting the hue values
    async def sort_colors_old(self, ctx: Context):
        # Gets non-color roles
        roles = [r for r in ctx.guild.roles if r.name[:2] != '0x']
        bot_role_pos = roles.index(ctx.me.top_role)

        # Gets color roles
        color_roles = [(r, r.color.value) for r in ctx.guild.roles if r.name[:2] == '0x'] # (role, int_RGB)
        colors = [role[1] for role in color_roles] # List of int_RGB

        # Convert RGB (red, green, blue) to HSL (hue, saturation, lightness)
        def rgb_to_hsl(color):
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            h, l, s = colorsys.rgb_to_hls(r, g, b) # Library for some reason uses HLS; swaps to HSL
            return h, s, l
        
        # Converts integer RGB values to HSL and appends them together
        colors_hsl = [(color, rgb_to_hsl(color), index) for index, color in enumerate(colors)] # (int_RGB, (H, S, L), index)
        colors_hsl_sorted = sorted(colors_hsl, key=lambda x: (x[1][0], x[1][1], x[1][2])) # Sorts colors
        colors_sorted = [color[2] for color in colors_hsl_sorted] # List of sorted indices
        roles_sorted = [color_roles[index][0] for index in colors_sorted] # List of sorted color roles
        roles_final = roles[:bot_role_pos] + roles_sorted + roles[bot_role_pos:] # Combines lists of non-color roles and sorted color roles

        swaps = self.count_swaps([r for r in ctx.guild.roles], roles_final)
        print("No change; color roles are already sorted!") if not swaps else print(f"Sorted roles! Made {swaps} swaps!")

        await ctx.guild.edit_role_positions({role: idx for idx, role in enumerate(roles_final)})

    # Counts swaps for debugging
    def count_swaps(self, a, b):
        swaps = 0
        for i in range(len(a)):
            if a[i] != b[i]:
                swaps += 1
        return swaps