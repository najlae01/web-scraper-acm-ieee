import scrapy
import re
from scrapy_splash import SplashRequest
from selenium.common import NoSuchElementException

from ..items import DataScrappingItem
from urllib.parse import urlencode
from selenium import webdriver
from scrapy_selenium import SeleniumRequest
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class IeeeSpider(scrapy.Spider):
    name = "ieee"
    topic = None
    start_urls = []
    page_no = 1
    r = None
    allowed_domains = ["ieeexplore.ieee.org"]
    retry_http_codes = [502, 503, 504, 400, 403, 404, 408]
    max_retries = 10
    retry_times = 10

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")

    def __init__(self, topic=None, *args, **kwargs):
        super(IeeeSpider, self).__init__(*args, **kwargs)
        self.topic = topic
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get('https://ieeexplore.ieee.org/')
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

    def start_requests(self):
        for i in range(11):
            params = {
                'newsearch': 'true',
                'queryText': self.topic,
                'highlight': 'true',
                'returnType': 'SEARCH',
                'matchPubs': 'true',
                'pageNumber': str(i),
                'returnFacets': 'ALL',
            }
            url = 'https://ieeexplore.ieee.org/search/searchresult.jsp?' + urlencode(params)
            yield SeleniumRequest(url=url, callback=self.parse, wait_time=3)

    def parse(self, response):
        print("crawling page")
        articles_links = self.driver.find_elements(By.XPATH, '//a[contains(@href, "/document/")]')
        for article in articles_links:
            article_url = article.get_attribute('href')
            yield SeleniumRequest(url=article_url, callback=self.parse_article, wait_time=5)

    def parse_article(self, response):
        self.driver.get(response.url)
        # authors
        elements = self.driver.find_elements(By.CLASS_NAME, "fa fa-angle-up")
        if len(elements) >= 1:
            elements[0].click()  # Click the first element
        else:
            print("Not enough matching elements found.")
        try:
            # wait
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'author-card'))
            )
            # Find the span element within .author-card
            authors_name = self.driver.find_elements(By.CLASS_NAME, 'author-card row.g-0 col-24-24 a span')
        except NoSuchElementException:
            authors_name = None

        authors_universities = []
        authors_countries = []

        for author_item in authors_name:
            university_country_selector = author_item.find_element(By.CLASS_NAME,
                                                 'author-card row.g-0 col-24-24 div:nth-child(2)').text

            university_match = re.match(r'^([^,]+)', university_country_selector)
            country_match = re.search(r'[^,]+$', university_country_selector)

            if university_match:
                authors_universities.append(university_match.group(1).strip())
            else:
                authors_universities.append(None)

            if country_match:
                authors_countries.append(country_match.group().strip())
            else:
                authors_countries.append(None)

        # articles
        title = self.driver.find_element(By.CLASS_NAME, 'document-title span').text
        topic = self.topic

        doi = self.driver.find_element(By.CLASS_NAME, 'u-pb-1.stats-document-abstract-doi a')
        doi_value = doi.get_attribute('href') if doi else None

        date_publication_selector = self.driver.find_element(By.CLASS_NAME,
                                                             'u-pb-1.stats-document-abstract-publishedIn a').text

        date_publication = None
        if date_publication_selector:
            try:
                date_publication = int(re.search(r'(\d{4})', date_publication_selector).group(1))
            except (ValueError, AttributeError):
                pass

        abstract = self.driver.find_element(By.CLASS_NAME, 'abstract-text col-12 u-mb-1 div').text

        references = []
        for reference_container in self.driver.find_elements(By.ID, 'reference-container'):
            reference = reference_container.find_elements(By.CLASS_NAME, 'd-flex col.u-px-1 div')
            references.extend([ref.text for ref in reference])

        citation_selector = self.driver.find_element(By.ID, 'citations-section-container a').text
        try:
            if citation_selector is not None:
                citations = ''.join(filter(str.isdigit, citation_selector))
            else:
                citations = 0  # or any other default value you want to set when there are no citations
        except ValueError:
            citations = 0

        downloads = self.driver.find_element(By.CLASS_NAME, 'usage-details-total-since b span').text
        try:
            if downloads is not None:
                downloads = int(''.join(filter(str.isdigit, downloads)))
            else:
                downloads = 0  # or any other default value you want to set when there are no downloads
        except ValueError:
            downloads = 0

        # journal
        publisher = "IEEE"
        issn = "21682372"
        indexation = 24
        impact_factor = 3.825

        item = DataScrappingItem()

        item['authors_name'] = authors_name
        item['authors_university'] = authors_universities
        item['authors_country'] = authors_countries

        item['title'] = title
        item['topic'] = topic
        item['doi'] = doi_value
        try:
            item['date_publication'] = date_publication
        except ValueError:
            item['date_publication'] = 0
        item['abstract'] = abstract
        item['references'] = references
        item['citation'] = citations
        item['downloads'] = downloads

        item['publisher'] = publisher
        item['issn'] = issn
        item['indexation'] = indexation
        item['impact_factor'] = impact_factor

        yield item

    def closed(self, reason):
        self.driver.quit()
