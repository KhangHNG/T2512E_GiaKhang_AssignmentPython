class Article:
    def __init__(self, url, category_id, source_id, title="", body="",
                 status="Pending", id=None, created_at=None,
                 updated_at=None, deleted_at=None):
        self.id = id
        self.url = url
        self.category_id = category_id
        self.source_id = source_id
        self.title = title          
        self.body = body            
        self.status = status       
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at