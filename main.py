from app import config, commands as cmd, storage, updates, globals
from app.types import CmdArgs, DeleteArgs
import discord
import asyncio
import json

client = discord.Client(intents=discord.Intents.all())


@client.event
async def on_ready():
    print(f'{client.user} se conectou ao Discord!')

    testChannel = client.get_channel(int(config.config["testChannel"]))
    if testChannel:
        await testChannel.send(f"+++++++++++++++++++++++++++++++++++++++")
    await storage.scanMessages(client)


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user or message.author.bot:
        return

    if len(message.content) <= 1:
        return

    submitChannel = config.config["submitChannel"]
    isSubmit = message.channel.id == int(submitChannel)
    adminChannel = config.config["adminChannel"]
    isAdmin = message.channel.id == int(adminChannel)

    isCommand = message.content.startswith(config.config['prefix'])
    index = 1 if isCommand else 0
    wordArray = [word for word in message.content.split() if "@" not in word]
    msgCase = " ".join(wordArray)[index::]
    msg = msgCase.lower()
    userId = str(message.author.id)

    # Make developer life easier by separating the discord message
    args: CmdArgs = (msg, message, userId, isCommand,
                     client, isSubmit, isAdmin, msgCase)

    await cmd.manage_commands(args)


async def reloadConfig():
    while not client.is_ready():
        await asyncio.sleep(1)
    while globals.RUNNING:
        await asyncio.sleep(1)
        config.reload()


async def _updateHandler(update):
    embedTemplate = updates.getUpdateEmbed(update)
    embed = discord.Embed.from_dict(embedTemplate)

    # send update to test Channels
    testChannel = client.get_channel(int(config.config["testChannel"]))
    if (testChannel):
        ss = f'Updating in {config.config["discordDelay"]} seconds:\n```{json.dumps(update, indent=2)}```'
        try:
            await testChannel.send(ss)
        except discord.errors.Forbidden:
            pass

    # only update every so many minutes to avoid spamming
    await asyncio.sleep(config.config["discordDelay"])

    # Send Update to Update Channel
    for chId in config.config["updateChannels"]:
        if chId == '':
            continue

        updateChannel = client.get_channel(int(chId))
        await updateChannel.send(embed=embed)


async def checkUpdates():
    while not client.is_ready():
        await asyncio.sleep(1)
    while globals.RUNNING:
        try:
            await updates.checkUpdates(handler=_updateHandler)
            await asyncio.sleep(config.config["updateDelay"])
        except:
            pass
            # print(
            #   "ERRO: Não é possível atualizar, verifique a disponibilidade da página ou do html")


async def runBot():
    try:
        if globals.RUNNING:
            await client.start(config.config["token"])
    except Exception as e:
        print("Error: ", e)


async def main():
    await storage.setUp()
    await asyncio.gather(
        runBot(),
        reloadConfig(),
        checkUpdates(),
    )

if __name__ == "__main__":
    config.reload()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print("ERROR", e)
