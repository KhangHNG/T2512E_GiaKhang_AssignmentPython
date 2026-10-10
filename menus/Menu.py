from database.DatabaseConnection import DatabaseConnection


class Menu:
    def __init__(self, db_conn=None):
        self.db_conn = db_conn or DatabaseConnection(
            host="localhost", user="root", password="", database="news_crawler"
        )

    def print_menu(self):
        pass

    @staticmethod
    def read_int(prompt, min_value=None, max_value=None):
        while True:
            raw = input(prompt).strip()
            try:
                value = int(raw)
            except ValueError:
                print("Vui lòng nhập một số nguyên.")
                continue
            if min_value is not None and value < min_value:
                print(f"Giá trị phải >= {min_value}.")
                continue
            if max_value is not None and value > max_value:
                print(f"Giá trị phải <= {max_value}.")
                continue
            return value

    @staticmethod
    def read_text(prompt, required=False, default=None):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            if default is not None:
                return default
            if not required:
                return ""
            print("Không được để trống.")