"""
Это шаблон кода телеграм бота.
Вы можете использовать его как основу для своих ботов.
"""

#
# Подключение библиотек
#

from collections import namedtuple
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

#
# Общие константы
#

BOT_ID = "@alberttopbot"
BOT_TOKEN = "665130047:AAGWlmEIO7-G419YqMCA8g9BlH5jnExv75E"
BOT_APPNAME = "secretsanta2008"

#
# Типы данных
#

User = namedtuple("User", (
    "id",
    "username",
    "real_name",
    "chat_id"
))

#
# Глобальные переменные
#

#
# Вспомогательные функции
#

def _send_text(bot, user, text):
    bot.send_message(chat_id=user.chat_id, text=text)

def _send_md(bot, user, text):
    bot.send_message(chat_id=user.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)

def _get_user(update):
    return User(
        update.message.from_user.id,
        update.message.from_user.username,
        update.message.from_user.full_name,
        update.message.chat_id
    )

#
# Команды
#

def hello_command(bot, update):
    me = _get_user(update)

    _send_text(bot, me, "Привет, мир!")

def hello_name_command(bot, update, args):
    me = _get_user(update)

    _send_text(bot, me, "Привет, {}!".format(args[0]))

#
# Главная функция
#

def main():
    _restore()
    updater = Updater(BOT_TOKEN)

    updater.dispatcher.add_handler(CommandHandler("hello_world", hello_command))
    updater.dispatcher.add_handler(CommandHandler("hello", hello_name_command, pass_args=True))

    updater.start_polling()
    print("Bot started polling")

    updater.idle()

    if "PORT" in os.environ:
        updater.start_webhook(listen="0.0.0.0", port=int(os.environ["PORT"]), url_path=BOT_TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(BOT_APPNAME, BOT_TOKEN))
        print("Bot started on webhook")
    else:
        updater.start_polling()
        print("Bot started polling")

    updater.idle()

if __name__ == "__main__":
    main()
