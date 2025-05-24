#!/usr/bin/env python3
import os
import telebot
from reqfunc import get_sunrise, rbc, solar, buks
import subprocess
from vosk import Model, KaldiRecognizer
import json

# import argostranslate.package
import argostranslate.translate
from dotenv import load_dotenv
import ping3
import time as t

# import threading

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# bot = telebot.TeleBot(BOT_TOKEN, parse_mode = 'HTML')
# bot = telebot.TeleBot(BOT_TOKEN, parse_mode = 'Markdown')


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "already started")


rep = "<pre>"
rep += "🤷‍♂️ cannot help you \U0001f534 \n"
rep += "U+260E".ljust(15) + "\U0000260e \n"
rep += "U+1F52D".ljust(15) + "\U000023f0 \n"
rep += "U+1F9EE".ljust(15) + "\U0001f9ee \n"
rep += "U+1F5D1".ljust(15) + "\U0001f5d1 \n"
rep += "</pre>"


@bot.message_handler(commands=["help"])
def nohelp(message):
    bot.reply_to(message, rep)


@bot.edited_message_handler(func=lambda m: m.text.lower() == "buks")
@bot.message_handler(func=lambda m: m.text.lower() == "buks")
def buks_h(message):
    rep = buks()
    bot.reply_to(message, rep)


@bot.edited_message_handler(func=lambda m: m.text.lower() == "rbc")
@bot.message_handler(func=lambda m: m.text.lower() == "rbc")
def mrbc(message):
    bot.reply_to(message, rbc()[:4000])


@bot.edited_message_handler(func=lambda m: m.text.lower() == "time")
@bot.message_handler(func=lambda m: m.text.lower() == "time")
def mtime(message):
    bot.reply_to(message, get_sunrise())


@bot.edited_message_handler(func=lambda m: True)
@bot.message_handler(func=lambda m: True)
def sol(message):
    sol = solar(message.text)
    if sol:

        # text = '*' + sol['Name'] + '*' + '\n' + "Radius: " + sol['Radius'] + ' Mass: ' + sol['Msss']
        # bot.send_photo(message.chat.id, photo=sol['Image'], caption=text, reply_to_message_id=message)

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
        bot.reply_to(message, m)
    # else:
    #     bot.reply_to(message, "do not know that object")


SAMPLE_RATE = 16000
# model = Model(lang="ru")  #  ~/.cache/vosk/
model = Model("vosk-model")
rec = KaldiRecognizer(model, SAMPLE_RATE)


@bot.message_handler(content_types=["voice"])
def voice_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    vosko(message, file_info)


@bot.message_handler(content_types=["video_note"])
def video_note_processing(message):
    file_info = bot.get_file(message.video_note.file_id)
    vosko(message, file_info)


@bot.message_handler(content_types=["video"])
def video_processing(message):
    file_info = bot.get_file(message.video.file_id)
    vosko(message, file_info)


@bot.message_handler(content_types=["audio"])
def audio_processing(message):
    file_info = bot.get_file(message.audio.file_id)
    vosko(message, file_info)


def vosko(message, file_info):
    downloaded_file = bot.download_file(file_info.file_path)
    with open("temp.ogg", "wb") as new_file:
        new_file.write(downloaded_file)
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
    bot.reply_to(message, text.capitalize())
    print(text)
    text = argostranslate.translate.translate(text, "ru", "en")
    bot.reply_to(message, text.capitalize())
    print(text)


homees = {
    "Daddy": ["192.168.88.101", 1],
    "Mammy": ["192.168.88.104", 0],
    "Mary": ["192.168.88.103", 0],
    "Max": ["192.168.88.114", 0],
}

comps = {
    "Daddy": ["192.168.88.128", 1],
    "Mammy": ["192.168.88.137", 0],
    "Mary": ["192.168.88.164", 0],
    "Max": ["192.168.88.121", 0],
    "Max2": ["192.168.88.149", 0],
    "Max3": ["192.168.88.132", 0],
}


def whoishome():
    global homees
    global comps
    while True:
        t.sleep(1)
        for k, v in homees.items():
            p = ping3.ping(v[0])
            if p and v[1] == 0:
                homees[k][1] = 1
                bot.send_message(text=f"{k} is home", chat_id="-4553062703")
            elif not p and v[1] == 1:
                homees[k][1] = 0
                bot.send_message(text=f"{k} left home", chat_id="-4553062703")

        for k, v in comps.items():
            p = ping3.ping(v[0])
            if p and v[1] == 0:
                homees[k][1] = 1
                bot.send_message(
                    text=f"{k} turned on the comp",
                    disable_notification=True,
                    chat_id="-4553062703",
                )
            elif not p and v[1] == 1:
                homees[k][1] = 0
                bot.send_message(
                    text=f"{k} turned off the comp",
                    disable_notification=True,
                    chat_id="-4553062703",
                )


# thread = threading.Thread(target=whoishome)
# thread.start()


bot.infinity_polling()
