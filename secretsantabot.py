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

def join_santa(bot, update, args):
    me = _get_user(update)

    if not args:
        _send_md(bot, me, "Укажите группу Тайного Санты, к которой вы хотите присоединиться: `/join имя_группы`")
        return
    
    group_name = ' '.join(args)

    if group_name not in santas:
        _send_text(bot, me, "К сожалению, такой группы не существует. Возможно вы допустили ошибку в наборе имени группы.")
        return

    group = santas[group_name]

    found = False
    for user in group.members:
        if user.id == me.id:
            found = True
            break
    if found:
        _send_text(bot, me, "Вы уже состоите в этой группе")
        return

    group.members.append(me)
    _send_text(bot, me, "Ура, теперь вы состоите в группе Тайного Санты! Вам придет уведомление о том, когда наступит время поздравлений")
    _send_md(bot, group.creator, "В вашу группу \"{}\" добавился участник: @{} ({})".format(group_name, me.username, me.real_name))

    _save()

def start_santa(bot, update, args):
    me = _get_user(update)

    if not args:
        _send_md(bot, me, "Укажите группу, для которой вы хотите запустить кампанию Тайного Санты: `/start имя_группы`")
        return
    
    group_name = ' '.join(args)

    if group_name not in santas:
        _send_text(bot, me, "К сожалению, такой группы не существует. Возможно вы допустили ошибку в наборе имени группы.")
        return
    
    group = santas[group_name]

    if group.creator.id != me.id:
        _send_text(bot, me, "К сожалению, вы не можете запустить кампанию Тайного Санты для этой группы, так как вы не являетесь ее создателем")
        return
    
    if group.pairs:
        _send_text(bot, me, "Эта кампания Тайного Санты уже запущена")
        return
    
    if len(group.members) < 2:
        _send_text(bot, me, "К сожалению, вы не можете устроить Тайного Санту в одиночку. Пригласите кого-нибудь присоединиться к вашей группе")
        return
    
    _send_text(bot, me, "Отлично! Сейчас я сгенерирую поздравительные пары и отправлю всем участникам группы (в том числе и вам) детальные инструкции")
    _generate_santa_pairs(bot, group_name)

    _save()

def start_wish(bot, update, args):
    me = _get_user(update)

    if not args:
        _send_md(bot, me, "Укажите группу, участнику которой вы хотите отправить поздравление: `/wish имя_группы`")
        return
    
    group_name = ' '.join(args)

    if group_name not in santas:
        _send_text(bot, me, "К сожалению, такой группы не существует. Возможно вы допустили ошибку в наборе имени группы.")
        return
    
    group = santas[group_name]

    found = False
    for user in group.members:
        if user.id == me.id:
            found = True
            break
    if not found:
        _send_text(bot, me, "К сожалению, вы не состоите в этой группе Тайного Санты")
        return
    
    if not group.pairs:
        _send_text(bot, me, "Кампания Тайного Санты в этой группе еще не запущена. Возможно еще не все добавились, а возможно организатор (@{}) забыл запустить кампанию".format(group.creator.username))
        return
    
    if me.id not in group.pairs:
        _send_text(bot, me, "Либо вы уже отправляли поздравление в этой группе, либо случилось страшное и вам не нашлось пары. Но скорее всего первое")
        return
    
    pair = group.pairs[me.id]

    wishes[me.id] = {
        "group": group_name,
        "pair": pair
    }

    _send_text(bot, me, "Отлично! Напишите следующим сообщением мне поздравление, которое нужно отправить пользователю @{} ({}). Можно использовать текст, стикер, картинки и аудио. Помните, что я отправлю только одно сообщение получателю и отредактировать его будет нельзя! Сообщение я отправлю анонимно, поэтому пользователь не узнает, что это вы ему отправили (если сами об этом не скажете).".format(pair.username, pair.real_name))

    _save()

def wish_handler(bot, update):
    me = _get_user(update)
    message = update.message

    if message is not None:
        if me.id not in wishes:
            _send_text(bot, me, "Так как вы не указали кому адресовано это пожелание, я отправлю его вам")

            _resend_message(bot, me, message)
        else:
            group_name = wishes[me.id]["group"]
            pair = wishes[me.id]["pair"]

            _send_md(bot, pair, "Кто-то из группы `{}` отправил вам поздравление как ваш Тайный Санта. Я пришлю вам его следующим сообщением!".format(group_name))
            _resend_message(bot, pair, message)

            _send_text(bot, me, "Адресат получил ваше поздравление! Теперь вы - настоящий Тайный Санта!")

            del wishes[me.id]

            if group_name in santas:
                group = santas[group_name]
                try:
                    del group.pairs[me.id]
                except:
                    pass
                
                if not group.pairs:
                    _send_md(bot, group.creator, "В группе `{}` все друг друга поздравили, кампания Тайного Санты окончена!".format(group_name))
                    del santas[group_name]
                
            _save()

#
# Главная функция
#

def main():
    _restore()

    updater = Updater(BOT_TOKEN)

    updater.dispatcher.add_handler(CommandHandler("create", create_santa, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler("join", join_santa, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler("start", start_santa, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler("wish", start_wish, pass_args=True))
    updater.dispatcher.add_handler(MessageHandler(None, wish_handler))

    # если бот запущен на сервисе Heroku, то надо работать в режиме веб хука.
    #
    # чтобы разместить свое приложение на Heroku:
    # 1. Зарегистрируйтесь на heroku.com
    # 2. Установите инструменты Heroku для вашей платформы: https://devcenter.heroku.com/articles/heroku-cli
    # 3. Установите git (если пользуетесь Windows, то https://git-scm.com/downloads)
    # 4. Откройте командную строку в папке с вашим проектом (например, при помощи VSCode)
    # 5. Инициализируйте репозиторий git в этой папке командой git init
    # 6. Авторизуйтесь инструментами Heroku на вашем компьютере: heroku login
    #     При этом откроется браузер и вы должны там выполнить вход в сервис с учетной записью, созданной в пункте 1
    # 7. Создайте приложение Heroku: heroku create имя_приложения
    # 8. Впишите имя приложения из предыдущего шага в константу BOT_APPNAME в этом файле (строка 18)
    # 9. Зафиксируйте ваше приложение в локальном git репозитории, созданном в шаге 5:
    #      git add .
    #      git commit -m "Initial commit"
    # 10. Отправьте изменения в Heroku: git push heroku master
    # 11. Готово
    #
    # Так как в бесплатную учетную запись Heroku входит недостаточно "дайно-часов" для
    #  непрерывной работы сервиса, а из-за специфики телеграма ваше приложение не будет засыпать,
    #  то рекомендую выключать вашего бота, когда он не используется, вручную:
    #    heroku ps:scale web=0
    # После этого, если захотите снова запустить бота, выполните команду
    #    heroku ps:scale web=1
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
