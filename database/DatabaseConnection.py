import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    def __init__(self, host = "localhost", user = "root", password = "", database= "news_crawler"):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }

    def get_connection(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            print(f"Lỗi kết nối database: {e}")
            return None