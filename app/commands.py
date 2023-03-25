from . import config, storage, stats as st, globals
from .types import CmdArgs, DeleteArgs
import discord
import datetime
import asyncio
from tabulate import tabulate


async def manage_commands(args: CmdArgs):

    msg, _, userId, isCommand, _, isSubmit, isAdmin, _ = args

    if isCommand and isAdmin and userId in config.config["admins"]:

        if msg.startswith("help"):
            await _cmdHelp(args)
        elif msg.startswith("up"):
            await _cmdUpdate(args)
        elif msg.startswith("st"):
            await _cmdStats(args)
        elif msg.startswith("al"):
            await _cmdAllow(args)
        elif msg.startswith("turnoff"):
            await _cmdOff(args)

        return

    if isSubmit:
        await _makeNew(args)


async def manage_delete(args: DeleteArgs):

    message, discordMessage, userId, serverId, *_ = args

    words = message.split()
    words = [word for word in words if '@' not in word]

    data = {
        "serverId": str(serverId),
        "authorId": str(userId),
        "authorName": discordMessage.author.name,
        "date": discordMessage.created_at.timestamp(),
        "content": message
    }

    valid, obj = storage.validateMessage(data)
    if not valid:
        return None

    if storage.deleteMessage(obj):
        return obj
    return None


async def _cmdHelp(args: CmdArgs):
    embed = discord.Embed(title="Lista de ajuda", color=0x0000ff)
    embed.add_field(name="help", value="Comando de ajuda", inline=True)
    embed.add_field(
        name="update", value="Receba as atualizações de empregos deste mês", inline=True)
    embed.add_field(
        name="stats [user/userID/role]", value="No caso de envio sem parâmetro, envia estatísticas globais, mas envia as estatísticas do usuário ou da função", inline=True)
    embed.add_field(name="allow <serie>",
                    value="Os usuários agora podem enviar séries com esse nome")
    embed.add_field(name="turnoff",
                    value="Este comando faz o bot desligar")
    await args[1].reply(embed=embed)


async def _cmdUpdate(args: CmdArgs):
    date = datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    filename = config.config["updateSpreadsheetName"]
    file = storage.IntoSpreadsheet(args[1], f"{filename}_{date}.xlsx")
    await args[1].reply(content=f"Arquivo de trabalho {date}", file=file)


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
        await testChannel.send(f"Inserindo Mensagem ```{args[0]}```")

    valid = storage.insertMessage(data)

    if not valid and testChannel:
        await testChannel.send(f"Mensagem não inserida")
    elif testChannel:
        await testChannel.send(f"Mensagem incorporada")


async def _cmdStats(args: CmdArgs):

    msg = args[0].split(" ")
    discordMessage = args[1]

    data = storage.getMessages()
    data = [p for p in data if p["serverId"] == str(discordMessage.guild.id)]
    roles = config.config["roles"]

    # Globales
    if len(msg) == 1:
        stats = st.parseGlobalStats(data)

        text = ""
        for stat in stats:
            text += f"```{_intoTabulate(stat)}```\n"

        embed = discord.Embed(title="Estatísticas globais", color=0x0000ff,
                              description=text)
        await discordMessage.reply(embed=embed)

        return

    param = msg[1]

    # Rol
    if param in [role["name"].lower() for role in roles]:
        role = param
        stats = st.parseRoleStats(data, role)
        text = f"```{_intoTabulate(stats)}```"
        embed = discord.Embed(title=f"estatísticas de função {role}", color=0x0000ff,
                              description=text)
        await discordMessage.reply(embed=embed)
        return

    # Usuario
    userName = param
    userId = 0
    for member in discordMessage.guild.members:
        names = [str(member.id), member.display_name.lower(),
                 member.name.lower()]
        if userName in names:
            userId = member.id
            break

    if userId == 0:
        embed = discord.Embed(
            title="Not found", description=f"Usuário não encontrado {userName}", color=0xff0000)
        await discordMessage.reply(embed=embed)
        return

    stats1, stats2 = st.parseUserStats(data, userId)
    text = f"```{_intoTabulate(stats1)}```\n ```{_intoTabulate(stats2)}```\n"
    embed = discord.Embed(title=f"Estatísticas do usuário {userName}", color=0x0000ff,
                          description=text)
    await discordMessage.reply(embed=embed)


def _intoTabulate(stats):
    headers, data = stats
    return tabulate(data, headers=headers, tablefmt="fancy_grid")


async def _cmdAllow(args: CmdArgs):
    _, dm, *_, msgCase = args
    msg = msgCase.split(" ")
    if len(msg) == 1:
        await _cmdHelp(args)
        return

    serie = " ".join(msg[1::])

    if not storage.isAllowed(serie):
        storage.addAllowed(serie)
    await dm.reply(f"Adicionado '{serie}' às séries permitidas")


async def _cmdOff(args: CmdArgs):
    _, msg, _, _, client, *_ = args
    user = msg.author.name
    embed = discord.Embed(title="Desligando o Bot", color=0xff0000,
                          description=f"A usuário {user} desligou o bot")
    await msg.reply(embed=embed)
    await client.close()
    globals.RUNNING = False
    await asyncio.sleep(1)
