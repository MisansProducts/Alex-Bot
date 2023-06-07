#======Libraries======
import discord
import random

#======Commands======
async def command(message, user_message, is_private):
    #HELLO COMMAND
    if user_message == "hello":
        responses = [
            "BEEP BEEP BOOP! I'M ALEX BOT!",
            "ALEX BOT HERE!",
            "ALEX BOT, REPORTING FOR DUTY!",
            "NO NEED FOR DRIPPIN' SAUCE, JUST ALEX BOT!"
        ]

        response = random.choice(responses)
        await message.author.send(response) if is_private else await message.channel.send(response)
    #HELP COMMAND
    elif user_message == "help":
        embed = discord.Embed(
            title = "ALEX BOT INFORMATION",
            description = "All commands",
            color = 0xf600ff
        )
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
            Alex Bot displays information about a particular user.
            """
        )
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
            Alex Bot flips a coin and you could bet on it.
            """
        )
        
        await message.author.send(embed = embed) if is_private else await message.channel.send(embed = embed)
    
    return