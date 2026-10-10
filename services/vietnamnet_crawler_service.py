import threading
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from models.article import Article
from services.crawler_service import CrawlerService
from repositories.ArticleRepository import ArticleRepository


class VietnamnetCrawlerService(CrawlerService):
    DEFAULT_LINK_SELECTOR = 'div.verticalPost__main h3.vnn-title a'
    DEFAULT_TITLE_SELECTOR = 'h1.content-detail-title'
    DEFAULT_CONTENT_SELECTOR = 'div.maincontent p'

    def __init__(self, db_conn, source):
        super().__init__()
        self.db_conn = db_conn
        self.source = source  # cấu hình nguồn (domain, path, selector...) lấy từ DB
        self.article_repo = ArticleRepository(db_conn)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def crawl_fresh_link(self):
        source = self.source
        full_url = f"https://{source.domain}{source.path}"
        print(f"[{source.name}] Đang lấy danh sách bài viết từ {full_url}")

        response = requests.get(full_url, headers=self.headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        link_selector = source.link_selector or self.DEFAULT_LINK_SELECTOR

        seen = set()
        new_count = 0
        for a in soup.select(link_selector):
            raw_href = a.get('href')
            if not raw_href:
                continue
            clean_url = urljoin(full_url, raw_href).split('#')[0]
            if clean_url in seen:
                continue
            seen.add(clean_url)

            if self.article_repo.exists_by_url(clean_url):
                continue

            article = Article(
                url=clean_url,
                category_id=source.category_id,
                source_id=source.id,
                status="Pending",
            )
            if self.article_repo.save(article):
                new_count += 1

        print(f"[{source.name}] Đã cào {new_count} bài mới (Pending).")

    def crawl_article_detail(self, article: Article):
        source = self.source
        try:
            res = requests.get(article.url, headers=self.headers, timeout=10)
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                self.article_repo.delete_by_id(article.id)
                print(f"[{source.name}] Bài không còn tồn tại (404), đã bỏ qua: {article.url}")
            else:
                print(f"[{source.name}] Lỗi HTTP khi tải bài {article.url}: {e}")
            return
        except requests.exceptions.RequestException as e:
            print(f"[{source.name}] Lỗi mạng khi tải bài {article.url}: {e}")
            return

        soup = BeautifulSoup(res.text, 'html.parser')

        remove_selector = source.remove_selector or 'script, style'
        for trash in soup.select(remove_selector):
            trash.decompose()

        title_el = soup.select_one(source.title_selector or self.DEFAULT_TITLE_SELECTOR)
        title = title_el.get_text(strip=True) if title_el else ""

        body_els = soup.select(source.content_selector or self.DEFAULT_CONTENT_SELECTOR)
        body = "\n".join(p.get_text(strip=True) for p in body_els)

        if title and body:
            article.title = title[:500]
            article.body = body
            article.status = "Completed"
            self.article_repo.update(article)
            print(f"[{source.name}] Đã cào nội dung: {title[:60]}")
        else:
            self.article_repo.delete_by_id(article.id)
            print(f"[{source.name}] Không có tiêu đề/nội dung, đã bỏ qua: {article.url}")

    def crawl_link_detail(self):
        """Bước 3: cào nội dung các bài Pending của nguồn này (đa luồng)."""
        source = self.source
        pending_articles = self.article_repo.find_by_status("Pending", source_id=source.id)
        if not pending_articles:
            print(f"[{source.name}] Không có bài nào ở trạng thái Pending.")
            return

        print(f"[{source.name}] Đang cào chi tiết {len(pending_articles)} bài...")
        start_time = time.time()
        list_thread = []
        for article in pending_articles:
            t = threading.Thread(target=self.crawl_article_detail, args=[article])
            t.start()
            list_thread.append(t)
        for t in list_thread:
            t.join()
        print(f"[{source.name}] Hoàn thành trong {time.time() - start_time:.2f}s.")