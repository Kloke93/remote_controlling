"""
Author: Tomas Dal Farra
Date: 31/05/2023
Description: Two items database with SQLite implementation for Remote-Controlling
"""
import sqlite3
import string
import uuid
import platform
import hashlib
from random import choice
import threading


CHARS = string.ascii_letters + string.digits


def generate_password(n: int = 8) -> str:
    """
    Generates a password with letters and digits of length n
    :param n: length of the password
    :return: generated password
    """
    return ''.join(choice(CHARS) for _ in range(n))


class DataBase:
    """ Creates a data to store user id and password """
    half_id = 6         # half of a normal id length

    def __init__(self):
        """ creates database with user (id, password) values """
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE user (
                        id text,
                        password text
                        )""")
        self.c.execute("INSERT INTO user VALUES (:id, :password)",
                       {'id': self.generate_id(), 'password': generate_password()})
        self.conn.commit()

    @staticmethod
    def generate_id() -> str:
        """
        Generates unique id based on the computer hardware
        Note: it is currently using mac address to generate the id, so it's not perfect
        :return: string with the unique id
        """
        name_hash = hashlib.md5(platform.node().encode())       # computer name
        mac_hash = hashlib.md5(str(uuid.getnode()).encode())    # mac address
        return mac_hash.hexdigest()[:DataBase.half_id] + name_hash.hexdigest()[:DataBase.half_id]

    def get_id(self):
        """
        Gets the user unique id
        :return: id
        """
        with self.lock:
            self.c.execute("SELECT id FROM user")
        identifier = self.c.fetchone()[0]
        self.conn.commit()
        return identifier

    def update_password(self, password):
        """
        Updates the password value in the database
        :param password: new password to set
        """
        with self.lock:
            self.c.execute("UPDATE user SET password = :password", {'password': password})
        print(f'password updated to {password}')

    def get_password(self):
        """
        Gets the user password
        :return: the password
        """
        with self.lock:
            self.c.execute("SELECT password FROM user")
        password = self.c.fetchone()[0]
        self.conn.commit()
        return password

    def close(self):
        """ Closes the database handler """
        self.conn.close()


def main():
    db = DataBase()
    print(db.get_id())
    db.close()


if __name__ == "__main__":
    # check if in 100 generation all password characters are always numbers or letters
    for i in range(100):
        for char in generate_password():
            assert char.isalpha() or char.isnumeric()
    db_test = DataBase()
    assert isinstance(db_test.get_password(), str)
    db_test.update_password("messi123")
    assert db_test.get_password() == "messi123"
    db_test.close()
    main()
