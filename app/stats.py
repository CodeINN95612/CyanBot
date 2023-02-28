import datetime


def parseGlobalStats(data):
    h1 = ['Type', '30 Days', 'All-time']
    h2 = ['User', 'Users (30 days)', 'Users (all)']

    today = datetime.datetime.today()
    past = today - datetime.timedelta(days=30)

    stats1 = {}
    for msg in data:
        role = msg["function"]
        date = datetime.datetime.fromtimestamp(msg["date"])
        if role not in stats1:
            stats1[role] = {"30": 0, "total": 0}
        if date >= past:
            stats1[role]["30"] += 1
        stats1[role]["total"] += 1

    stats2 = {}
    for msg in data:
        role = msg["function"]
        date = datetime.datetime.fromtimestamp(msg["date"])
        if role not in stats2:
            stats2[role] = {"30": 0, "total": 0}
        if date >= past:
            stats2[role]["30"] += 1
        stats1[role]["total"] += 1

    return (h1, stats1), (h2, stats2)


def parseRoleStats(data, role):

    h = ['User', '30 Days', 'All-time']


def parseUserStats(data, id):
    h1 = ['Type', '30 Days', 'All-time']
    h2 = ['Type', 'Days Ago', 'Chap', 'Series']
    return [], (h1, h2)
