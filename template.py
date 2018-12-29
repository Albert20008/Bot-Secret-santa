"""
Это шаблон кода телеграм бота.
Вы можете использовать его как основу для своих ботов.
"""

#
# Подключение библиотек
#
import os
import random
import pickle
from collections import namedtuple
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler

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

Group = namedtuple("Group", (
    "creator",
    "members",
    "pairs"
))
#
# Глобальные переменные
#

santas = {}

wishes = {}

#
# Вспомогательные функции
#

def _send_text(bot, user, text):
    bot.send_message(chat_id=user.chat_id, text=text)

def _send_md(bot, user, text):
    bot.send_message(chat_id=user.chat_id, text=text, parse_mode=ParseMode.MARKDOWN)

def _resend_message(bot, user, message):
    if message.text:
        bot.send_message(chat_id=user.chat_id, text=message.text)
    
    if message.sticker:
        bot.send_sticker(chat_id=user.chat_id, sticker=message.sticker)
    
    if message.photo:
        bot.send_photo(chat_id=user.chat_id, photo=message.photo[0], caption=message.caption)
    
    if message.audio:
        bot.send_audio(chat_id=user.chat_id, audio=message.audio)
    
    if message.voice:
        bot.send_voice(chat_id=user.chat_id, voice=message.voice)

def _get_user(update):
    return User(
        update.message.from_user.id,
        update.message.from_user.username,
        update.message.from_user.full_name,
        update.message.chat_id
    )

def _generate_santa_pairs(bot, group_name):
    group = santas[group_name]

    members = group.members.copy()
    random.shuffle(members)

    group.pairs.clear()

    for i, member in enumerate(members):
        pair = members[(i+1) % len(members)]
        group.pairs[member.id] = pair
    
    for member in group.members:
        pair = group.pairs[member.id]
        _send_md(bot, member, "Привет! Настало время поздравлений в группе `{0}` Тайного Санты! Вам выпало поздравлять пользователя @{1} ({2}). Отправьте мне сообщение `/wish {0}` и следуйте дальнейшим инструкциям, чтобы поздравить этого человека".format(group_name, pair.username, pair.real_name))

def _save():
    with open("santas.pickle", "wb") as f:
        pickle.dump(santas, f)
    with open("wishes.pickle", "wb") as f:
        pickle.dump(wishes, f)

def _restore():
    global santas
    global wishes

    if os.path.exists("santas.pickle"):
        with open("santas.pickle", "rb") as f:
            santas = pickle.load(f)
    if os.path.exists("wishes.pickle"):
        with open("wishes.pickle", "rb") as f:
            wishes = pickle.load(f)
#
# Команды
#

def hello_command(bot, update):
    me = _get_user(update)

    _send_text(bot, me, "Привет, мир!")
    _save()

def hello_name_command(bot, update, args):
    me = _get_user(update)

    _send_text(bot, me, "Привет, {}!".format(args[0]))

    _save()

def create_santa(bot, update, args):
    me = _get_user(update)

    if not args:
        _send_md(bot, me, "Чтобы создать группу Тайного Санты, наберите `/create имя_группы`, где `имя_группы` это любая строка, которая будет идентифицировать вашу группу")
        return
    
    group_name = ' '.join(args)

    if group_name in santas:
        _send_text(bot, me, "К сожалению, это имя группы уже занято, попробуйте выбрать другое")
        return

    santas[group_name] = Group(me, [me, me], {})
    _send_text(bot, me, "Поздравляю, ваша группа Тайного Санты создана! Отправьте всем участникам группы следующее сообщение, которое поможет им вступить в вашу группу")
    _send_md(bot, me, "Привет! {} создал(а) группу Тайного Санты и хочет, чтобы вы приняли в ней участие. Для этого добавьте меня ({}) и отправьте мне сообщение `/join {}`".format(me.real_name, BOT_ID, group_name))

    _save()

#
# Главная функция
#

def main():
    _restore()
    updater = Updater(BOT_TOKEN)

    updater.dispatcher.add_handler(CommandHandler("hello_world", hello_command))
    updater.dispatcher.add_handler(CommandHandler("hello", hello_name_command, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler("create", create_santa, pass_args=True))

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
