import scrapy


class DataScrappingItem(scrapy.Item):

    # authors
    authors_name = scrapy.Field()
    authors_university = scrapy.Field()
    authors_country = scrapy.Field()

    # articles
    title = scrapy.Field()
    topic = scrapy.Field()
    doi = scrapy.Field()
    date_publication = scrapy.Field()
    abstract = scrapy.Field()
    references = scrapy.Field()
    citation = scrapy.Field()
    downloads = scrapy.Field()

    # journal
    publisher = scrapy.Field()
    issn = scrapy.Field()
    indexation = scrapy.Field()
    impact_factor = scrapy.Field()

    pass
