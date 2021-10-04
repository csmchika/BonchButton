import re
from typing import NamedTuple, Optional
import exceptions
import db
from main_parser import login
from asgiref.sync import sync_to_async

LK_ROOT_URL = "https://lk.sut.ru/cabinet/"
LK_PARSE_URL = "https://lk.sut.ru/cabinet/?login=yes"


class Message(NamedTuple):
    """Структура распаршенного сообщения о новом расходе"""
    mail: str
    password: str


class User(NamedTuple):
    """Структура добавленного в БД нового расхода"""
    id: Optional[int]
    mail: str
    password: str


async def add_user(raw_message: str, user_id: int) -> User:
    """Добавляет новое сообщение.
    Принимает на вход текст сообщения, пришедшего в бот."""
    try:
        parsed_message = await _parse_message(raw_message)
    except exceptions.NotCorrectMessage:
        raise exceptions.NotCorrectMessage
    except exceptions.NotCorrectMail:
        raise exceptions.NotCorrectMail
    except exceptions.NotBonchUser:
        raise exceptions.NotBonchUser
    else:
        if db.get_ids(user_id):
            db.insert("users", {
                "id": user_id,
                "mail": parsed_message.mail,
                "password": parsed_message.password,
                "use": 0,
            })
            return User(id=user_id, mail=parsed_message.mail, password=parsed_message.password)
        else:
            raise exceptions.UserAlreadyInBase


async def _parse_message(raw_message: str) -> Message:
    """Парсит текст пришедшего сообщения о новом расходе."""
    try:
        msg = raw_message.split()
        mail = msg[0]
        password = msg[1]
        if not await validatemail(mail):
            raise exceptions.NotCorrectMail
        try:
            await sync_to_async(login)(mail, password)
        except exceptions.NotBonchUser:
            raise exceptions.NotBonchUser
        except Exception as ex:
            print(f'An exception of type {type(ex).__name__} occurred. Arguments:\n{ex.args!r} при входе на парсинге')
        else:
            return Message(mail=mail, password=password)
    except exceptions.NotBonchUser:
        raise exceptions.NotBonchUser
    except exceptions.NotCorrectMail:
        raise exceptions.NotCorrectMail
    except Exception as ex:
        print(f'An exception of type {type(ex).__name__} occurred. Arguments:\n{ex.args!r} при парсинге сообщения')
        raise exceptions.NotCorrectMessage


async def validatemail(email):
    res = r'[^@]+@[^@]+\.[^@]+'
    return re.match(res, email)
