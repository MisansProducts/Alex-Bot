#Made by Alex

#======Libraries======
from distutils.command.config import config
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands.cooldowns import BucketType
import asyncio
import random
import os
import sys
import io
import psycopg2
import time
import json

#======Config File======
#Opens config file
if os.path.exists(os.getcwd() + "\\config.json"):
    with open(os.getcwd() + "\\config.json") as myConfigFile:
        configData = json.load(myConfigFile) #Gets data
#Creates config file
else:
    configTemplate = {
        "myToken": "",
        "myPrefix": "!",
        "myChannel": "",
        "psycopg2_host": "",
        "psycopg2_database": "",
        "psycopg2_user": "",
        "psycopg2_password": ""}
    
    with open(os.getcwd() + "\\config.json", "w+") as myConfigFile:
        json.dump(configTemplate, myConfigFile, indent = 4) #Writes template

#======Variables======
tylerFolderPath = os.path.join(os.path.dirname(__file__), "Tyler\\") #File path for !tyler command
#Gets values from keys in the config file
myToken = configData["myToken"] #Token for Discord API connection
myPrefix = configData["myPrefix"] #Prefix for bot command
myChannel = int(configData["myChannel"]) #ID for Discord channel
#PostgreSQL login information
psycopg2_host = configData["psycopg2_host"]
psycopg2_database = configData["psycopg2_database"]
psycopg2_user = configData["psycopg2_user"]
psycopg2_password = configData["psycopg2_password"]

#Prefix
bot = commands.Bot(command_prefix = myPrefix, case_insensitive = True)

#Removes Default Help Command
bot.remove_command("help")

#Event Log
@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Game("!help"))
    await bot.get_channel(myChannel).connect() #Connects to a discord channel
    print(bot.user.name)
    print(f"ID:  {bot.user.id}")
    print(f"Running on python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"Discord version {discord.__version__}")
    print("Connected to:")
    for guild in bot.guilds:
        print(guild.name)
    print("---------------------")
    #Adds Cogs
    bot.add_cog(CommandErrorHandler(bot))

#Error Handler (Command Error Cogs)
class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        #Command Not Found
        if isinstance(error, commands.CommandNotFound):
            return await ctx.send("That's not a command. Try `!help` for a list of commands.")

        #Cooldown
        elif isinstance(error, commands.CommandOnCooldown):
            seconds = int(error.retry_after)
            return await ctx.send(f"Whoa, buddy! Don't get snippy on me! ({seconds // 60}:{(seconds % 60):02d} remaining)")
        
        #Missing Required Arguments
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Please type the command with all the required arguments.")

        #Bad Argument
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("Please type the command with the correct types of arguments.")

#Database Class
class DBcall:
    #Opens Database
    @staticmethod
    def db_connect():
        #Connects To PostgreSQL
        con = psycopg2.connect(
            host = psycopg2_host,
            database = psycopg2_database,
            user = psycopg2_user,
            password = psycopg2_password)
        #Cursor
        cur = con.cursor()
        #Returns Variables
        return con, cur
    #Updates For New Users
    @staticmethod
    def db_new(function, user):
        function("""INSERT INTO INFORMATION VALUES(
            %s, %s, 0, 0, 0, 0, 0, %s, %s, %s, %s, %s, %s, 0)""",
            (user.id,
            str(user),
            str(user.joined_at),
            str(user.top_role),
            random.randint(12, 100),
            random.choice(["A", "B", "C", "D"]),
            random.choice(["Architect", "Artist", "Educator", "Entrepreneur", "Farmer", "Manufacturer", "Merchant", "Politician", "Programmer", "Scientist"]),
            random.choice(["Archery", "Baking", "Basketball", "Camping", "Chess", "Cooking", "Dance", "Drawing", "Gamer", "Gardening", "Hiking", "Hunting", "Kissing", "Learning", "Music", "Painting", "Photography", "Pottery", "Sewing", "Writing"])))

#Database
@bot.event
async def on_message(message):
    #Returns On Bot Message
    if message.author.bot:
        return

    #Makes Commands Work
    if message.content.startswith("!"):
        await bot.process_commands(message)

    #Opens Database
    con, cur = DBcall.db_connect()

    #Makes User ID A String
    user_id = str(message.author.id)

    #Gives Experience/Fame
    cur.execute(f"""SELECT COUNT(*) FROM INFORMATION WHERE "ID" = {user_id}""")
    if cur.fetchone()[0]: #This checks if the user ID is in the database.
        #Last Earned Every Minute
        cur.execute(f"""SELECT "Last Earned" FROM INFORMATION WHERE "ID" = {user_id}""")
        if int(time.time()) - cur.fetchone()[0] > 60:
            #Gives Fame
            cur.execute(f"""SELECT "Level" FROM INFORMATION WHERE "ID" = {user_id}""")
            if cur.fetchone()[0] == 20:
                cur.execute(f"""UPDATE INFORMATION SET "Fame" = "Fame" + 1 WHERE "ID" = {user_id}""")
                cur.execute(f"""UPDATE INFORMATION SET "Last Earned" = {int(time.time())} WHERE "ID" = {user_id}""")
            #Gives Experience
            else:
                cur.execute(f"""UPDATE INFORMATION SET "Experience" = "Experience" + 1 WHERE "ID" = {user_id}""")
                cur.execute(f"""UPDATE INFORMATION SET "Last Earned" = {int(time.time())} WHERE "ID" = {user_id}""")
                #Variables
                cur.execute(f"""SELECT "Experience" FROM INFORMATION WHERE "ID" = {user_id}""")
                exp = cur.fetchone()[0]
                cur.execute(f"""SELECT "Level" FROM INFORMATION WHERE "ID" = {user_id}""")
                lvl = cur.fetchone()[0]
                #Level Up
                if exp > int((lvl * 1.5) ** 1.9407390484):
                    cur.execute(f"""UPDATE INFORMATION SET "Level" = "Level" + 1 WHERE "ID" = {user_id}""")
                    cur.execute(f"""SELECT "Level" FROM INFORMATION WHERE "ID" = {user_id}""")
                    lvl = cur.fetchone()[0]
                    cur.execute(f"""UPDATE INFORMATION SET "Experience" = 0 WHERE "ID" = {user_id}""")
                    #Channel To Send In
                    channel = bot.get_channel(436690172143468546)
                    #Level 5 Role
                    if lvl == 5:
                        role_5 = discord.utils.get(message.author.guild.roles, name = "Level 5")
                        await message.author.add_roles(role_5)
                        await channel.send(f"Hey {message.author.mention}, you now have the Level 5 role.")
                    #Level 10 Role
                    elif lvl == 10:
                        role_10 = discord.utils.get(message.author.guild.roles, name = "Level 10")
                        await message.author.add_roles(role_10)
                        await channel.send(f"Hey {message.author.mention}, you now have the Level 10 role.")
                    #Level 15 Role
                    elif lvl == 15:
                        role_15 = discord.utils.get(message.author.guild.roles, name = "Level 15")
                        await message.author.add_roles(role_15)
                        await channel.send(f"Hey {message.author.mention}, you now have the Level 15 role.")
                    #Level 20 Role
                    elif lvl == 20:
                        role_20 = discord.utils.get(message.author.guild.roles, name = "Level 20")
                        await message.author.add_roles(role_20)
                        await channel.send(f"Hey {message.author.mention}, you now have the Level 20 role. Congratulations on reaching the final level! Any experience gained from now on will be turned into fame.")
    #Puts New User In Database
    else:
        DBcall.db_new(cur.execute, message.author)

    #Closes Cursor
    cur.close()
    #Saves Changes
    con.commit()
    #Stops Connection To PostgreSQL
    con.close()

#Nothing For Bump Command On DISBOARD Bot
@bot.command()
async def d(ctx):
    return

#GENERAL COMANDS ----------------------------------------------------------------------------------------------------
#Help Command
@bot.command(name = "help")
@commands.cooldown(1, 3, commands.BucketType.user)
async def help(ctx):
    embed = discord.Embed(
        title = "ALEX BOT INFORMATION",
        description = "All commands", color = 0xf600ff)
    #General Commands
    embed.add_field(
        name = "GENERAL COMMANDS",
        value = """
        `!help`
        Alex Bot displays a list of commands.

        `!hello`
        Alex Bot greets you!

        `!rank` **(opt: @user)**
        Alex Bot displays the rank of a particular user.

        `!refresh`
        Alex Bot refreshes your data in its database.

        `!joke`
        Alex Bot tells a funny joke.

        `!roast`
        Alex Bot roasts you.

        `!countdown` **(1 - 10)**
        Alex Bot counts down to 0.

        `!tyler`
        Alex Bot displays a Tyler of his choice.

        `!avatar` **(opt: @user)**
        Alex Bot displays the profile picture of a particular user in full resolution. (It might take some time if the picture is a GIF.)

        `!info` **(opt: @user)**
        Alex Bot displays information about a particular user.""")
    #Economy Commands
    embed.add_field(
        name = "ECONOMY COMMANDS",
        value = """
        `!balance` **(opt: @user)**
        Alex Bot displays the balance of a particular user.

        `!deposit` **(amount)**
        You deposit your money into your bank.

        `!withdraw` **(amount)**
        You withdraw your money from your bank.

        `!transfer` **(@user) (amount)**
        You transfer money from your pocket to a particular user.

        `!work`
        You work for money.

        `!flip` **(opt: h/t) (opt: amount)**
        Alex Bot flips a coin and you could bet on it.""")
    await ctx.send(embed = embed)

#Hello Command
@bot.command(name = "hello")
@commands.cooldown(1, 3, commands.BucketType.user)
async def hello(ctx):
    messages = [
        "BEEP BEEP BOOP! I'M ALEX BOT!",
        "ALEX BOT HERE!",
        "ALEX BOT, REPORTING FOR DUTY!",
        "NO NEED FOR DRIPPIN' SAUCE, JUST ALEX BOT!"
        ]
    await ctx.send(random.choice(messages))

#Rank Command
@bot.command(name = "rank")
@commands.cooldown(1, 3, commands.BucketType.user)
async def rank(ctx, user: discord.Member = None):
    #Defaults To The Author When No Argument Given
    if user == None:
        user = ctx.author
    
    #Opens Database
    con, cur = DBcall.db_connect()

    #Retrieves Information
    cur.execute(f"""SELECT COUNT(*) FROM INFORMATION WHERE "ID" = {user.id}""")
    if cur.fetchone()[0]:
        #Variables
        cur.execute(f"""SELECT "Experience" FROM INFORMATION WHERE "ID" = {user.id}""")
        exp = cur.fetchone()[0] + 1
        cur.execute(f"""SELECT "Level" FROM INFORMATION WHERE "ID" = {user.id}""")
        lvl = cur.fetchone()[0]
        cur.execute(f"""SELECT "Fame" FROM INFORMATION WHERE "ID" = {user.id}""")
        fame = cur.fetchone()[0]
    #Creates Information
    else:
        DBcall.db_new(cur.execute, user)
        #Saves Changes
        con.commit()
        #Variables
        cur.execute(f"""SELECT "Experience" FROM INFORMATION WHERE "ID" = {user.id}""")
        exp = cur.fetchone()[0]
        cur.execute(f"""SELECT "Level" FROM INFORMATION WHERE "ID" = {user.id}""")
        lvl = cur.fetchone()[0]
        cur.execute(f"""SELECT "Fame" FROM INFORMATION WHERE "ID" = {user.id}""")
        fame = cur.fetchone()[0]

    #Closes Cursor
    cur.close()
    #Stops Connection To PostgreSQL
    con.close()
    
    #Consistency
    if exp > int((lvl * 1.5) ** 1.9407390484):
        lvl += 1
        exp = 0

    #Sends Message
    if lvl != 20:
        await ctx.send(f"{user.mention} is LVL {lvl} with {exp} EXP and {fame} FAME. {int((lvl * 1.5) ** 1.9407390484) - exp} EXP required to level up.")
    else:
        fame += 1
        await ctx.send(f"{user.mention} is LVL {lvl} with {exp} EXP and {fame} FAME.")

#Refresh Command (add a refresh to the name in database and other stuff)
@bot.command(name = "refresh")
@commands.cooldown(1, 600, commands.BucketType.user)
async def refresh(ctx):
    #Opens Database
    con, cur = DBcall.db_connect()

    #Variables
    user = ctx.author
    give = []

    #Retrieves Information
    cur.execute(f"""SELECT COUNT(*) FROM INFORMATION WHERE "ID" = {user.id}""")
    if cur.fetchone()[0]:
        #Variable
        cur.execute(f"""SELECT "Level" FROM INFORMATION WHERE "ID" = {user.id}""")
        lvl = cur.fetchone()[0]
    #Creates Information
    else:
        return await ctx.send("Refreshed!")

    #Closes Cursor
    cur.close()
    #Stops Connection To PostgreSQL
    con.close()

    #Gives Roles
    for i in range(20, 0, -5):
        if lvl > i:
            give.append(discord.utils.get(user.guild.roles, name = f"Level {i}"))
    await user.add_roles(*give)
    await ctx.send("Refreshed!")

#Joke Command
@bot.command(name = "joke")
@commands.cooldown(1, 3, commands.BucketType.user)
async def joke(ctx):
    messages = [
        "An old lady asked me to help check her _balance._ **So, I pushed her over!**",
        "I bought some _shoes_ from a drug dealer. I don't know what he **laced** them with, but I've been **tripping** all day!",
        "I told a girl that she drew her _eyebrows_ too high. She seemed **surprised!**",
        "I'm so good at _sleeping_ that I can do it with my **eyes closed!**",
        "If you _look_ really closely, all mirrors look like **eyeballs!**",
        "What do you call a guy with a _rubber toe?_ **Roberto!**",
        "A _blind_ man walks into a bar. And a table. **And a chair.**",
        "I know a lot of jokes about _unemployed_ people, but none of them **work!**",
        "I couldn't figure out why the baseball kept getting _larger_...then it **hit me.**",
        "Why did the old man fall in the _well?_ Because he couldn't see **that well!**",
        "I ate a _clock_ yesterday; it was very **time consuming.**",
        "What did the _traffic light_ say to the car? Don't look! I'm about to **change.**",
        "Did you hear about the restaurant on the _moon?_ Great food, **no atmosphere.**",
        "What two things can you never eat for _breakfast?_ **Lunch and dinner.**"]
    await ctx.send(random.choice(messages))

#Roast Command
@bot.command(name = "roast")
@commands.cooldown(1, 3, commands.BucketType.user)
async def roast(ctx):
    user = ctx.author
    messages = [
        f"{user.mention} You look ugly!",
        f"Ew, {user.mention} is here."]
    await ctx.send(random.choice(messages))

#Countdown Command
@bot.command(name = "countdown", aliases = ["cd"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def countdown(ctx, number:int):
    #Range Error
    if number <= 0 or number > 10:
        return await ctx.send('Keep the number in the range of 1 to 10.')
    #Sends Number
    countdown_message = await ctx.send(number)
    await asyncio.sleep(1)
    #Edits Number
    for i in range(number - 1, 0, -1):
        await countdown_message.edit(content = i)
        await asyncio.sleep(1)
    await countdown_message.edit(content = "GO!")

#Tyler Command
@bot.command(name = "tyler", aliases = ["t"])
@commands.cooldown(1, 3, commands.BucketType.user)
async def tyler(ctx):
    messages_basic = [
        "This is Tyler.",
        "Hello Tyler!",
        "You look cute, Tyler!",
        "Oh Tyler...",
        "What are you doing, Tyler?"]
    
    #Writes message and uploads file
    my_files = os.listdir(tylerFolderPath)
    pick_pic = random.choice(my_files)
    return await ctx.send(random.choice(messages_basic), file = discord.File(os.path.join(tylerFolderPath, pick_pic)))

#Avatar Command
@bot.command(name = "avatar", aliases = ["ava"])
@commands.cooldown(1, 3, commands.BucketType.user)
async def avatar(ctx, user: discord.Member = None):
    #Defaults To The Author When No Argument Given
    if user == None:
        user = ctx.author
    
    #Variable
    var = io.BytesIO()

    #Saves URL
    await user.avatar_url.save(var)
    if user.is_avatar_animated():
        avatar = discord.File(var, filename = 'Beautiful.gif')
    else:
        avatar = discord.File(var, filename = 'Beautiful.webp')
    
    #Sends Avatar
    await ctx.send(file = avatar)

#Info Command
@bot.command(name = "info")
@commands.cooldown(1, 3, commands.BucketType.user)
async def info(ctx, user: discord.Member = None):
    #Defaults To The Author When No Argument Given
    if user == None:
        user = ctx.author

    #Opens Database
    con, cur = DBcall.db_connect()

    #Retrieves Information
    cur.execute(f"""SELECT COUNT(*) FROM INFORMATION WHERE "ID" = {user.id}""")
    if cur.fetchone()[0]:
        #Variables
        cur.execute(f"""SELECT "First Joined" FROM INFORMATION WHERE "ID" = {user.id}""")
        first_joined = cur.fetchone()[0].strftime(f"%b %d, %Y")
        cur.execute(f"""SELECT "Highest Role" FROM INFORMATION WHERE "ID" = {user.id}""")
        highest_role = cur.fetchone()[0]
        cur.execute(f"""SELECT "Age" FROM INFORMATION WHERE "ID" = {user.id}""")
        age = cur.fetchone()[0]
        cur.execute(f"""SELECT "Gender" FROM INFORMATION WHERE "ID" = {user.id}""")
        gender = cur.fetchone()[0]
        cur.execute(f"""SELECT "Occupation" FROM INFORMATION WHERE "ID" = {user.id}""")
        occupation = cur.fetchone()[0]
        cur.execute(f"""SELECT "Hobby" FROM INFORMATION WHERE "ID" = {user.id}""")
        hobby = cur.fetchone()[0]
    #Creates Information
    else:
        DBcall.db_new(cur.execute, user)
        #Saves Changes
        con.commit()
        #Variables
        cur.execute(f"""SELECT "First Joined" FROM INFORMATION WHERE "ID" = {user.id}""")
        first_joined = cur.fetchone()[0].strftime(f"%b %d, %Y")
        cur.execute(f"""SELECT "Highest Role" FROM INFORMATION WHERE "ID" = {user.id}""")
        highest_role = cur.fetchone()[0]
        cur.execute(f"""SELECT "Age" FROM INFORMATION WHERE "ID" = {user.id}""")
        age = cur.fetchone()[0]
        cur.execute(f"""SELECT "Gender" FROM INFORMATION WHERE "ID" = {user.id}""")
        gender = cur.fetchone()[0]
        cur.execute(f"""SELECT "Occupation" FROM INFORMATION WHERE "ID" = {user.id}""")
        occupation = cur.fetchone()[0]
        cur.execute(f"""SELECT "Hobby" FROM INFORMATION WHERE "ID" = {user.id}""")
        hobby = cur.fetchone()[0]

    #Closes Cursor
    cur.close()
    #Stops Connection To PostgreSQL
    con.close()

    #Embeds Message
    embed = discord.Embed(title = f"{user.name}", color = 0xf600ff)
    embed.add_field(name = "ID", value = user.id)
    embed.add_field(name = "FIRST JOINED", value = first_joined)
    embed.add_field(name = "HIGHEST ROLE", value = highest_role)
    embed.add_field(name = "AGE", value = age)
    embed.add_field(name = "GENDER", value = gender)
    embed.add_field(name = "OCCUPATION", value = occupation)
    embed.add_field(name = "HOBBY", value = hobby)
    embed.set_thumbnail(url = user.avatar_url)
    await ctx.send(embed = embed)

#ECONOMY COMANDS ----------------------------------------------------------------------------------------------------
#Balance Command
@bot.command(name = "balance", aliases = ["bal"])
@commands.cooldown(1, 3, commands.BucketType.user)
async def balance(ctx, user: discord.Member = None):
    #Opens Database
    con, cur = DBcall.db_connect()

    #Defaults To The Author When No Argument Given
    if user == None:
        user = ctx.author
    
    #Retrieves Information
    cur.execute(f"""SELECT COUNT(*) FROM INFORMATION WHERE "ID" = {user.id}""")
    if cur.fetchone()[0]:
        #Variables
        cur.execute(f"""SELECT "Pocket" FROM INFORMATION WHERE "ID" = {user.id}""")
        pocket = cur.fetchone()[0]
        cur.execute(f"""SELECT "Bank" FROM INFORMATION WHERE "ID" = {user.id}""")
        bank = cur.fetchone()[0]
        await ctx.send(f"{user.mention} has ${pocket} in their pocket and ${bank} locked up in their bank.")
    #Creates Information
    else:
        DBcall.db_new(cur.execute, user)
        #Saves Changes
        con.commit()
        #Variables
        cur.execute(f"""SELECT "Pocket" FROM INFORMATION WHERE "ID" = {user.id}""")
        pocket = cur.fetchone()[0]
        cur.execute(f"""SELECT "Bank" FROM INFORMATION WHERE "ID" = {user.id}""")
        bank = cur.fetchone()[0]
        await ctx.send(f"{user.mention} has ${pocket} in their pocket and ${bank} locked up in their bank.")

    #Closes Cursor
    cur.close()
    #Stops Connection To PostgreSQL
    con.close()

#Deposit Command
@bot.command(name = "deposit", aliases = ["dep"])
@commands.cooldown(1, 3, commands.BucketType.user)
async def deposit(ctx, amount):
    #Opens Database
    con, cur = DBcall.db_connect()

    #Variable
    user = ctx.author

    #Updates Information
    cur.execute(f"""SELECT COUNT(*) FROM INFORMATION WHERE "ID" = {user.id}""")
    if cur.fetchone()[0]:
        #Variable
        cur.execute(f"""SELECT "Pocket" FROM INFORMATION WHERE "ID" = {user.id}""")
        pocket = cur.fetchone()[0]
        #Converts All To Integer Amount
        if amount.lower() == "all":
            amount = pocket
            if amount == 0:
                return await ctx.send(f"{user.mention}, you don't have any money in your pocket.")
        #Consistency
        try:
            amount = int(amount)
            if amount <= 0 or amount != int(amount):
                raise ValueError
        except ValueError:
            return await ctx.send(f"{user.mention}, your amount must be a positive integer greater than 0.")
        if pocket - amount < 0:
            return await ctx.send(f"{user.mention}, you don't have ${amount} to deposit!")
        #Deposits Money
        cur.execute(f"""UPDATE INFORMATION SET "Pocket" = "Pocket" - {amount} WHERE "ID" = {user.id}""")
        cur.execute(f"""UPDATE INFORMATION SET "Bank" = "Bank" + {amount} WHERE "ID" = {user.id}""")
        await ctx.send(f"{user.mention} deposited ${amount} in their bank.")
    else:
        await ctx.send(f"{user.mention} please `!refresh` your data.")

    #Closes Cursor
    cur.close()
    #Saves Changes
    con.commit()
    #Stops Connection To PostgreSQL
    con.close()

#Withdraw Command
@bot.command(name = "withdraw", aliases = ["with"])
@commands.cooldown(1, 3, commands.BucketType.user)
async def withdraw(ctx, amount):
    #Opens Database
    con, cur = DBcall.db_connect()

    #Variable
    user = ctx.author
    
    #Updates Information
    cur.execute(f"""SELECT COUNT(*) FROM INFORMATION WHERE "ID" = {user.id}""")
    if cur.fetchone()[0]:
        #Variable
        cur.execute(f"""SELECT "Bank" FROM INFORMATION WHERE "ID" = {user.id}""")
        bank = cur.fetchone()[0]
        #Converts All To Integer Amount
        if amount.lower() == "all":
            amount = bank
            if amount == 0:
                return await ctx.send(f"{user.mention}, you don't have any money in your bank.")
        #Consistency
        try:
            amount = int(amount)
            if amount <= 0 or amount != int(amount):
                raise ValueError
        except ValueError:
            return await ctx.send(f"{user.mention}, your amount must be a positive integer greater than 0.")
        if bank - amount < 0:
            return await ctx.send(f"{user.mention}, you don't have ${amount} to withdraw!")
        #Withdraws Money
        cur.execute(f"""UPDATE INFORMATION SET "Bank" = "Bank" - {amount} WHERE "ID" = {user.id}""")
        cur.execute(f"""UPDATE INFORMATION SET "Pocket" = "Pocket" + {amount} WHERE "ID" = {user.id}""")
        await ctx.send(f"{user.mention} withdrew ${amount} from their bank.")
    else:
        await ctx.send(f"{user.mention} please `!refresh` your data.")

    #Closes Cursor
    cur.close()
    #Saves Changes
    con.commit()
    #Stops Connection To PostgreSQL
    con.close()

#Transfer Command
@bot.command(name = "transfer", aliases = ["give"])
@commands.cooldown(1, 3, commands.BucketType.user)
async def transfer(ctx, recipient: discord.Member, amount):
    #Opens Database
    con, cur = DBcall.db_connect()

    #Variables
    user = ctx.author
    
    #Recipient Cannot Be Sender
    if recipient.id == user.id:
        return await ctx.send(f"{user.mention}, you cannot send money to yourself.")

    #Retrieves Information (Checks If User Has Data)
    cur.execute(f"""SELECT COUNT(*) FROM INFORMATION WHERE "ID" = {recipient.id}""")
    if cur.fetchone()[0]:
        pass
    #Creates Information
    else:
        DBcall.db_new(cur.execute, recipient)
        #Saves Changes
        con.commit()
    
    #Updates Information
    cur.execute(f"""SELECT COUNT(*) FROM INFORMATION WHERE "ID" = {user.id}""")
    if cur.fetchone()[0]:
        #Variable
        cur.execute(f"""SELECT "Pocket" FROM INFORMATION WHERE "ID" = {user.id}""")
        pocket = cur.fetchone()[0]
        #Converts All To Integer Amount
        if amount.lower() == "all":
            amount = pocket
            if amount == 0:
                return await ctx.send(f"{user.mention}, you don't have any money in your pocket.")
        #Consistency
        try:
            amount = int(amount)
            if amount <= 0 or amount != int(amount):
                raise ValueError
        except ValueError:
            return await ctx.send(f"{user.mention}, your amount must be a positive integer greater than 0.")
        if pocket - amount < 0:
            return await ctx.send(f"{user.mention}, you don't have ${amount} in your pocket.")
        #Transfers Money
        cur.execute(f"""UPDATE INFORMATION SET "Pocket" = "Pocket" - {amount} WHERE "ID" = {user.id}""")
        cur.execute(f"""UPDATE INFORMATION SET "Pocket" = "Pocket" + {amount} WHERE "ID" = {recipient.id}""")
        await ctx.send(f"{user.mention} transfered ${amount} to {recipient.mention}!")
    else:
        await ctx.send(f"{user.mention} please `!refresh` your data.")

    #Closes Cursor
    cur.close()
    #Saves Changes
    con.commit()
    #Stops Connection To PostgreSQL
    con.close()

#Work Command
@bot.command(name = "work")
@commands.cooldown(1, 300, commands.BucketType.user)
async def work(ctx):
    #Opens Database
    con, cur = DBcall.db_connect()

    #Variables
    user = ctx.author
    give_money = random.randint(10, 50)

    #Updates Information
    cur.execute(f"""SELECT COUNT(*) FROM INFORMATION WHERE "ID" = {user.id}""")
    if cur.fetchone()[0]:
        cur.execute(f"""UPDATE INFORMATION SET "Pocket" = "Pocket" + {give_money} WHERE "ID" = {user.id}""")
        await ctx.send(f"{user.mention} earned ${give_money}!")
    else:
        DBcall.db_new(cur.execute, user)
        #Saves Changes
        con.commit()
        #Updates Information
        cur.execute(f"""UPDATE INFORMATION SET "Pocket" = "Pocket" + {give_money} WHERE "ID" = {user.id}""")
        await ctx.send(f"{user.mention} earned ${give_money}!")

    #Closes Cursor
    cur.close()
    #Saves Changes
    con.commit()
    #Stops Connection To PostgreSQL
    con.close()

#Flip Command
@bot.command(name = "flip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def flip(ctx, choice = None, amount = None):
    #Opens Database
    con, cur = DBcall.db_connect()

    #Variable
    user = ctx.author

    #Retrieves Information
    cur.execute(f"""SELECT COUNT(*) FROM INFORMATION WHERE "ID" = {user.id}""")
    if cur.fetchone()[0]:
        #Pocket Money
        cur.execute(f"""SELECT "Pocket" FROM INFORMATION WHERE "ID" = {user.id}""")
        pocket = cur.fetchone()[0]
    
    #Fail Safe On Flip Choice
    if choice == None:
        pass
    elif choice.isnumeric() and amount == None:
        amount = str(choice)
        choice = "heads"
    elif choice.lower() == "all":
        amount = "all"
        choice = "heads"
    elif choice.lower() not in ["heads", "h", "tails", "t"]:
        return await ctx.send("You need to either bet on heads, tails, or don't bet at all.")
    elif amount.lower() in ["heads", "h", "tails", "t"]:
        return await ctx.send("Nope.")

    #Fail Safe On Flip Amount
    if amount == None:
        amount = 0
        choice = None
    elif amount.isnumeric():
        amount = int(amount)
        if int(amount) == 0:
            choice = None
        elif pocket - amount < 0:
            return await ctx.send(f"{user.mention}, you don't have ${amount} in your pocket.")
    elif amount.lower() == "all" and choice.lower() in ["heads", "h", "tails", "t"]:
        amount = int(pocket)
        if amount == 0:
            return await ctx.send(f"{user.mention}, you don't have any money in your pocket.")
    else:
        raise commands.BadArgument
    
    #Heads
    if random.randint(1, 2) == 1:
        await ctx.send("Heads!")
        #Win
        if choice.lower() in ["heads", "h"]:
            cur.execute(f"""UPDATE INFORMATION SET "Pocket" = "Pocket" + {amount} WHERE "ID" = {user.id}""")
            await ctx.send(f"{user.mention} won +${amount}!")
        #No Bet
        elif choice == None:
            return
        #Lose
        else:
            cur.execute(f"""UPDATE INFORMATION SET "Pocket" = "Pocket" - {amount} WHERE "ID" = {user.id}""")
            await ctx.send(f"{user.mention} lost -${amount}!")
    #Tails
    else:
        await ctx.send("Tails!")
        #Win
        if choice.lower() in ["tails", "t"]:
            cur.execute(f"""UPDATE INFORMATION SET "Pocket" = "Pocket" + {amount} WHERE "ID" = {user.id}""")
            await ctx.send(f"{user.mention} won +${amount}!")
        #No Bet
        elif choice == None:
            return
        #Lose
        else:
            cur.execute(f"""UPDATE INFORMATION SET "Pocket" = "Pocket" - {amount} WHERE "ID" = {user.id}""")
            await ctx.send(f"{user.mention} lost -${amount}!")
    
    #Closes Cursor
    cur.close()
    #Saves Changes
    con.commit()
    #Stops Connection To PostgreSQL
    con.close()

#Bot Token
bot.run(myToken, reconnect = False)