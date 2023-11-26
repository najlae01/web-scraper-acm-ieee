import scrapy
import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from scrapy_selenium import SeleniumRequest
from ..items import DataScrappingItem
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class IeeeSpider(scrapy.Spider):
    name = "ieee"
    topic = None
    start_urls = []
    page_no = 0
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
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                       options=self.chrome_options)

    def start_requests(self):
        for i in range(0, 400):
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
            self.start_urls.append(url)
            yield SeleniumRequest(url=url, callback=self.parse, wait_time=3)

    def parse(self, response):
        self.driver.get(response.url)
        print("crawling page")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'List-results-items')))
        articles_links = self.driver.find_elements(By.XPATH, '//a[contains(@href, "/document/")]')
        print(articles_links)
        for article in articles_links:
            article_url = article.get_attribute('href')
            if "citations" not in article_url and "media" not in article_url:
                print("Link " + article_url)
                yield SeleniumRequest(url=article_url, callback=self.parse_article, wait_time=3)

    def parse_article(self, response):
        self.driver.get(response.url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'document-title')))
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # articles
        title_selector = soup.select_one('.document-title')
        title = title_selector.select_one('span').text
        topic = self.topic

        doi = soup.select_one('.u-pb-1.stats-document-abstract-doi a')
        doi_value = doi['href'] if doi else None

        date_publication_selector = soup.select_one('.stats-document-abstract-publishedIn')
        date_publication = date_publication_selector.select_one('a')
        if date_publication:
            try:
                date_publication = int(re.search(r'(\d{4})', date_publication.text).group(1))
            except (ValueError, AttributeError):
                pass

        abstract_selector = soup.select_one('.abstract-text .col-12 .u-mb-1 div')
        abstract = abstract_selector.text if abstract_selector else None

        references = []
        for reference_container in soup.select('.reference-container'):
            reference_text = reference_container.select_one('.col.u-px-1')
            if reference_text:
                references.append(reference_text.text.strip())

        citation_element = soup.select_one(
            '.document-banner-metric-container .document-banner-metric:nth-child(1)')
        citation_selector = citation_element.select_one('.document-banner-metric-count')
        downloads_element = soup.select_one(
            '.document-banner-metric-container .document-banner-metric:nth-child(2)')
        downloads_selector = downloads_element.select_one('.document-banner-metric-count')
        citations = 0
        if citation_selector:
            try:
                citations = int(citation_selector.text)
            except ValueError:
                citations = 0
        downloads = 0
        if downloads_selector:
            try:
                downloads = int(downloads_selector.text)
            except ValueError:
                downloads = 0

        # journal
        publisher = "IEEE"
        issn = "21682372"
        indexation = 24
        impact_factor = 3.825

        # authors
        # Select all author elements
        authors_names_selector = soup.select('.authors-container .authors-info-container span.blue-tooltip a span')

        authors_names = []

        for author_element in authors_names_selector:
            author_name = author_element.text.strip()
            authors_names.append(author_name)

        '''elements = self.driver.find_elements(By.CLASS_NAME, "browse-pub-tab")
        if len(elements) >= 1:
            elements[0].find_element(By.CSS_SELECTOR, "a").click()
        else:
            print("Not enough matching elements found.")'''

        authors_universities = []
        authors_countries = []

        authors_elements = soup.find_all("div", {"class": "author-card text-base-md-lh"})

        for author_element in authors_elements:
            # Extract university and country information from the parent element
            university_country_parent = author_element.find('div', class_='col-24-24')
            if university_country_parent is None:
                university_country_parent = author_element.find('div', class_='col-14-24')

            university_country_selector = university_country_parent.find_all('div')[1]
            if university_country_selector:
                university_country_text = university_country_selector.text
                university_match = re.match(r'^([^,]+)', university_country_text)
                country_match = re.search(r'[^,]+$', university_country_text)

                if university_match:
                    authors_universities.append(university_match.group(1).strip())
                else:
                    authors_universities.append(None)

                if country_match:
                    authors_countries.append(country_match.group().strip())
                else:
                    authors_countries.append(None)

            else:
                authors_universities.append(None)
                authors_countries.append(None)

        item = DataScrappingItem()

        item['authors_name'] = authors_names
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
