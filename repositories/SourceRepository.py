from models.source import Source
from repositories.Repositories import BaseRepository


class SourceRepository(BaseRepository):
    def __init__(self, db_connection):
        super().__init__(db_connection)

    @staticmethod
    def _to_entity(row):
        return Source(
            id=row['id'],
            name=row['name'],
            domain=row['domain'],
            path=row['path'],
            category_id=row['category_id'],
            description=row['description'],
            link_selector=row['link_selector'],
            title_selector=row['title_selector'],
            description_selector=row['description_selector'],
            content_selector=row['content_selector'],
            remove_selector=row['remove_selector'],
            status=row['status'],
        )

    def save(self, entity: Source):
        query = """
            INSERT INTO sources (
                name, domain, path, category_id, description,
                link_selector, title_selector, description_selector,
                content_selector, remove_selector, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            entity.name, entity.domain, entity.path, entity.category_id,
            entity.description, entity.link_selector, entity.title_selector,
            entity.description_selector, entity.content_selector,
            entity.remove_selector, entity.status,
        )
        result = self._execute(query, params)
        if result is None:
            return None
        entity.id = result[1]
        return entity.id

    def update(self, entity: Source):
        query = """
            UPDATE sources
            SET name = %s, domain = %s, path = %s, category_id = %s, description = %s,
                link_selector = %s, title_selector = %s, description_selector = %s,
                content_selector = %s, remove_selector = %s, status = %s
            WHERE id = %s
        """
        params = (
            entity.name, entity.domain, entity.path, entity.category_id,
            entity.description, entity.link_selector, entity.title_selector,
            entity.description_selector, entity.content_selector,
            entity.remove_selector, entity.status, entity.id,
        )
        result = self._execute(query, params)
        return result is not None and result[0] > 0

    def update_status(self, entity_id, status: str) -> bool:
        result = self._execute("UPDATE sources SET status = %s WHERE id = %s", (status, entity_id))
        return result is not None and result[0] > 0

    def find_all(self):
        return [self._to_entity(r) for r in self._query("SELECT * FROM sources ORDER BY id")]

    def find_active(self):
        rows = self._query("SELECT * FROM sources WHERE status = 'Active' ORDER BY id")
        return [self._to_entity(r) for r in rows]

    def find_by_id(self, entity_id):
        row = self._query_one("SELECT * FROM sources WHERE id = %s", (entity_id,))
        return self._to_entity(row) if row else None

    def find_by_domain_and_path(self, domain, path):
        row = self._query_one(
            "SELECT * FROM sources WHERE domain = %s AND path = %s", (domain, path)
        )
        return self._to_entity(row) if row else None

    def delete_by_id(self, entity_id):
        result = self._execute("DELETE FROM sources WHERE id = %s", (entity_id,))
        return result is not None and result[0] > 0