from aiogram.utils import executor
import logging
import bot
import exceptions
import users_preparse


logging.basicConfig(level=logging.INFO)

executor.start_polling(bot.dp,
                       skip_updates=True,)
