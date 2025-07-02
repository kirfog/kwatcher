#!/usr/bin/env python3
import telebot
from dotenv import load_dotenv
import os

from botfunc import sunrise, solar, rbc, vosko, buks
from botcom import nohelp

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def start_h(message):
    bot.reply_to(message, "already started")


@bot.message_handler(commands=["help"])
def nohelp_h(message):
    bot.reply_to(message, nohelp())


@bot.edited_message_handler(func=lambda m: m.text.lower() == "buks")
@bot.message_handler(func=lambda m: m.text.lower() == "buks")
def buks_h(message):
    rep = buks()
    bot.reply_to(message, rep)


@bot.edited_message_handler(func=lambda m: m.text.lower() == "rbc")
@bot.message_handler(func=lambda m: m.text.lower() == "rbc")
def rbc_h(message):
    bot.reply_to(message, rbc()[:4000])


@bot.edited_message_handler(func=lambda m: m.text.lower() == "sunrise")
@bot.message_handler(func=lambda m: m.text.lower() == "sunrise")
def sunrise_h(message):
    bot.reply_to(message, sunrise())


@bot.edited_message_handler(func=lambda m: True)
@bot.message_handler(func=lambda m: True)
def solar_h(message):
    bot.reply_to(message, solar(message.text))


def downloadfile(file_info):
    downloaded_file = bot.download_file(file_info.file_path)
    with open("temp.ogg", "wb") as new_file:
        new_file.write(downloaded_file)


@bot.message_handler(content_types=["voice"])
def voice_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    downloadfile(file_info)
    bot.reply_to(message, vosko())


@bot.message_handler(content_types=["video_note"])
def video_note_processing(message):
    file_info = bot.get_file(message.video_note.file_id)
    downloadfile(file_info)
    bot.reply_to(message, vosko())


@bot.message_handler(content_types=["video"])
def video_processing(message):
    file_info = bot.get_file(message.video.file_id)
    downloadfile(file_info)
    bot.reply_to(message, vosko())


@bot.message_handler(content_types=["audio"])
def audio_processing(message):
    file_info = bot.get_file(message.audio.file_id)
    downloadfile(file_info)
    bot.reply_to(message, vosko())


bot.infinity_polling()
