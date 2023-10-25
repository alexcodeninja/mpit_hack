import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from tinydb import TinyDB, Query
import googletrans
import sched
import threading

# chatbot variables
logging.basicConfig(level=logging.INFO, filename="bot_logs.log", filemode="w", format="%(asctime)s %(levelname)s %(message)s")
bot = Bot(token="6414216172:AAESR33MikSbdNKLltT02w2fMZBtwKkyAYs")
dp = Dispatcher(bot)

# local database variables
users = TinyDB("data/users_ids.json")
questions = TinyDB("data/irregular_questions.json")
qur = Query()

#schedule, needed to upload data at a certain time


@dp.message(Command("start"))
async def start(message: types.Message):
	if users.search(qur.id == message.from_user.id) == []:
		bot.send_message("Добро пожаловать!\nПожалуйста выберите язык.\n\nWelocome!\nPlease choose the language.")
		logging.info("New user started!")


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())