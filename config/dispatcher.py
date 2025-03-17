from os import getenv
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv


load_dotenv()


TOKEN = getenv("BOT_TOKEN")


print(TOKEN)

dp = Dispatcher(storage=MemoryStorage())