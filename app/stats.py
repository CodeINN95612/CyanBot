import datetime
from . import storage, config


def parseGlobalStats(data):
    h1 = ['Type', '30 Days', 'All-time']
    h2 = ['Users (30 Days)']
    h3 = ['User (All)']
    roles = config.config["roles"]
    for role in roles:
        h2.append(role["name"])
        h3.append(role["name"])

    today = datetime.datetime.today()
    past = today - datetime.timedelta(days=30)

    stats1 = {}
    for msg in data:
        role = msg["function"]
        date = datetime.datetime.fromtimestamp(msg["date"])
        if role not in stats1:
            stats1[role] = {"name": role,  "30": 0, "total": 0}
        if date >= past:
            stats1[role]["30"] += 1
        stats1[role]["total"] += 1

    stats2 = {}
    for msg in data:
        userId = msg["authorId"]
        user = msg["authorName"]
        if userId not in stats2:
            stats2[userId] = {"name": user}
            for role in roles:
                stats2[userId][role["name"]] = 0
        date = datetime.datetime.fromtimestamp(msg["date"])
        if date >= past:
            stats2[userId][msg["function"]] += 1

    stats3 = {}
    for msg in data:
        userId = msg["authorId"]
        user = msg["authorName"]
        if userId not in stats3:
            stats3[userId] = {"name": user}
            for role in roles:
                stats3[userId][role["name"]] = 0
        stats3[userId][msg["function"]] += 1

    # transformar a arreglos
    stats1 = _toArr(stats1)
    stats2 = _toArr(stats2)
    stats3 = _toArr(stats3)

    # Agregar Totales
    stats1 = _addTotal(stats1)
    stats2 = _addTotal(stats2)
    stats3 = _addTotal(stats3)

    return (h1, stats1), (h2, stats2), (h3, stats3)


def parseRoleStats(data, role):

    today = datetime.datetime.today()
    past = today - datetime.timedelta(days=30)

    h = ['User', '30 Days', 'All-time']
    stats = {}
    for msg in data:
        if msg["function"].lower() != role:
            continue

        userId = msg["authorId"]
        user = msg["authorName"]
        if userId not in stats:
            stats[userId] = {"name": user, "30": 0, "total": 0}
        date = datetime.datetime.fromtimestamp(msg["date"])
        if date >= past:
            stats[userId]["30"] += 1
        stats[userId]["total"] += 1

    stats = _toArr(stats)
    stats = _addTotal(stats)

    return (h, stats)


def parseUserStats(data, id):
    h1 = ['Type', '30 Days', 'All-time']
    h2 = ['Type', 'Days Ago', 'Series', 'Chapter']

    today = datetime.datetime.today()
    past = today - datetime.timedelta(days=30)

    data = sorted(data, key=lambda x: x["date"])

    stats1 = {}
    for msg in data:

        if msg["authorId"] != str(id):
            continue

        role = msg["function"]
        date = datetime.datetime.fromtimestamp(msg["date"])
        if role not in stats1:
            stats1[role] = {"name": role,  "30": 0, "total": 0}
        if date >= past:
            stats1[role]["30"] += 1
        stats1[role]["total"] += 1
    stats1 = _toArr(stats1)
    stats1 = _addTotal(stats1)

    stats2 = {}
    for role in config.config["roles"]:
        stats2[role["name"]] = {
            "role": role["name"], "daysAgo": "", "serie": "", "cap": ""}
    for msg in data:

        if msg["authorId"] != str(id):
            continue

        role = msg["function"]
        date = datetime.datetime.fromtimestamp(msg["date"])
        dias = (today - date).days
        serie = msg["serie"]
        if len(serie) > 20:
            serie = serie[:17] + "..."

        stats2[role]["daysAgo"] = str(dias)
        stats2[role]["serie"] = serie
        stats2[role]["cap"] = msg["chapter"]

    stats2 = _toArr(stats2)

    return (h1, stats1), (h2, stats2)


def _toArr(stats):
    statArr = []
    for stat in stats:
        values = list(stats[stat].values())
        statArr.append(values)
    return statArr


def _addTotal(stats):
    stats.append(["Total"] + [sum(col) for col in list(zip(*stats))[1:]])
    return stats
