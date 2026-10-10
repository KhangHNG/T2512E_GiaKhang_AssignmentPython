from abc import ABC, abstractmethod

from mysql.connector import Error, IntegrityError


class BaseRepository(ABC):
    def __init__(self, db_connection):
        self.db = db_connection

    @abstractmethod
    def save(self, entity):
        pass

    @abstractmethod
    def update(self, entity):
        pass

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def find_by_id(self, entity_id):
        pass

    @abstractmethod
    def delete_by_id(self, entity_id):
        pass

    def _query(self, query, params=()):
        conn = self.db.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params)
                return cursor.fetchall()
            finally:
                cursor.close()
        except Error as e:
            print(f"[DB ERROR] Lỗi truy vấn: {e}")
            return []
        finally:
            conn.close()

    def _query_one(self, query, params=()):
        rows = self._query(query, params)
        return rows[0] if rows else None

    def _execute(self, query, params=()):
        conn = self.db.get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount, cursor.lastrowid
            finally:
                cursor.close()
        except IntegrityError as e:
            self._safe_rollback(conn)
            print(f"[DB ERROR] Vi phạm ràng buộc dữ liệu (trùng hoặc đang được tham chiếu): {e}")
            return None
        except Error as e:
            self._safe_rollback(conn)
            print(f"[DB ERROR] Lỗi thực thi: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def _safe_rollback(conn):
        try:
            conn.rollback()
        except Error:
            pass