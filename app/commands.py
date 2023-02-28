from . import config, storage, stats as st
from .types import CmdArgs
import discord
import datetime


async def manage_commands(args: CmdArgs):

    msg, _, userId, isCommand, _, isSubmit, isAdmin = args

    if isCommand and isAdmin and userId in config.config["admins"]:

        if msg.startswith("help"):
            await _cmdHelp(args)
        elif msg.startswith("up"):
            await _cmdUpdate(args)
        elif msg.startswith("st"):
            await _cmdStats(args)

        return

    if isSubmit:
        await _makeNew(args)


async def _cmdHelp(args: CmdArgs):
    embed = discord.Embed(title="Lista de Ayuda", color=0x0000ff)
    embed.add_field(name="help", value="Comando de Ayuda", inline=True)
    embed.add_field(
        name="update", value="Obtener las actualizaciones de trabajos de este mes", inline=True)

    await args[1].reply(embed=embed)


async def _cmdUpdate(args: CmdArgs):
    date = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    filename = config.config["updateSpreadsheetName"]
    file = storage.IntoSpreadsheet(args[1], f"{filename}_{date}.xlsx")
    await args[1].reply(content=f"Archivo de trabajos {date}", file=file)


async def _makeNew(args: CmdArgs):
    msg = args[1]
    discordClient = args[4]

    authorId = msg.author.id
    authorName = msg.author.display_name
    date = msg.created_at.timestamp()
    content = args[0]
    server_id = msg.guild.id
    data = {
        "serverId": str(server_id),
        "authorId": str(authorId),
        "authorName": authorName,
        "date": date,
        "content": content
    }

    testChannel = discordClient.get_channel(int(config.config["testChannel"]))
    if testChannel:
        await testChannel.send(f"Insertando Mensaje ```{args[0]}```")

    valid = storage.insertMessage(data)

    if not valid and testChannel:
        await testChannel.send(f"Mensaje no insertado")
    elif testChannel:
        await testChannel.send(f"Mensaje insertado")


async def _cmdStats(args: CmdArgs):
    return

    msg = args[0]
    discordMessage = args[1]

    data = storage.getMessages()
    roles = config.config["roles"]
    param = msg.split()[1]

    if len(msg) == 1:
        stats, (h1, h2) = st.parseGlobalStats(data)
    elif param in roles:
        role = param
        stats, header = st.parseRoleStats(data)
        pass
    else:
        userName = param
        userId = discordMessage.guild.get_member_named(userName)
        stats, (h1, h2) = st.parseUserStats(data, userId)
        pass
