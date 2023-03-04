from . import config, storage
from bs4 import BeautifulSoup as bs
import aiohttp
import hashlib
import re


async def checkUpdates(handler):
    updates = await _getUpdates()
    series = storage.getSeries()
    for update in updates:
        sId = update["sId"]
        chId = update["chId"]
        if sId in series:
            if series[sId] == chId:
                continue

        # Description takes more time so we only grab it if needed
        update["description"] = await _getDescription(update["sLink"])

        storage.upsertSerie(sId, chId)
        await handler(update)


async def _getUpdates():

    link = config.config["updateLink"]
    html = await _fetchHtml(link)
    soup = bs(html, "html.parser")
    divs = soup.find_all("div", class_="col-6 col-sm-6 col-md-6 col-xl-3")

    updateList = []
    for div in divs:
        parsed = _parseDiv(div)
        updateList.append(parsed)

    return list(reversed(updateList))


def _parseDiv(dv):
    ret = {
        "chLink": "N/A",
        "chNum": "-1",
        "chId": "-1",

        "sLink": "N/A",
        "sName": "N/A",
        "sId": "-1",
        "cover": "N/A",
        "description": ""
    }

    linkAGroup = dv.find("a", class_="series-link")
    ret["sLink"] = linkAGroup["href"].strip()
    ret["sName"] = linkAGroup["title"].strip()
    img = linkAGroup.find("img")
    ret["cover"] = img["data-src"]
    ret["sId"] = str(_hash_string(ret["sName"]))

    chapters = dv.find("div", class_="series-content").find_all("a")
    chapter = chapters[0]
    chapterStr = chapter.find("span", "series-badge").text.strip()
    ret["chNum"] = chapterStr.split(" ")[1]
    ret["chId"] = str(_hash_string(chapterStr))
    ret["chLink"] = chapter["href"]
    return ret


def getUpdateEmbed(update):
    template = {
        "title": "",
        "url": "",
        "description": "",
        "color": 0x0000ff,
        "image": {
            "url": ""
        },
        "fields": [
            {"name": "Links",
             "value": "",
             "inline": True, },
        ]
    }
    template['title'] = f":mega: | {update['sName']} - Capítulo {update['chNum']}"
    template['url'] = update['chLink']
    desc = update["description"]
    template[
        'description'] = f"💥 Aqui una nueva actualización 💥 ¡Revisenla en nuestra página oficial! \n \n {desc}"
    template['image']['url'] = update['cover']
    template['fields'][0]['value'] = f"[[Capítulo]]({update['chLink']}) • [[Serie]]({update['sLink']})"
    return template


async def _getDescription(link):
    html = await _fetchHtml(link)
    soup = bs(html, "html.parser")

    div = soup.find("div", class_="summary__content")
    if not div:
        return ""

    p = div.find("p")
    if not p:
        return ""

    return p.text.strip()


def _hash_string(string) -> int:
    # Crea un objeto SHA-256
    sha256 = hashlib.sha256()

    # Actualiza el objeto SHA-256 con la cadena de texto
    sha256.update(string.encode('utf-8'))

    # Obtiene el hash en formato hexadecimal
    hex_dig = sha256.hexdigest()

    # Convierte el hash hexadecimal a un entero sin signo (unsigned int)
    num = int(hex_dig, 16)

    return num


async def _fetchHtml(link):
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
            content_type = response.headers.get('Content-Type', '')
            charset_match = re.search(r'charset=(\S+)', content_type)
            if charset_match:
                charset = charset_match.group(1)
                html_bytes = await response.read()
                html_string = html_bytes.decode(charset)
                return html_string
            else:
                html_bytes = await response.read()
                return html_bytes.decode(errors='replace')
