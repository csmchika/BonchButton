import os
from typing import Dict, List, Tuple

import sqlite3


conn = sqlite3.connect(os.path.join("db", "users.db"))
cursor = conn.cursor()


def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def delete(row_id: int) -> None:
    cursor.execute(f"DELETE FROM users WHERE id = ?", (row_id,))
    conn.commit()


def get_cursor():
    return cursor


def get_all_id():
    cursor.execute("SELECT id FROM users")
    ids = cursor.fetchall()
    print(ids)
    return ids


def get_ids(user_id: int):
    cursor.execute("SELECT id FROM users")
    ids = cursor.fetchall()
    for i in ids:
        if user_id == i[0]:
            return False
    return True


def get_use(user_id: int):
    cursor.execute("SELECT use FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    if result[0] == 1:
        return True
    return False


def get_values(user_id: int):
    cursor.execute("SELECT mail, password FROM users WHERE id = ?", (user_id, ))
    result = cursor.fetchone()
    if result:
        return result


def change_use(user_id: int, i: int):
    if i == 1:
        cursor.execute("UPDATE users SET use = ? WHERE id = ?", (1, user_id,))
        conn.commit()
    else:
        cursor.execute("UPDATE users SET use = ? WHERE id = ?", (0, user_id,))
        conn.commit()


def _init_db():
    """Инициализирует БД"""
    with open("createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type = ? AND name = ?", ('table', 'users',))
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


check_db_exists()
