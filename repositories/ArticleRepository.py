from models.article import Article
from repositories.Repositories import BaseRepository


class ArticleRepository(BaseRepository):
    _LIST_COLUMNS = "id, url, category_id, source_id, title, status, created_at, updated_at"

    def __init__(self, db_connection):
        super().__init__(db_connection)
    @staticmethod
    def _to_entity(row):
        return Article(
            id=row['id'],
            url=row['url'],
            category_id=row['category_id'],
            source_id=row['source_id'],
            title=row['title'],
            body=row.get('body') or "",
            status=row['status'],
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
            deleted_at=row.get('deleted_at'),
        )

    def save(self, entity: Article):
        query = """
            INSERT INTO articles (
                url, category_id, source_id, title, body, status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        params = (
            entity.url, entity.category_id, entity.source_id,
            entity.title or "", entity.body or "", entity.status,
        )
        result = self._execute(query, params)
        if result is None:
            return None
        entity.id = result[1]
        return entity.id

    def update(self, entity: Article):
        query = """
            UPDATE articles
            SET url = %s, category_id = %s, source_id = %s, title = %s,
                body = %s, status = %s, updated_at = NOW()
            WHERE id = %s AND deleted_at IS NULL
        """
        params = (
            entity.url, entity.category_id, entity.source_id,
            entity.title or "", entity.body or "", entity.status, entity.id,
        )
        result = self._execute(query, params)
        return result is not None and result[0] > 0

    def find_all(self):
        rows = self._query(
            f"SELECT {self._LIST_COLUMNS} FROM articles "
            "WHERE deleted_at IS NULL ORDER BY created_at DESC, id DESC"
        )
        return [self._to_entity(r) for r in rows]

    def find_by_id(self, entity_id):
        row = self._query_one(
            "SELECT * FROM articles WHERE id = %s AND deleted_at IS NULL", (entity_id,)
        )
        return self._to_entity(row) if row else None

    def find_by_status(self, status: str, source_id=None):
        query = "SELECT * FROM articles WHERE status = %s AND deleted_at IS NULL"
        params = [status]
        if source_id is not None:
            query += " AND source_id = %s"
            params.append(source_id)
        query += " ORDER BY id"
        return [self._to_entity(r) for r in self._query(query, tuple(params))]

    def exists_by_url(self, url: str) -> bool:
        row = self._query_one("SELECT 1 AS found FROM articles WHERE url = %s LIMIT 1", (url,))
        return row is not None
    
    @staticmethod
    def _build_filter(keyword=None, source_id=None, crawled_date=None):
        conditions, params = ["deleted_at IS NULL"], []
        if keyword:
            like = f"%{keyword}%"
            conditions.append("(title LIKE %s OR body LIKE %s)")
            params.extend([like, like])
        if source_id is not None:
            conditions.append("source_id = %s")
            params.append(source_id)
        if crawled_date:
            conditions.append("DATE(created_at) = %s")
            params.append(crawled_date)
        return " WHERE " + " AND ".join(conditions), params

    def count(self, keyword=None, source_id=None, crawled_date=None) -> int:
        where, params = self._build_filter(keyword, source_id, crawled_date)
        row = self._query_one(f"SELECT COUNT(*) AS total FROM articles{where}", tuple(params))
        return row['total'] if row else 0

    def find_page(self, page=1, page_size=10, keyword=None, source_id=None, crawled_date=None):
        page = max(1, page)
        offset = (page - 1) * page_size
        where, params = self._build_filter(keyword, source_id, crawled_date)
        query = (
            f"SELECT {self._LIST_COLUMNS} FROM articles{where} "
            "ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s"
        )
        rows = self._query(query, tuple(params) + (page_size, offset))
        return [self._to_entity(r) for r in rows]

    def delete_by_id(self, entity_id):
        query = """
            UPDATE articles
            SET status = 'Deleted', deleted_at = NOW(), updated_at = NOW()
            WHERE id = %s AND deleted_at IS NULL
        """
        result = self._execute(query, (entity_id,))
        return result is not None and result[0] > 0

    def delete_older_than(self, days: int) -> int:
        query = """
            UPDATE articles
            SET status = 'Deleted', deleted_at = NOW(), updated_at = NOW()
            WHERE deleted_at IS NULL
              AND created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        result = self._execute(query, (days,))
        return result[0] if result else 0