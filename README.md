# Alex Bot

Alex Bot is a bot for Discord I created to test out creative features for my Discord server. I originally wanted a bot to display a random picture of my friend named "Tyler" along with a funny caption. Since then, I expanded the bot to be more versatile. So far, this project includes 16 commands.

Commands:
* `!help` - Alex Bot displays a list of commands.
* `!hello` - Alex Bot greets you!
* `!rank [opt: @user]` - Alex Bot displays the rank of a particular user.
* `!refresh` - Alex Bot refreshes your data in its database.
* `!joke` - Alex Bot tells a funny joke.
* `!roast` - Alex Bot roasts you.
* `!countdown [1-10]` - Alex Bot counts down to 0.
* `!tyler` - Alex Bot displays a Tyler of his choice.
* `!avatar [opt: @user]` - Alex Bot displays the profile picture of a particular user in full resolution. (It might take some time if the picture is a GIF.)
* `!info [opt: @user]` - Alex Bot displays information about a particular user.
* `!balance [opt: @user]` - Alex Bot displays the balance of a particular user.
* `!deposit [amount]` - You deposit your money into your bank.
* `!withdraw [amount]` - You withdraw your money from your bank.
* `!transfer [@user] [amount]` - You transfer money from your pocket to a particular user.
* `!work` - You work for money.
* `!flip [opt: h/t] [opt: amount]` - Alex Bot flips a coin and you could bet on it.

Included is the "Tyler" folder with a few sample images. You can change the images to whatever you want and change the source code for the `!tyler` command to suit your needs.

Most of the features rely on a connection to some sort of database so that the bot can save information about users. I chose to use PostgreSQL because you can easily interact with the data in real time and see pretty graphic representations on pgAdmin.

When you first open `main.py`, a JSON file named `config.json` will be created in the same directory. Open this file and fill in the relevant information.

Config file:
* **myToken** - Your bot token for the discord API.
* **myPrefix** - An optional prefix to use commands. Default is "!".
* **myChannel** - The voice channel ID for Alex Bot to connect to.
* **psycopg2_host** - Your host IP.
* **psycopg2_database** - Name of your database.
* **psycopg2_user** - Username for PostgreSQL.
* **psycopg2_password** - Password for PostgreSQL.

Make sure [Python](https://www.python.org/downloads/ "Download Python from www.python.org") is installed on your device before opening this file.

There are a few required libraries you need to install before using this program:
* `pip install -U discord.py[voice]` - To install Discord API functionality and the ability for the bot to connect to voice channels.
* `pip install psycopg2-binary` - For PostgreSQL support.
* `pip install asyncio` - Framework for code to work.

Download and install [PostgreSQL](https://www.postgresql.org/ "Visit www.postgresql.org") and use pgAdmin to setup your database.

Future updates will include:
* Database portability
    * Optionality to use a database or not
* Overhaul the !tyler command
* Hide and target feature to the !roast command
* The ability to play music in voice channels

## Credits

Alex Akoopie - Creator