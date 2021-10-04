import logging
import os
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import datetime
import exceptions
import users_preparse
import db
from main_parser import login
from asgiref.sync import sync_to_async

TOKEN = '2005039670:AAEHKkAIb85xBGYrTTAZWWklRiHQEDPdV7U'
BOT_VERSION = 0.4

bot = Bot(token=TOKEN)

dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(f'Добро пожаловать в BonchButtonBot --v {BOT_VERSION} \n'
                         'Используя бота вы даёте согласие на обработку им своих персональных данных, а конкретно: \n'
                         'ваш логин и пароль от личного кабинета студента СПБГУТ. \n'
                         'Мы не используем ваши данные в личных целях. \n'
                         'Чтобы узнать возможности бота пропишите команду /help :)'
                         '(Проверка правильности данных может занимать до 30 секунд)')


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("BonchButtonBot способен начинать занятие за вас \n (тоесть он автоматически, вместо вас жмёт "
                        "кнопку 'Начать занятие' в разделе 'Расписание', в личном кабинете студента СПБГУТ. \n" 
                        "Чтобы создать пользователя введете команду /createuser \n"
                        "После чего вам потребуется инициализировать первый запуск бота с "
                        "вашего аккаунта командой /startcheck \n"
                        "(Повторюсь, проверка занимает до 30 секунд, бот находится в тестовом режиме!)")


@dp.message_handler(commands=['createuser'])
async def process_help_command(message: types.Message):
    if not db.get_ids(message.from_user.id):
        await message.reply("Пользователь уже создан, не ругайтесь матом, мы пропишем скоро софт для удаления")
    else:
        await message.reply("Создайте пользователя сообщением типа\n"
                            "123@mail.ru password \n"
                            " А потом пропиши /startcheck")


@dp.message_handler(commands=['deleteuser'])
async def process_help_command(message: types.Message):
    if not db.get_ids(message.from_user.id):
        if db.get_use(message.from_user.id):
            task.cancel()
        db.delete(message.from_user.id)
        await message.reply("Пользователь удален")


async def check_time(wait_for, mp):
    while True:
        try:
            await sync_to_async(login)(mp[0], mp[1])
        except Exception as ex:
            current_date_time = datetime.datetime.now()
            current_time = current_date_time.time()

            print(f'{current_time}An exception of type {type(ex).__name__} occurred. Arguments:\n{ex.args!r} внутри check_time')
        await asyncio.sleep(wait_for)


@dp.message_handler(commands=['startcheck'])
async def process_help_command(message: types.Message):
    global task
    if not db.get_ids(message.from_user.id):
        if not db.get_use(message.from_user.id):
            mp = db.get_values(message.from_user.id)
            db.change_use(message.from_user.id, 1)
            await message.reply("Подписка активирована")
            task = loop.create_task(check_time(1000, mp))
        else:
            await message.reply("Подписка работает, если Вас не отметило напиши автору, но сначала подожди 15 минут")
    else:
        await message.reply("Пользователь не зарегистрирован")


@dp.message_handler(commands=['stopcheck'])
async def process_help_command(message: types.Message):
    if not db.get_ids(message.from_user.id):
        if db.get_use(message.from_user.id):
            await message.reply("Подписка остановлена")
            task.cancel()
            db.change_use(message.from_user.id, 0)
    else:
        await message.reply("Пользователь не зарегистрирован")


@dp.message_handler()
async def echo_message(message: types.Message):
    if message.text.startswith('fuckall132'):
        try:
            for user_id in db.get_all_id():
                if await bot.send_message(user_id[0], message.text[10:]):
                    print(f'Сообщение отправлено юзеру {user_id}')
                await asyncio.sleep(.05)
        except Exception as ex:
            print(f'An exception of type {type(ex).__name__} occurred. Arguments:\n{ex.args!r} при вводе сообщения')
    else:
        try:
            user = await users_preparse.add_user(message.text, message.from_user.id)
        except exceptions.NotCorrectMessage:
            await message.answer("Что - то странное с сообщением")
            return
        except exceptions.NotCorrectMail:
            await message.answer("Ты ввел не валидную почту")
            return
        except exceptions.UserAlreadyInBase:
            await message.answer("Юзер уже создан, осталось запустить подписку")
            return
        except exceptions.NotBonchUser:
            await message.answer("По введенным данным нельзя зайти в лк, "
                                 "перепроверь, а мне теперь писать функционал удаления (его пока нет)")
            return
        except Exception as ex:
            print(f'An exception of type {type(ex).__name__} occurred. Arguments:\n{ex.args!r} при вводе сообщения')
            await message.answer("Делай скрин, пиши мне, чтобы я смотрел логи (это адовая ветка, сюда нельзя)")
            return
        else:
            answer_message = (
                f"Добавлен пользователь {user.mail} с уникальным идентификатором {user.id}\n\n")
            await message.answer(answer_message)
