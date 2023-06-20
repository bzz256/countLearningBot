from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# API_TOKEN = '5863542880:AAGYnnYELe6-1CUb0zLtvR0nhFnYSW2sX90'
API_TOKEN = '5826886671:AAGhbIzAe2YQUHehtffoRoTp3EWQQ_HOzzk'

bot = Bot(token=API_TOKEN)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
