class Source:
    def __init__(self, name, domain, path, category_id, 
                 description, link_selector, title_selector, 
                 description_selector, content_selector, remove_selector, 
                 status="Active", id=None):
        self.id = id
        self.name = name
        self.domain = domain
        self.path = path
        self.category_id = category_id
        self.description = description
        self.link_selector = link_selector
        self.title_selector = title_selector
        self.description_selector = description_selector
        self.content_selector = content_selector
        self.remove_selector = remove_selector
        self.status = status
        