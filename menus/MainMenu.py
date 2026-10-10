from menus.Menu import Menu
from menus.SourceMenu import SourceMenu
from menus.ArticleMenu import ArticleMenu
from menus.CrawlerMenu import CrawlerMenu


class MainMenu(Menu):
    def __init__(self):
        super().__init__()
        self.sourceMenu = SourceMenu(self.db_conn)
        self.articleMenu = ArticleMenu(self.db_conn)
        self.crawlerMenu = CrawlerMenu(self.db_conn)

    def print_menu(self):
        while True:
            print("\n=== CHƯƠNG TRÌNH TỔNG HỢP TIN TỨC ĐA NGUỒN ===")
            print("1. Quản lý nguồn tin")
            print("2. Quản lý tin tức")
            print("3. Chạy Crawler")
            print("0. Thoát chương trình")

            selection = self.read_int("Nhập lựa chọn (0 - 3): ", 0, 3)
            print()

            if selection == 1:
                self.sourceMenu.print_menu()
            elif selection == 2:
                self.articleMenu.print_menu()
            elif selection == 3:
                self.crawlerMenu.print_menu()
            elif selection == 0:
                print("Đang thoát chương trình...")
                break