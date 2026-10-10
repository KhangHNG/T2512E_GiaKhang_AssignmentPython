from urllib.parse import urlparse

from menus.Menu import Menu
from models.source import Source
from repositories.SourceRepository import SourceRepository
from repositories.CategoryRepository import CategoryRepository


class SourceMenu(Menu):
    def __init__(self, db_conn=None):
        super().__init__(db_conn)
        self.source_repo = SourceRepository(self.db_conn)
        self.category_repo = CategoryRepository(self.db_conn)

    def print_menu(self):
        while True:
            print("\n--- QUẢN LÝ NGUỒN TIN ---")
            print("1. Xem danh sách các nguồn tin")
            print("2. Thêm nguồn tin mới")
            print("3. Cập nhật thông tin nguồn tin")
            print("4. Xóa nguồn tin (hoặc đổi trạng thái Kích hoạt/Bỏ kích hoạt)")
            print("0. Quay lại Menu chính")

            selection = self.read_int("Nhập lựa chọn (0 - 4): ", 0, 4)
            print()

            if selection == 1:
                self.show_sources()
            elif selection == 2:
                self.add_source()
            elif selection == 3:
                self.update_source()
            elif selection == 4:
                self.delete_or_toggle_source()
            elif selection == 0:
                print("Đang quay lại Menu chính...")
                break

    def show_sources(self):
        sources = self.source_repo.find_all()
        if not sources:
            print("Chưa có nguồn tin nào.")
            return sources
        for s in sources:
            print(f"{s.id} - {s.name} - https://{s.domain}{s.path} - {s.status}")
        return sources

    def add_source(self):
        print("--- THÊM NGUỒN TIN MỚI ---")
        name = self.read_text("Tên nguồn (vd: VnExpress): ", required=True)
        domain, path = self._ask_url("URL trang chủ/chuyên mục (vd: https://vnexpress.net/the-thao): ")

        if self.source_repo.find_by_domain_and_path(domain, path):
            print("Nguồn này (cùng domain và đường dẫn) đã tồn tại.")
            return

        category_id = self._choose_category()
        description = self.read_text("Mô tả (Enter để bỏ qua): ")
        print("Cấu hình CSS Selector:")
        link_selector = self.read_text("  - Selector thẻ <a> lấy link bài viết: ", required=True)
        title_selector = self.read_text("  - Selector tiêu đề bài viết: ", required=True)
        description_selector = self.read_text("  - Selector tóm tắt (Enter để bỏ qua): ")
        content_selector = self.read_text("  - Selector nội dung bài viết: ", required=True)
        remove_selector = self.read_text("  - Selector các phần cần loại bỏ, vd: quảng cáo (Enter để bỏ qua): ")

        source = Source(
            name=name, domain=domain, path=path, category_id=category_id,
            description=description, link_selector=link_selector,
            title_selector=title_selector, description_selector=description_selector,
            content_selector=content_selector, remove_selector=remove_selector,
            status="Active",
        )
        new_id = self.source_repo.save(source)
        if new_id:
            print(f"Đã thêm nguồn tin '{name}' (ID = {new_id}).")
        else:
            print("Thêm nguồn tin thất bại.")

    def update_source(self):
        print("--- CẬP NHẬT NGUỒN TIN ---")
        if not self.show_sources():
            return
        source = self._ask_source("Nhập ID nguồn cần cập nhật (0 để hủy): ")
        if not source:
            return

        print("(Nhấn Enter để giữ nguyên giá trị hiện tại)")
        source.name = self.read_text(f"Tên nguồn [{source.name}]: ", default=source.name)

        current_url = f"https://{source.domain}{source.path}"
        domain, path = self._ask_url(f"URL [{current_url}]: ", default=(source.domain, source.path))
        existing = self.source_repo.find_by_domain_and_path(domain, path)
        if existing and existing.id != source.id:
            print("Đã có nguồn khác dùng URL này. Hủy cập nhật.")
            return
        source.domain, source.path = domain, path

        source.category_id = self._choose_category(current=source.category_id)
        source.description = self.read_text(
            f"Mô tả [{source.description or ''}]: ", default=source.description or "")
        source.link_selector = self.read_text(
            f"Selector link [{source.link_selector}]: ", default=source.link_selector)
        source.title_selector = self.read_text(
            f"Selector tiêu đề [{source.title_selector}]: ", default=source.title_selector)
        source.description_selector = self.read_text(
            f"Selector tóm tắt [{source.description_selector or ''}]: ",
            default=source.description_selector or "")
        source.content_selector = self.read_text(
            f"Selector nội dung [{source.content_selector}]: ", default=source.content_selector)
        source.remove_selector = self.read_text(
            f"Selector loại bỏ [{source.remove_selector or ''}]: ",
            default=source.remove_selector or "")

        if self.source_repo.update(source):
            print("Cập nhật thành công.")
        else:
            print("Cập nhật thất bại (hoặc không có thay đổi).")

    def delete_or_toggle_source(self):
        print("--- XÓA / ĐỔI TRẠNG THÁI NGUỒN TIN ---")
        if not self.show_sources():
            return
        source = self._ask_source("Nhập ID nguồn tin (0 để hủy): ")
        if not source:
            return

        print(f"\nNguồn đã chọn: {source.name} (đang {source.status})")
        print("1. Đổi trạng thái Active/Inactive")
        print("2. Xóa nguồn khỏi CSDL")
        print("0. Hủy")
        choice = self.read_int("Nhập lựa chọn (0 - 2): ", 0, 2)

        if choice == 1:
            new_status = "Inactive" if source.status == "Active" else "Active"
            if self.source_repo.update_status(source.id, new_status):
                print(f"Đã chuyển trạng thái sang {new_status}.")
            else:
                print("Đổi trạng thái thất bại.")
        elif choice == 2:
            if self.source_repo.delete_by_id(source.id):
                print("Đã xóa nguồn tin.")
            else:
                print("Xóa thất bại (nguồn có thể đang có bài viết, hãy dùng chức năng Bỏ kích hoạt).")

    def _ask_source(self, prompt):
        source_id = self.read_int(prompt, 0)
        if source_id == 0:
            return None
        source = self.source_repo.find_by_id(source_id)
        if not source:
            print(f"Không tìm thấy nguồn tin có ID = {source_id}.")
        return source

    @staticmethod
    def _parse_url(raw):
        raw = raw.strip()
        if "://" not in raw:
            raw = "https://" + raw
        parsed = urlparse(raw)
        if not parsed.netloc or "." not in parsed.netloc:
            return None
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        path = parsed.path or "/"
        return domain, path

    def _ask_url(self, prompt, default=None):
        while True:
            raw = input(prompt).strip()
            if not raw and default is not None:
                return default
            parsed = self._parse_url(raw) if raw else None
            if parsed:
                return parsed
            print("URL không hợp lệ. Vui lòng nhập lại.")

    def _choose_category(self, current=None):
        categories = self.category_repo.find_all()
        if not categories:
            print("(Chưa có danh mục nào trong CSDL, bỏ qua danh mục.)")
            return current
        print("Danh mục hiện có:")
        for c in categories:
            print(f"  {c.id}. {c.name}")
        valid_ids = {c.id for c in categories}
        while True:
            raw = input("Nhập ID danh mục (Enter để bỏ qua/giữ nguyên): ").strip()
            if not raw:
                return current
            if raw.isdigit() and int(raw) in valid_ids:
                return int(raw)
            print("ID danh mục không hợp lệ.")