import os
import telebot
from reqfunc import get_sunrise, rbc, solar

BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = telebot.TeleBot(BOT_TOKEN)

# bot = telebot.TeleBot(BOT_TOKEN, parse_mode = 'HTML')
# bot = telebot.TeleBot(BOT_TOKEN, parse_mode = 'Markdown')


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "already started")


@bot.message_handler(commands=["help"])
def nohelp(message):
    bot.reply_to(message, "cannot help you")


@bot.edited_message_handler(func=lambda m: m.text == "rbc")
@bot.message_handler(func=lambda m: m.text == "rbc")
def mrbc(message):
    bot.reply_to(message, rbc()[:4000])


@bot.edited_message_handler(func=lambda m: m.text == "time")
@bot.message_handler(func=lambda m: m.text == "time")
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
    else:
        bot.reply_to(message, "do not know that object")


bot.infinity_polling()
