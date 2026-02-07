from threading import Thread
import hashlib
from urllib.parse import urlparse
from inspect import getsource
from utils.download import download
from utils.url_pattern_detection import get_url_pattern_hash
from utils import get_logger
import scraper
import time
from collections import defaultdict

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.seen_urls = set()
        self.seen_url_patterns = defaultdict(int)
        self.MAX_URL_PATTERN_HITS = 250
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                parsed_url = urlparse(scraped_url)._replace(scheme='')
                hashed_url = hashlib.sha256(parsed_url.encode('utf-8')).hexdigest()
                hashed_url_pattern = get_url_pattern_hash()

                if self.seen_url_patterns[hashed_url_pattern] >= self.MAX_URL_PATTERN_HITS:
                    print(f"Hashed url pattern reaached its limit")
                    continue
                if hashed_url in self.seen_urls:
                    print(f"Hashed url already seen...skipping")
                    continue
                hashed_url_pattern[self.seen_url_patterns] += 1

                if hashed_url in self.seen_urls:
                    print(f"Hashed url already seen...skipping")
                    continue
                self.seen_urls.add(hashed_url)
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
