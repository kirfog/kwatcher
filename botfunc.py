import requests
import feedparser
import re
from bs4 import BeautifulSoup

import subprocess
from vosk import Model, KaldiRecognizer
import json
import argostranslate.translate


def buks():
    r = requests.get(url="https://www.push52.ru/")
    soup = BeautifulSoup(r.content, features="html.parser")
    d = soup.find(id="body_CurrencyBoard1_usdrub")
    sell = d.find("span", {"class": "sell"}).get_text()
    buy = d.find("span", {"class": "buy"}).get_text()
    b = f"продать = {buy}\nкупить = {sell}"
    return b


def sunrise():
    sessionSun = requests.session()
    sun = sessionSun.get(
        "https://api.sunrise-sunset.org/json?lat=59.9342802&lng=30.3350986"
    ).json()
    sun = f"Sun rises at {sun['results']['sunrise']} and sets at {sun['results']['sunset']} UTC"
    return sun


def get_rss(link):
    rss = feedparser.parse(link)
    r = ""
    for i in rss["entries"]:
        r = r + "\n" + i["title"] + " " + i["link"] + " " + i["description"] + "\n"
    return r


def rbc():
    return get_rss("http://static.feed.rbc.ru/rbc/internal/rss.rbc.ru/rbc.ru/news.rss")


def solar(text):
    sol = None
    session = requests.session()
    page = session.get(
        "https://en.wikipedia.org/wiki/List_of_Solar_System_objects_by_size"
    )
    soup = BeautifulSoup(page.content, features="html.parser")
    wiki = "https://upload.wikimedia.org/wikipedia/commons/"

    pattern1 = r"\[.*?\]"
    pattern2 = r"\(.*?\)"
    pattern3 = r"(\/[^\/]+$)"

    r = []
    table = soup.find_all("table")[0]
    for row in table.find_all("tr")[2:]:
        image = None
        name = None
        name = None
        mass = None
        radius = None
        td = row.find_all("td")
        img = row.find("img")
        if img:
            image = img["src"].strip()
            image = re.sub(pattern3, "", image)
            image = wiki + image[47:]
        if td:
            name = td[0].find("a")["title"]
            name = re.sub(pattern2, "", name).strip()
            radius = re.sub(pattern1, "", td[2].text).strip()
            mass = re.sub(pattern1, "", td[5].text).strip()
            if "star" in td[10].text.strip().split(";")[0].lower():
                type = "star"
            elif "planet" in td[10].text.strip().split(";")[0].lower():
                type = "planet"
            else:
                type = "moon"

        r.append(
            {"Name": name, "Image": image, "Mass": mass, "Radius": radius, "Type": type}
        )

    table2 = soup.find_all("table")[1]
    for row in table2.find_all("tr")[1:]:
        image = None
        name = None
        name = None
        mass = None
        radius = None
        td = row.find_all("td")
        img = row.find("img")
        if img:
            image = img["src"].strip()
            image = re.sub(pattern3, "", image)
            image = wiki + image[47:]
        if td:
            name = td[0].find("a")["title"]
            name = re.sub(pattern2, "", name).strip()
            radius = re.sub(pattern1, "", td[2].text).strip()
            mass = re.sub(pattern1, "", td[3].text).strip()
            if "star" in td[6].text.strip().split(";")[0].lower():
                type = "moon"
            elif "planet" in td[6].text.strip().split(";")[0].lower():
                type = "planet"
            else:
                type = "asteroid"
        r.append(
            {"Name": name, "Image": image, "Mass": mass, "Radius": radius, "Type": type}
        )

    for line in r:
        if text.lower() in str(line["Name"]).lower():
            sol = line
            m = (
                sol["Name"]
                + "\n"
                + "Radius: "
                + sol["Radius"]
                + "\n"
                + "Mass: "
                + sol["Mass"]
                + "\n"
                + sol["Image"]
                + "\n"
            )
            return m
        else:
            m = "do not know that object"
    return m


SAMPLE_RATE = 16000
# model = Model(lang="ru")  #  ~/.cache/vosk/
model = Model("vosk-model-small")
rec = KaldiRecognizer(model, SAMPLE_RATE)


def vosko():
    answer = {"ru": "", "en": ""}
    with subprocess.Popen(
        [
            "ffmpeg",
            "-loglevel",
            "quiet",
            "-i",
            "temp.ogg",
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "1",
            "-f",
            "s16le",
            "-",
        ],
        stdout=subprocess.PIPE,
    ) as process:
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                rec.Result()
            else:
                rec.PartialResult()
        r = rec.FinalResult()
    text = json.loads(r)["text"]
    answer["ru"] = text.capitalize()
    print(text)
    text = argostranslate.translate.translate(text, "ru", "en")
    answer["en"] = text.capitalize()
    print(text)
    return answer["ru"] + "\n" + answer["en"]
