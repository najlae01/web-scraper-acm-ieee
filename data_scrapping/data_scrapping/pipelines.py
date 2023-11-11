import pymongo


class DataScrappingPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        print()
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DB', 'items'),
            mongo_collection=crawler.settings.get('MONGODB_COLLECTION', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.mongo_collection].insert_one(dict(item))
        return item
