from abc import abstractmethod, ABC

from bs4 import BeautifulSoup
import requests


class CrawlerService:
    @abstractmethod
    def crawl_fresh_link(self):
        pass

    @abstractmethod
    def crawl_link_detail(self):
        pass

    def crawl_detail(self, link):
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        print(f"Processing link: {link}")
        response = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        if "vnexpress.net" in link:
            title_tag = soup.select_one('h1.title-detail')
        elif "vietnamnet.vn" in link:
            title_tag = soup.select_one('h1.content-detail-title')
        if title_tag != None:
            news_title = title_tag.text
            print(news_title)