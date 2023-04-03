from . import storage
from . import config, globals, spreadsheet as ss
import os
import json
import datetime
import discord


async def setUp():

    if not os.path.exists(globals.DATA_DIR):
        os.makedirs(globals.DATA_DIR)

    if not os.path.exists(globals.SERIES_FILE):
        with open(globals.SERIES_FILE, 'w') as f:
            json.dump({}, f)

    if not os.path.exists(globals.MSG_FILE):
        with open(globals.MSG_FILE, 'w') as f:
            json.dump([], f)

    if not os.path.exists(globals.ALLOWED_FILE):
        with open(globals.ALLOWED_FILE, 'w') as f:
            json.dump([], f)


async def scanMessages(discordClient: discord.Client):

    scanDays = config.config["scanDays"]
    testChannel = discordClient.get_channel(int(config.config["testChannel"]))
    if testChannel:
        await testChannel.send(f"Verificando mensagens dos últimos {scanDays} dias")

    messages = []

    channelId = config.config["submitChannel"]
    dateNow = datetime.datetime.utcnow()
    dateThen = dateNow - datetime.timedelta(days=scanDays)
    updateChannel = discordClient.get_channel(int(channelId))
    server_id = updateChannel.guild.id

    async for message in updateChannel.history(after=dateThen):

        if not isinstance(message, discord.Message) or message.author.bot:
            continue

        authorId = message.author.id
        authorName = message.author.display_name
        date = message.created_at.timestamp()
        content = message.content.lower()
        data = {
            "serverId": str(server_id),
            "authorId": str(authorId),
            "authorName": authorName,
            "date": date,
            "content": content
        }
        messages.append(data)

    validMessages = _validateMessages(messages)
    _parseOverwriteMessages(validMessages, globals.MSG_FILE)

    if testChannel:
        await testChannel.send(f"{len(validMessages)} mensagens verificadas")


def getMessages():
    with open(globals.MSG_FILE, 'r') as f:
        return json.load(f)


def insertMessage(message) -> bool:
    valid, obj = validateMessage(message)
    if not valid:
        return False
    _parseAppendMessage(obj, globals.MSG_FILE)
    return True


def deleteMessage(obj) -> bool:
    filename = globals.MSG_FILE
    with open(filename, 'r') as f:
        messages = json.load(f)

    removed = False
    for i, msg in enumerate(messages):
        if msg["serverId"] != obj["serverId"]:
            continue
        if msg["serie"].lower() != obj["serie"].lower():
            continue
        if msg["function"].lower() != obj["function"].lower():
            continue
        if msg["chapter"] != obj["chapter"]:
            continue

        del messages[i]
        removed = True
        break

    if removed:
        with open(filename, 'w') as f:
            json.dump(messages, f, indent=4)

    return removed


def getSeries():
    with open(globals.SERIES_FILE, 'r') as f:
        return json.load(f)


def upsertSerie(sId, chId):
    with open(globals.SERIES_FILE, 'r') as f:
        dataFile = json.load(f)

    dataFile[sId] = chId

    with open(globals.SERIES_FILE, 'w') as f:
        json.dump(dataFile, f, indent=4)


def addAllowed(name):
    with open(globals.ALLOWED_FILE, 'r') as f:
        dataFile = json.load(f)

    dataFile.append(name)

    with open(globals.ALLOWED_FILE, 'w') as f:
        json.dump(dataFile, f, indent=4)


def isAllowed(name):
    with open(globals.ALLOWED_FILE, 'r') as f:
        dataFile = json.load(f)

    return name.lower() in [s.lower() for s in dataFile]


def getAllowed():
    with open(globals.ALLOWED_FILE, 'r') as f:
        dataFile = json.load(f)
    return [s.lower() for s in dataFile]


def getAllowedRealName(loweredName):
    with open(globals.ALLOWED_FILE, 'r') as f:
        dataFile = json.load(f)
    name = [s for s in dataFile if s.lower() == loweredName.lower()][0]
    return name


def _validateMessages(messages):

    valid_messages = []

    for message in messages:
        valid, obj = validateMessage(message)
        if not valid:
            continue

        valid_messages.append(obj)

    return valid_messages


def validateMessage(message):
    content = message['content']
    words = content.split()
    words = [word for word in words if '@' not in word]

    if len(words) < 3:
        return (False, {})

    try:
        numbers = float(words[-1])
    except:
        return (False, {})

    role_name = words[-2]
    role_values = [r['name']
                   for r in config.config["roles"] if r['name'].lower() == role_name]

    if len(role_values) == 0:
        return (False, {})

    serie = " ".join(words[:-2])
    if not storage.isAllowed(serie):
        return (False, {})
    serie = storage.getAllowedRealName(serie)

    return (True, {
        "serverId": message["serverId"],
        "authorId": message["authorId"],
        "authorName": message["authorName"],
        "date": message["date"],
        "serie": serie,
        "function": role_values[0],
        "chapter": numbers
    })


def _parseAppendMessage(message, filename):
    with open(filename, 'r') as f:
        messages = json.load(f)
    messages.append(message)
    with open(filename, 'w') as f:
        json.dump(messages, f, indent=4)


def _parseAppendMessages(messages, filename):
    with open(filename, 'r') as file:
        existing_data = json.load(file)

    existing_data.extend(messages)

    with open(filename, 'w') as file:
        json.dump(existing_data, file, indent=4)


def _parseOverwriteMessages(messages, filename):
    with open(filename, 'w') as file:
        json.dump(messages, file, indent=4)


def IntoSpreadsheet(discordMessage: discord.Message, filename: str):
    with open(globals.MSG_FILE, 'r') as f:
        messagesFile = json.load(f)

    # filtrar servidor
    serverId = str(discordMessage.guild.id)
    now = datetime.datetime.now()
    ago = now - datetime.timedelta(days=config.config["scanDays"])
    messages = []
    for msg in messagesFile:
        if msg["serverId"] != serverId:
            continue
        date = datetime.datetime.fromtimestamp(msg["date"])
        if ago <= date <= now:
            messages.append(msg)

    # construir nueva data
    data = {}
    for msg in messages:
        id = msg["authorId"]
        if id not in data:
            data[id] = {
                "author": msg["authorName"],
                "totalWork": 0,
                "totalValue": 0.0,
                "roles": ""
            }
            for role in config.config["roles"]:
                role = role["name"]
                data[id][ss.valColName(role)] = 0.0
                data[id][ss.numColName(role)] = 0

        role = [role for role in config.config["roles"]
                if role["name"].lower() == msg["function"].lower()][0]
        roleName = role["name"]
        roleValue = role["value"]
        data[id]["totalWork"] += 1
        data[id]["totalValue"] += roleValue
        data[id][ss.valColName(roleName)] += roleValue
        data[id][ss.numColName(roleName)] += 1
        if data[id]["roles"] == "":
            data[id]["roles"] = roleName
        elif not roleName in data[id]["roles"].split():
            data[id]["roles"] += f" - {roleName}"

    # Archivo de Excel

    archivo = "./data/" + config.config["updateSpreadsheetName"] + '.xlsx'

    ss.createWorkbook(
        archivo, data, config.config["roles"], storage.getAllowed(), now, ago)

    with open(archivo, 'rb') as f:
        file = discord.File(f, filename=filename)
    return file
