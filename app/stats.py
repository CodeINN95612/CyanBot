import datetime

from . import storage
from . import config


def parseGlobalStats(data):
    roles = config.config["roles"]
    today = datetime.datetime.today()
    past = today - datetime.timedelta(days=30)

    gstats = []

    h1 = ['Type', '30 Days', 'All-time']
    stats1 = {}
    for msg in data:
        role = msg["function"]
        date = datetime.datetime.fromtimestamp(msg["date"])
        if role not in stats1:
            stats1[role] = {"name": role,  "30": 0, "total": 0}
        if date >= past:
            stats1[role]["30"] += 1
        stats1[role]["total"] += 1
    stats1 = dict(
        sorted(stats1.items(), key=lambda x: x[1]['30'], reverse=True))
    gstats.append((h1, stats1))

    for role in [role["name"] for role in roles]:
        h = ["User", f"{role} 30 Days", f"{role} (All)"]
        stats = {}
        for msg in [msg for msg in data if msg["function"].lower() == role.lower()]:
            userId = msg["authorId"]
            user = msg["authorName"]
            if userId not in stats:
                stats[userId] = {"name": user,
                                 f"{role}_30": 0, f"{role}_all": 0}
            date = datetime.datetime.fromtimestamp(msg["date"])
            if date >= past:
                stats[userId][f"{role}_30"] += 1
            stats[userId][f"{role}_all"] += 1
        stats = dict(
            sorted(stats.items(), key=lambda x: x[1][f'{role}_30'], reverse=True))
        gstats.append((h, stats))

    gstats = [(h, _numerate(stat)) for h, stat in gstats]
    gstats = [(h, _toArr(stat)) for h, stat in gstats]
    gstats = [(h, _addTotal(stat)) for h, stat in gstats]
    gstats = [(h, _parseIfEmpty(h, stat)) for h, stat in gstats]

    return gstats


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

    stats = dict(
        sorted(stats.items(), key=lambda x: x[1]['30'], reverse=True))
    stats = _numerate(stats)
    stats = _toArr(stats)
    stats = _addTotal(stats)
    stats = _parseIfEmpty(h, stats)

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

    stats1 = dict(
        sorted(stats1.items(), key=lambda x: x[1]['30'], reverse=True))
    stats1 = _numerate(stats1)
    stats1 = _toArr(stats1)
    stats1 = _addTotal(stats1)
    stats1 = _parseIfEmpty(h1, stats1)

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

    stats2 = dict(
        sorted(stats2.items(), key=lambda x: float("inf") if x[1]["daysAgo"] == "" else float(x[1]["daysAgo"]), reverse=False))
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


def _parseIfEmpty(h, stats):
    if len(stats) == 1:
        stats[0] = ['Total' if i == 0 else '0' for (i, _) in enumerate(h)]
    return stats


def _numerate(stats):
    for i, id in enumerate(stats, start=1):
        try:
            stats[id]["name"] = str(i) + ". " + stats[id]["name"]
        except Exception as e:
            pass
    return stats
