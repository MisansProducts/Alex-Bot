import colorsys

import discord
from discord.ext.commands import Context

class Color():
    async def run(self, ctx: Context, color: discord.Color):
        role_name: str = f"0x{hex(color.value)[2:].upper().zfill(6)}"

        new_role = await ctx.guild.create_role(reason=f"Color role created by {ctx.author}", name=role_name, color=color)

        # Solution by leocx1000 (349373972103561218)
        roles = [r for r in ctx.guild.roles if r.id != new_role.id]
        roles.insert(roles.index(ctx.me.top_role), new_role)
        await ctx.guild.edit_role_positions({role: idx for idx, role in enumerate(roles)})

        await ctx.author.add_roles(new_role)
        await ctx.send(f"YOUR COLOR IS {role_name}")
        
    async def sort_colors(self, ctx: Context):
        # Gets non-color roles
        roles = [r for r in ctx.guild.roles if r.name[:2] != '0x']
        bot_role_pos = roles.index(ctx.me.top_role)

        # Gets color roles
        color_roles = [(r, r.color.value) for r in ctx.guild.roles if r.name[:2] == '0x'] # (role, int_RGB)
        colors = [role[1] for role in color_roles] # list of int_RGB

        # Convert RGB (red, green, blue) to HSL (hue, saturation, lightness)
        def rgb_to_hsl(color):
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            h, l, s = colorsys.rgb_to_hls(r, g, b) # Library for some reason uses HLS; swaps to HSL
            return h, s, l
        
        # Counts swaps for debugging
        def count_swaps(a, b):
            swaps = 0
            for i in range(len(a)):
                if a[i] != b[i]:
                    swaps += 1
            return swaps
        
        # Converts integer RGB values to HSL and appends them together
        colors_hsl = [(color, rgb_to_hsl(color), index) for index, color in enumerate(colors)] # (int_RGB, (H, S, L), index)
        colors_hsl_sorted = sorted(colors_hsl, key=lambda x: (x[1][0], x[1][1], x[1][2])) # Sorts colors
        colors_sorted = [color[2] for color in colors_hsl_sorted] # List of sorted indices
        roles_sorted = [color_roles[index][0] for index in colors_sorted] # List of sorted color roles
        roles_final = roles[:bot_role_pos] + roles_sorted + roles[bot_role_pos:] # Combine lists of non-color roles and sorted color roles

        swaps = count_swaps([r for r in ctx.guild.roles], roles_final)
        print("No change; color roles are already sorted!") if not swaps else print(f"Sorted roles! Made {swaps} swaps!")

        await ctx.guild.edit_role_positions({role: idx for idx, role in enumerate(roles_final)})
