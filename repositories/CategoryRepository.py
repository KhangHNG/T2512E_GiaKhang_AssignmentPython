from models.category import Category
from repositories.Repositories import BaseRepository


class CategoryRepository(BaseRepository):
    def __init__(self, db_connection):
        super().__init__(db_connection)

    @staticmethod
    def _to_entity(row):
        return Category(id=row['id'], name=row['name'], description=row['description'])

    def save(self, entity: Category):
        result = self._execute(
            "INSERT INTO categories (name, description, created_at, updated_at) "
            "VALUES (%s, %s, NOW(), NOW())",
            (entity.name, entity.description or ""),
        )
        if result is None:
            return None
        entity.id = result[1]
        return entity.id

    def update(self, entity: Category):
        result = self._execute(
            "UPDATE categories SET name = %s, description = %s, updated_at = NOW() "
            "WHERE id = %s AND deleted_at IS NULL",
            (entity.name, entity.description or "", entity.id),
        )
        return result is not None and result[0] > 0

    def find_all(self):
        rows = self._query("SELECT * FROM categories WHERE deleted_at IS NULL ORDER BY id")
        return [self._to_entity(r) for r in rows]

    def find_by_id(self, entity_id):
        row = self._query_one(
            "SELECT * FROM categories WHERE id = %s AND deleted_at IS NULL", (entity_id,)
        )
        return self._to_entity(row) if row else None

    def delete_by_id(self, entity_id):
        result = self._execute(
            "UPDATE categories SET deleted_at = NOW(), updated_at = NOW() "
            "WHERE id = %s AND deleted_at IS NULL",
            (entity_id,),
        )
        return result is not None and result[0] > 0