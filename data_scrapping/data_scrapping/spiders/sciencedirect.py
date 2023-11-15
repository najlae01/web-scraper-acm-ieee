import scrapy
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from ..items import DataScrappingItem
import time


class ScienceDirectSpider(scrapy.Spider):
    name = "sciencedirect"
    start_urls = None
    topic = None
    allowed_domains = ["www.sciencedirect.com"]

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")

    handle_httpstatus_list = [301]

    def __init__(self, keyword=None, topic=None, *args, **kwargs):
        super(ScienceDirectSpider, self).__init__(*args, **kwargs)
        self.topic = topic
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get('https://www.sciencedirect.com/')
        time.sleep(5)
        self.driver.find_element(By.ID, 'gh-signin-btn').click()
        time.sleep(5)
        username = self.driver.find_element(By.ID, "bdd-email")
        username.send_keys("najlae.abarghache@etu.uae.ac.ma")
        time.sleep(5)
        self.driver.find_element(By.ID, "bdd-elsPrimaryBtn").click()
        password = self.driver.find_element(By.ID, "bdd-password")
        password.send_keys("Fstt2023.")
        time.sleep(5)
        self.driver.find_element(By.ID, "bdd-elsPrimaryBtn").click()
        time.sleep(5)
        self.start_urls = ['https://www.sciencedirect.com/search']
        self.driver.get('https://www.sciencedirect.com/search?qs=' + topic)

    def parse(self, response):
        delay = 10
        try:
            wait = WebDriverWait(self.driver, delay)
            wait_element = wait.until(EC.presence_of_element_located((By.ID, 'srp-results-list')))
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div.result-item-content h2 span a")
            for element in elements:
                article = element.get_attribute("href")
                driver1 = webdriver.Chrome()
                driver1.get(str(article))
                driver1.minimize_window()

                authors_name = []
                authors_university = []
                authors_country = []
                title = ""
                doi = ""
                date_publication = 0
                abstract = ""
                references = []
                issn = ""
                indexation = 0
                impact_factor = 0
                affiliation = []
                try:
                    wait1 = WebDriverWait(self.driver, delay)
                    wait_element1 = wait1.until(EC.presence_of_element_located((By.ID, 'abstracts')))
                    elements1 = driver1.find_elements(By.CSS_SELECTOR, "span.title-text")
                    for element1 in elements1:
                        title = element1.text
                    elements1 = driver1.find_elements(By.CSS_SELECTOR,
                    "div#author-group.author-group a.author.size-m.workspace-trigger span.content")
                    for element1 in elements1:
                        authors_name.append(element1.text)
                    try:
                        elems = driver1.find_elements(By.CSS_SELECTOR, "button#show-more-btn")
                        ActionChains(driver1).click(elems[0]).perform()
                        elements1 = driver1.find_elements(By.CSS_SELECTOR, "dl.affiliation dd")
                        for element1 in elements1:
                            affiliation.append(element1.text)
                    except Exception:
                        print(Exception)
                    elements1 = driver1.find_elements(By.CSS_SELECTOR, "a.doi")
                    for element1 in elements1:
                        doi = element1.text
                    elements1 = driver1.find_elements(By.CSS_SELECTOR,
                        "div#publication.Publication div.publication-volume div.text-xs")
                    for element1 in elements1:
                        date_publication = element1.text
                    elements1 = driver1.find_elements(By.CSS_SELECTOR, "div#abstracts.Abstracts.u-font-serif")
                    for element1 in elements1:
                        abstract = element1.text
                    elements1 = driver1.find_elements(By.CSS_SELECTOR, "ul li.bib-reference.u-margin-s-bottom")
                    for element1 in elements1:
                        references.append(element1.text)
                except TimeoutException:
                    print("Loading data took too much time.")
                driver1.quit()

                date_publication = date_publication.split(',')[1]
                date_publication = int(date_publication.split(' ')[-1])

                item = DataScrappingItem()

                for inf in affiliation:
                    y = inf.split(',')
                    authors_university.append(y[0])
                    authors_country.append(y[-1])
                authors_country = ';'.join(authors_country)
                item['authors_name'] = authors_name
                item['authors_university'] = authors_university
                item['authors_country'] = authors_country.strip()

                item['title'] = title
                item['topic'] = self.topic
                item['doi'] = doi
                item['date_publication'] = date_publication
                item['abstract'] = abstract
                item['references'] = references

                item['publisher'] = "ScienceDirect"
                item['issn'] = issn
                item['indexation'] = indexation
                item['impact_factor'] = impact_factor

                yield item
        except TimeoutException:
            print("Loading data took too much time.")
        self.driver.quit()
