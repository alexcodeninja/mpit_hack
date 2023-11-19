from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F
from tinydb import TinyDB, Query
import logging
import asyncio
import googletrans
import requests
import connect

####    setup local variables, configs and other    ####

# logging settings
logging.basicConfig(level=logging.INFO, filename = "bot_logs.log", filemode="w")

# chatbot variables
bot = Bot(token="6414216172:AAESR33MikSbdNKLltT02w2fMZBtwKkyAYs")
dp = Dispatcher()

# local database variables
users = TinyDB("data/users_ids.json")
questions = TinyDB("data/irregular_questions.json")
feedback = TinyDB("data/feedback.json")
qur = Query()

# googletrans object
translator = googletrans.Translator()

#weather
def kelToCel(fah):
    cel = fah - 273.15
    return round(cel)
def get_weather_data():
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                           params={'id': 463828, 'units': 'metric', 'lang': 'ru', 'APPID': connect.weather_api})
        data = res.json()
        info = ""
        for i in data['list'][0:9]:
            info += " | ".join((i['dt_txt'], '{0:+3.0f}'.format(i['main']['temp']), i['weather'][0]['description']))
            info += "\n"
        return info
    except Exception as e:
        print("Exception (forecast):", e)
        pass

####    end of setup    ####

def msg_trans(message: types.Message, bot_msg: str):
    dest = users.table("users").search(qur.id == message.from_user.id)[-1]["lg"] if users.table("users").search(qur.id == message.from_user.id) != [] else "ru"
    translated = translator.translate(text=bot_msg, src="ru", dest=dest)
    return translated.text


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if users.table("users").search(qur.id == message.from_user.id) == []:

        await message.answer(
            text=f"Добро пожаловать, {message.from_user.first_name} {message.from_user.last_name}! Надеемся этот бот станет вашим лучшим помошником при посщении куршской косы!"
                 f"\n\nWelcome {message.from_user.first_name} {message.from_user.last_name}! We hope this bot will become your best assistant when visiting the kurshskoy kosy!",
        )
        menu = [
            [InlineKeyboardButton(text="Русский", callback_data="ru")],
            [InlineKeyboardButton(text="English", callback_data="en")],
            [InlineKeyboardButton(text="Deutsch", callback_data="nl")],
            [InlineKeyboardButton(text="中国人(chinese)", callback_data="zh-cn")],
            [InlineKeyboardButton(text="Español", callback_data="es")],
        ]
        lang_menu = InlineKeyboardMarkup(inline_keyboard=menu)
        await message.answer("Пожалуйста выберите язык\n\nPlease select the language", reply_markup=lang_menu)

    else:
        await cmd_menu(message)


@dp.message(F.text.in_({"/menu", "Открыть меню", "Menu openen", "Menú abierto", "打开菜单", "Open menu"}))
async def cmd_menu(message: types.Message):
    labels = [
        msg_trans(message, "Вопросы посещения"),
        msg_trans(message, "Погода"),
        msg_trans(message, "Правила пребывания"),
        msg_trans(message, "Обратная связь"),
    ]\

    kb = [
        [types.KeyboardButton(text=f"❔ {labels[0]}")],
        [types.KeyboardButton(text=f"⛅️ {labels[1]}")],
        [types.KeyboardButton(text=f"📜 {labels[2]}")],
        [types.KeyboardButton(text=f"📝 {labels[3]}")],
    ]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         keyboard=kb,
                                         one_time_keyboard=False,
                                         input_field_placeholder="Выберите пункт из меню")

    await message.answer(text=msg_trans(message=message, bot_msg="Рады видеть вас в нашем боте.\nВы можете воспользоваться меню"), reply_markup=keyboard)


@dp.callback_query(F.data.in_({"ru", "en", "nl", "zh-cn", "es"}))
async def langsel(message):
    users.table("users").insert({
        "id": message.from_user.id,
        "lg": message.data
    })
    kb = [[
        KeyboardButton(text=msg_trans(message, "Открыть меню"))
    ]]
    await bot.send_message(chat_id=message.from_user.id, text=msg_trans(message, bot_msg="Настройка языка завершена, тепепь вы можете в полной степени пользоваться телеботом :)"), reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True))
# Вопросы и ответы Q&A

@dp.message(F.text.startswith("❔"))
async def qanda(message: types.Message):
    builder = InlineKeyboardBuilder()
    quest_txt = msg_trans(message=message, bot_msg="Вопрос ")
    for i in range(1, 8):
        builder.button(text=f"{quest_txt} №{i}", callback_data=f"{i}")
    builder.adjust(2)
    await message.answer(msg_trans(message, bot_msg="""1.В какие дни и в какое время национальный парк «Куршская коса» открыт для посещения?
2.Как попасть на Куршскую косу? Мы приехали на КПП/в Зеленоградск – куда идти дальше?
3.Где на Куршской косе можно разместиться с палаткой?
4.Как попасть на экскурсию на Куршскую косу?
5.Нужно ли каждый раз покупать входной билет при въезде на территорию национального парка?
6.Если приехать вечером и разместиться на Куршской косе на ночлег, нужно ли на следующий день снова покупать входной билет в парк?
7.Как покупать входные билеты посетителям, въезжающим на рейсовых автобусах, и в каких случаях им можно не покупать билеты?
Другой вопрос можно задать при помощи /question (текст вопроса)
Например: /question как лучше всего провести время на куршской косе?
"""), reply_markup=builder.as_markup())
# Отправка feedback-а

@dp.message(F.text.startswith("📝"))
async def feedback(message: types.Message):
    await message.answer(msg_trans(message, "Вы можете оставить обратную связь, например для того чтобы поделиться впечатлениями от телеграм бота :)"))
    await message.answer(text=msg_trans(message, "для того чтобы оставить обратную связь напишите: ")+" /feedback "+msg_trans(message, bot_msg=" текст обратной связи\n\nпример:\n/")+"feedback "+msg_trans(message, bot_msg="мне тут очень понравилось и бот у вас классныый!"))
#Отправка feedback-a продолжение

@dp.message(Command("feedback"))
async def send_feedback(message: types.Message, command: CommandObject):
    print("something")
    # if len(command.args) < 10:
    #     await message.answer(msg_trans(message, "Текст обратной связи слишком короткий, пожалуйста напишите длиннее."))
    # else:
    #     port = 465  # For SSL
    #     smtp_server = "smtp.gmail.com"
    #     sender_email = "aalexdeada@gmail.com"  # Enter your address
    #     receiver_email = "aaa.deadcode@gmail.com"  # Enter receiver address
    #     password = "7263194728301853"
    #
    #     msg = EmailMessage()
    #     msg.set_content(command.args)
    #     msg['Subject'] = "Hello Underworld from Python Gmail!"
    #     msg['From'] = sender_email
    #     msg['To'] = receiver_email
    #
    #     context = ssl.create_default_context()
    #     with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    #         server.login(sender_email, password)
    #         server.send_message(msg, from_addr=sender_email, to_addrs=receiver_email)
    await message.answer(text=msg_trans(message, "Обратная связь отправлена"))

@dp.message(F.text.startswith("📜"))
async def show_rules(message: types.Message):
    f_btn = InlineKeyboardButton(text=msg_trans(message, "Посмотреть полную версию"), url="https://park-kosa.ru/pravila-poseshheniya-parka")
    mrkp = InlineKeyboardMarkup(inline_keyboard=[[f_btn]])
    await message.answer(text=msg_trans(message=message, bot_msg="""Уважаемые посетители национального парка просим соблюдать ниже указанные правила:
1. Следуйте указаниям на табличках и не отклоняйтесь от маршрута.
2. Не оставляйте мусор на территории заповедника.
3. Не кормите животных и не приближайтесь к ним на расстояние меньше 10 метров.
4. Не собирайте растения и не ломайте ветки.
5. Не разводите костры без разрешения администрации заповедника.
6. Соблюдайте тишину и не шумите, чтобы не нарушать спокойствие животных и природы.
7. Не купайтесь в запрещенных местах и не загрязняйте воду.
8. Соблюдайте правила безопасности и не подвергайте себя опасности.
9. Следите за детьми и не допускайте их беспорядочного поведения.
10. Помните, что заповедник - это уникальный уголок природы, который нужно беречь и сохранять для будущих поколений."""),reply_markup=mrkp)

@dp.callback_query(F.data.in_({f"{i}" for i in range(1,8)}))
async def regular_QandA(message):
    with open("answrs.txt", "r", encoding="UTF-8") as f:
        all_answrs = f.read().split("#")
        print(len(all_answrs))
        await bot.send_message(chat_id=message.from_user.id, text=msg_trans(message=message,bot_msg=all_answrs[int(message.data)-1]))

@dp.message(F.text.startswith("⛅️"))
async def show_weather(message):
    data = get_weather_data()
    print(data, type(data))

    await message.answer(text=msg_trans(message,"погода на Куршской косе на следующие 24 часа:"))
    await message.answer(text=msg_trans(message, bot_msg=data))
    # message.answer(text=msg_trans(message=message, bot_msg=data))


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # sched.create_backup()
    asyncio.run(main())