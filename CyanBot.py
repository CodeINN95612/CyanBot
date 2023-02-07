import discord
import config
from spreadsheet import Spreadsheet

client = discord.Client()
sp = Spreadsheet(config.config["sheet_name"] + ".xlsx")


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user or message.bot:
        return

    sp.add_user(config.config["sheet_name"], message.author.name)

client.run(config.config["token"])
