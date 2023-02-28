from . import config, storage, stats as st
from .types import CmdArgs
import discord
import datetime
from tabulate import tabulate


async def manage_commands(args: CmdArgs):

    msg, discordMessage, userId, isCommand, _, isSubmit, isAdmin = args

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
    embed.add_field(
        name="stats [user/userID/role]", value="En caso de enviar sin parametro envia estadisticas globales, sino envia las estadisticas del usuario o del rol", inline=True)

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
    # return

    msg = args[0].split(" ")
    discordMessage = args[1]

    data = storage.getMessages()
    roles = config.config["roles"]

    # Globales
    if len(msg) == 1:
        stats1, stats2, stats3 = st.parseGlobalStats(data)

        text = f"```{_intoTabulate(stats1)}```\n ```{_intoTabulate(stats2)}```\n ```{_intoTabulate(stats3)}```\n "

        embed = discord.Embed(title="Estadísticas globales", color=0x0000ff,
                              description=text)
        await discordMessage.reply(embed=embed)

        return

    param = msg[1]

    # Rol
    if param in [role["name"].lower() for role in roles]:
        role = param
        stats = st.parseRoleStats(data, role)
        text = f"```{_intoTabulate(stats)}```"
        embed = discord.Embed(title=f"Estadísticas del rol {role}", color=0x0000ff,
                              description=text)
        await discordMessage.reply(embed=embed)
        return

    # Usuario
    userName = param
    userId = 0
    for member in discordMessage.guild.members:
        names = [member.id, member.display_name.lower(), member.name.lower()]
        if userName in names:
            userId = member.id
            break

    if userId == 0:
        embed = discord.Embed(
            title="Not found", description=f"No se encontro el usuario {userName}", color=0xff0000)
        await discordMessage.reply(embed=embed)
        return

    stats1, stats2 = st.parseUserStats(data, userId)
    text = f"```{_intoTabulate(stats1)}```\n ```{_intoTabulate(stats2)}```\n"
    embed = discord.Embed(title=f"Estadísticas del usuario {userName}", color=0x0000ff,
                          description=text)
    await discordMessage.reply(embed=embed)


def _intoTabulate(stats):
    headers, data = stats
    return tabulate(data, headers=headers, tablefmt="fancy_grid")
