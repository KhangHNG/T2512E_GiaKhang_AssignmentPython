import math
from datetime import datetime

from menus.Menu import Menu
from repositories.ArticleRepository import ArticleRepository
from repositories.SourceRepository import SourceRepository


class ArticleMenu(Menu):
    PAGE_SIZE = 10

    def __init__(self, db_conn=None):
        super().__init__(db_conn)
        self.article_repo = ArticleRepository(self.db_conn)
        self.source_repo = SourceRepository(self.db_conn)

    def print_menu(self):
        while True:
            print("\n--- QUẢN LÝ TIN TỨC ---")
            print("1. Xem danh sách tin tức (phân trang bằng phím < và >)")
            print("2. Tìm kiếm tin tức (theo tiêu đề hoặc nội dung)")
            print("3. Lọc tin tức theo Nguồn hoặc Ngày cào")
            print("4. Xem chi tiết một bài viết")
            print("5. Xóa tin tức")
            print("0. Quay lại Menu chính")

            selection = self.read_int("Nhập lựa chọn (0 - 5): ", 0, 5)
            print()

            if selection == 1:
                self._paginate("DANH SÁCH TIN TỨC")
            elif selection == 2:
                self.search_articles()
            elif selection == 3:
                self.filter_articles()
            elif selection == 4:
                self.show_detail()
            elif selection == 5:
                self.delete_articles()
            elif selection == 0:
                print("Đang quay lại Menu chính...")
                break

    def _paginate(self, title, keyword=None, source_id=None, crawled_date=None):
        total = self.article_repo.count(keyword, source_id, crawled_date)
        if total == 0:
            print("Không có bài viết nào.")
            return

        total_pages = math.ceil(total / self.PAGE_SIZE)
        source_names = {s.id: s.name for s in self.source_repo.find_all()}
        page = 1

        while True:
            articles = self.article_repo.find_page(
                page, self.PAGE_SIZE, keyword, source_id, crawled_date)
            print(f"\n--- {title} | Trang {page}/{total_pages} | Tổng {total} bài ---")
            for a in articles:
                title_text = a.title or "(chưa có tiêu đề)"
                source_name = source_names.get(a.source_id, "?")
                crawled = str(a.created_at)[:16] if a.created_at else ""
                print(f"{a.id} - {title_text} - {source_name} - {a.status} - {crawled}")

            nav = input("[<] Trang trước | [>] Trang sau | [số] Đến trang | [q] Thoát: ").strip().lower()
            if nav == ">":
                if page < total_pages:
                    page += 1
                else:
                    print("Đã ở trang cuối.")
            elif nav == "<":
                if page > 1:
                    page -= 1
                else:
                    print("Đã ở trang đầu.")
            elif nav == "q":
                break
            elif nav.isdigit() and 1 <= int(nav) <= total_pages:
                page = int(nav)
            else:
                print("Lựa chọn không hợp lệ.")

    def search_articles(self):
        keyword = self.read_text("Nhập từ khóa (tiêu đề hoặc nội dung): ", required=True)
        self._paginate(f"KẾT QUẢ TÌM KIẾM '{keyword}'", keyword=keyword)

    def filter_articles(self):
        print("--- LỌC TIN TỨC (Enter để bỏ qua tiêu chí) ---")
        source_id = None
        sources = self.source_repo.find_all()
        if sources:
            for s in sources:
                print(f"  {s.id}. {s.name}")
            valid_ids = {s.id for s in sources}
            while True:
                raw = input("Nhập ID nguồn: ").strip()
                if not raw:
                    break
                if raw.isdigit() and int(raw) in valid_ids:
                    source_id = int(raw)
                    break
                print("ID nguồn không hợp lệ.")

        crawled_date = None
        while True:
            raw = input("Nhập ngày cào (YYYY-MM-DD): ").strip()
            if not raw:
                break
            try:
                datetime.strptime(raw, "%Y-%m-%d")
                crawled_date = raw
                break
            except ValueError:
                print("Sai định dạng ngày, ví dụ: 2026-10-10.")

        if source_id is None and crawled_date is None:
            print("Bạn chưa chọn tiêu chí lọc nào.")
            return
        self._paginate("KẾT QUẢ LỌC", source_id=source_id, crawled_date=crawled_date)

    def show_detail(self):
        article_id = self.read_int("Nhập ID bài viết (0 để hủy): ", 0)
        if article_id == 0:
            return
        article = self.article_repo.find_by_id(article_id)
        if not article:
            print(f"Không tìm thấy bài viết có ID = {article_id}.")
            return

        source = self.source_repo.find_by_id(article.source_id)
        print("\n" + "=" * 80)
        print(f"Tiêu đề   : {article.title or '(chưa có)'}")
        print(f"Nguồn     : {source.name if source else '?'}")
        print(f"Ngày cào  : {article.created_at or ''}")
        print(f"Trạng thái: {article.status}")
        print(f"Đường dẫn : {article.url}")
        print("-" * 80)
        print(f"Nội dung:\n{article.body or '(chưa cào nội dung)'}")
        print("=" * 80)
        input("Nhấn Enter để quay lại...")

    def delete_articles(self):
        print("1. Xóa một bài viết theo ID")
        print("2. Xóa các bài viết quá cũ")
        print("0. Hủy")
        choice = self.read_int("Nhập lựa chọn (0 - 2): ", 0, 2)

        if choice == 1:
            article_id = self.read_int("Nhập ID bài viết cần xóa (0 để hủy): ", 0)
            if article_id == 0:
                return
            article = self.article_repo.find_by_id(article_id)
            if not article:
                print(f"Không tìm thấy bài viết có ID = {article_id}.")
                return
            if self.article_repo.delete_by_id(article_id):
                print(f"Đã xóa bài viết: {article.title or article.url}")
            else:
                print("Xóa thất bại.")
        elif choice == 2:
            days = self.read_int("Xóa các bài cũ hơn bao nhiêu ngày? (0 để hủy): ", 0)
            if days == 0:
                return
            deleted = self.article_repo.delete_older_than(days)
            print(f"Đã xóa {deleted} bài viết cũ hơn {days} ngày.")