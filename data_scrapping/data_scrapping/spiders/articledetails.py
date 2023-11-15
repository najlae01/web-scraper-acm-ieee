#!/usr/bin/env python
# -*- coding: utf-8 -*-
# =============================================================================
#
# RUN THIS CODE USING THE FOLLOWING LINE ON CMD
# scrapy crawl articledetails -o details.csv
#
# Approximate crawling time is 16.66 minutes.
# =============================================================================
import time
from selenium import webdriver
import scrapy
from selenium.webdriver.common.by import By

# =============================================================================
# ENVIRONMENTAL SETTINGS
# Chrome Driver used here. Please change the driver path with yours.
# =============================================================================
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=chrome_options)


# Corresponding spider object description to gather details of previously gathered 100 links of the articles.
class ArticleDetails(scrapy.Spider):
    name = 'articledetails'
    allowed_domains = ['www.sciencedirect.com']
    # use output of previous spider as input here
    try:
        with open("links.csv", "rt") as f:
            start_urls = [url.strip() for url in f.readlines()][1:]
    except:
        start_urls = []

    # Headers attribute allows our scraper to pretend it is a real user.
    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        # each url is gathered from response.request object
        driver.get(response.request.url)
        time.sleep(3)
        # Title of the article
        title = driver.find_element(By.XPATH, '//span[@class="title-text"]').text
        # Author name and surname is taken here. Since there are multiple authors in some articles, these are lists of elements
        author_firstname = driver.find_elements(By.XPATH,
            '//*[@class="author size-m workspace-trigger"]//*[@class="text given-name"]')
        author_lastname = driver.find_elements(By.XPATH,
            '//*[@class="author size-m workspace-trigger"]//*[@class="text surname"]')
        # Abstract of the article we have try except here since some of the articles does not have abstract and we set its initial value to none
        abstract = "None"
        try:
            abstract = driver.find_element(By.XPATH, "//div[@class='abstract author']//p").text
        except:
            pass
        # In order to reach the location info a button on the page must be triggered to fire embedded JavaScript code in order to
        # make the page generate a div element that contains location info
        driver.execute_script("document.getElementsByClassName('show-hide-details u-font-sans')[0].click()")
        time.sleep(1)
        # Location is here. Since there are multiple contributing institutions in some articles, this is a list of elements
        location = driver.find_elements(By.XPATH, '//*[contains(@class,"affiliation")]//dd')
        # Empty arrays to be filled with texts stored in each element in the lists gathered above.
        authors_firstname = []
        authors_lastname = []
        authors = []

        # Necessary loops to extract texts from previously gathered lists and to be stored as array of texts.
        for au in author_firstname:
            authors_firstname.append(au.text)

        for au in author_lastname:
            authors_lastname.append(au.text)

        for au in range(len(authors_firstname)):
            authors.append(authors_firstname[au] + " " + authors_lastname[au])

        # Yielding takes place in each location element since we need our data to reflect number of contributions from countries among the world
        for lo in location:
            country = lo.text.split(",")[-1].lstrip()
            yield {
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'location': country
            }






