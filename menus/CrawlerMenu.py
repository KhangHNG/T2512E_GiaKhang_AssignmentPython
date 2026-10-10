import requests

from menus.Menu import Menu
from repositories.SourceRepository import SourceRepository
from services.vnexpress_crawler_service import VnexpressCrawlerService
from services.vietnamnet_crawler_service import VietnamnetCrawlerService


class CrawlerMenu(Menu):
    CRAWLERS = {
        "vnexpress.net": VnexpressCrawlerService,
        "vietnamnet.vn": VietnamnetCrawlerService,
    }

    def __init__(self, db_conn=None):
        super().__init__(db_conn)
        self.source_repo = SourceRepository(self.db_conn)

    def print_menu(self):
        while True:
            print("\n--- CHẠY CRAWLER ---")
            print("1. Cào tất cả các nguồn đang Active")
            print("2. Cào một nguồn cụ thể")
            print("0. Quay lại Menu chính")

            selection = self.read_int("Nhập lựa chọn (0 - 2): ", 0, 2)
            print()

            if selection == 1:
                self.crawl_all()
            elif selection == 2:
                self.crawl_one()
            elif selection == 0:
                print("Đang quay lại Menu chính...")
                break

    def crawl_all(self):
        sources = self.source_repo.find_active()
        if not sources:
            print("Không có nguồn nào đang Active.")
            return
        for source in sources:
            self._crawl_source(source)
        print("\n=== Đã cào xong tất cả các nguồn ===")

    def crawl_one(self):
        sources = self.source_repo.find_all()
        if not sources:
            print("Chưa có nguồn tin nào.")
            return
        for s in sources:
            print(f"{s.id} - {s.name} - https://{s.domain}{s.path} - {s.status}")

        source_id = self.read_int("Nhập ID nguồn cần cào (0 để hủy): ", 0)
        if source_id == 0:
            return
        source = self.source_repo.find_by_id(source_id)
        if not source:
            print(f"Không tìm thấy nguồn có ID = {source_id}.")
            return
        if source.status != "Active":
            print(f"Nguồn '{source.name}' đang Inactive, hãy kích hoạt trước khi cào.")
            return
        self._crawl_source(source)

    def _crawl_source(self, source):
        crawler_cls = self.CRAWLERS.get(source.domain)
        if crawler_cls is None:
            print(f"[{source.name}] Chưa hỗ trợ crawler cho domain '{source.domain}'.")
            return

        print(f"\n[{source.name}] Bắt đầu cào...")
        try:
            crawler = crawler_cls(self.db_conn, source)
            crawler.crawl_fresh_link()
            crawler.crawl_link_detail()
            print(f"[{source.name}] Hoàn thành.")
        except requests.exceptions.ConnectionError:
            print(f"[{source.name}] Lỗi mạng: không kết nối được tới máy chủ.")
        except requests.exceptions.Timeout:
            print(f"[{source.name}] Lỗi: quá thời gian chờ phản hồi.")
        except requests.exceptions.HTTPError as e:
            print(f"[{source.name}] Lỗi HTTP: {e}")
        except Exception as e:
            print(f"[{source.name}] Lỗi không xác định: {e}")