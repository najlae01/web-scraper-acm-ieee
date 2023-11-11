import scrapy
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from data_scrapping.items import DataScrappingItem


class ScienceDirectSpider(scrapy.Spider):
    name = "sciencedirect"
    start_urls = None
    driver = webdriver.Chrome()
    allowed_domains = ["sciencedirect.com"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.sciencedirect.com/",
        "Content-Type": "application/json",
    }

    handle_httpstatus_list = [302]
    handle_httpstatus_list = [301]

    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
    ]

    def __init__(self, keyword=None, topic=None, *args, **kwargs):
        super(ScienceDirectSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://www.sciencedirect.com/search']
        self.driver.get("https://www.sciencedirect.com/search?qs=" + topic)
        self.r = scrapy.Request("https://www.sciencedirect.com/search?qs=" + topic,
                               method='POST', headers=self.headers)

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
