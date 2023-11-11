import scrapy
import requests
from scrapy_splash import SplashRequest
from data_scrapping.items import DataScrappingItem


class IeeeSpider(scrapy.Spider):
    name = "ieee"
    topic = None
    start_urls = []
    page_no = 1
    r = None
    allowed_domains = ["ieeexplore.ieee.org"]

    handle_httpstatus_list = [302]
    handle_httpstatus_list = [301]

    def __init__(self, keyword=None, topic=None, *args, **kwargs):
        super(IeeeSpider, self).__init__(*args, **kwargs)
        for i in range(50):
            self.start_urls += ['https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=' +
                                topic + '&highlight=true&returnFacets=ALL&returnType=SEARCH&matchPubs=true&pageNumber='
                                + str(i)]
            self.topic = topic

    def parse(self, response):
        for article in response.css("a::attr(href"):
            if '/doi/' in article.extract():
                yield SplashRequest('https://ieeexplore.ieee.org' + article.extract(),
                                    self.parse_article, args={'wait': 3})

    def parse_article(self, response):
        # authors
        authors_name = []
        authors_info = response.css('.author-info__body').css('p::text').extract()
        authors_university = ""
        authors_country = ""

        # articles
        title = response.css('[class^="_ngcontent"][class$="-c163"]').css('::text').extract()
        topic = self.topic
        try:
            doi = response.css('a[href^="https://doi.org/"]')
        except:
            doi = ""
        #date_publication = record["publicationYear"]
        abstract = response.css('div[xplmathjax]::text').extract_first()
        references = ""
        #citation = record["citationCount"]
        downloads = ';'.join(response.css('.tooltip .metric').css('span::text').extract())

        # journal
        publisher = "IEEE"
        issn = "21682372"
        indexation = 24
        impact_factor = 3.825

        length = len(authors_info)
        for i in range(length):
            author = authors_info[i]
            authors_name.append(author['preferredName'])

        item = DataScrappingItem()

        item['authors_name'] = authors_name
        item['authors_university'] = authors_university
        item['authors_country'] = authors_country

        item['title'] = title
        item['topic'] = topic
        item['doi'] = doi
        #try:
            #item['date_publication'] = int(date_publication[0].split(' ')[-1])
        #except:
            #item['date_publication'] = 0
        item['abstract'] = abstract
        item['references'] = references
        #item['citation'] = citation
        item['downloads'] = downloads

        item['publisher'] = publisher
        item['issn'] = issn
        item['indexation'] = indexation
        item['impact_factor'] = impact_factor

        yield item



