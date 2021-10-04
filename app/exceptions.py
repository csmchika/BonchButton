class NotCorrectMessage(Exception):
    """Некорректное сообщение в бот, которое не удалось распарсить"""
    pass


class UserAlreadyInBase(Exception):
    """user уже есть"""
    pass


class NotCorrectMail(Exception):
    """Некорректная почта, которое не удалось распарсить"""
    pass


class NotBonchUser(Exception):
    """Ошибка при входе в лк"""
    pass
