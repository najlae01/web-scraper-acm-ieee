import scrapy
from scrapy_splash import SplashRequest
from ..items import DataScrappingItem


class AcmSpider(scrapy.Spider):
    name = "acm"
    topic = None
    allowed_domains = ["dl.acm.org"]
    start_urls = []

    handle_httpstatus_list = [302]
    handle_httpstatus_list = [301]

    def __init__(self, keyword=None, topic=None, *args, **kwargs):
        super(AcmSpider, self).__init__(*args, **kwargs)
        for i in range(50):
            self.start_urls += ['https://dl.acm.org/action/doSearch?AllField=' +
                                topic + '&startPage=' + str(i) + '&pageSize=' +
                                str(20)]
            self.topic = topic

    def parse(self, response):
        for article in response.css("a::attr(href)"):
            if '/doi/' in article.extract():
                yield SplashRequest('https://dl.acm.org' + article.extract(),
                                    self.parse_article, args={'wait': 3})

    def parse_article(self, response):
        item = DataScrappingItem()

        # authors
        authors_name = response.css('.author-data').css('span::text').extract()
        authors_info = response.css('.author-info__body').css('p::text').extract()
        authors_university = []
        authors_country = []

        # articles
        title = response.css('.citation__title::text').extract_first()
        topic = self.topic
        doi = response.css('.issue-item__doi::text').extract()
        date_publication = response.css('.CitationCoverDate::text').extract()
        abstract = response.css('.abstractSection').css('p::text').extract()
        references = response.css('.references__note::text').extract()
        citation = ';'.join(response.css('.tooltip .citation').css('span::text').extract())
        downloads = ';'.join(response.css('.tooltip .metric').css('span::text').extract())

        # journal
        publisher = "ACM"
        issn = "00045411, 1557735X"
        indexation = 134
        impact_factor = 6.738

        if len(authors_info) != 0:
            for author_info in authors_info:
                if author_info != "":
                    string = author_info.split(',')
                    authors_university.append(string[0])

                    if len(string) > 1:
                        authors_country.append(string[len(string) - 1])
                    else:
                        authors_country = ""
                else:
                    authors_university = ""
                    authors_country = ""

        authors_country = ";".join(authors_country)

        item['authors_name'] = authors_name
        item['authors_university'] = authors_university
        item['authors_country'] = authors_country

        item['title'] = title
        item['topic'] = topic
        item['doi'] = doi
        try:
            item['date_publication'] = int(date_publication[0].split(' ')[-1])
        except:
            item['date_publication'] = 0
        item['abstract'] = abstract
        item['references'] = references
        item['citation'] = int(''.join(citation).split(';')[0].replace(',', ''))
        item['downloads'] = int(''.join(downloads).split(';')[0].replace(',', ''))

        item['publisher'] = publisher
        item['issn'] = issn
        item['indexation'] = indexation
        item['impact_factor'] = impact_factor

        yield item

