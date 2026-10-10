from database.DatabaseConnection import DatabaseConnection
from menus.MainMenu import MainMenu
from models.category import Category
from models.source import Source
from models.article import Article
from repositories.CategoryRepository import CategoryRepository
from repositories.ArticleRepository import ArticleRepository
from services.crawler_service import CrawlerService
from services.vietnamnet_crawler_service import VietnamnetCrawlerService
from services.vnexpress_crawler_service import VnexpressCrawlerService
from repositories.SourceRepository import SourceRepository


if __name__ == "__main__":
    menu = MainMenu()
    menu.print_menu()