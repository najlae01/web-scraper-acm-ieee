BOT_NAME = "data_scrapping"

SPIDER_MODULES = ["data_scrapping.spiders"]
NEWSPIDER_MODULE = "data_scrapping.spiders"

SPLASH_URL = 'localhost:8050'
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

ROBOTSTXT_OBEY = False
MEDIA_ALLOW_REDIRECTS = False
DOWNLOAD_DELAY = 3

SPIDER_MIDDLEWARES = {
   "data_scrapping.middlewares.DataScrappingSpiderMiddleware": 543,
   "scrapy_splash.SplashCookiesMiddleware": 723,
   "scrapy_splash.SplashMiddleware": 725,
}

ITEM_PIPELINES = {
   "data_scrapping.pipelines.DataScrappingPipeline": 300,
}
MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "ScrappedData"
MONGODB_COLLECTION = "articles"
MONGODB_URI = "mongodb://localhost:27017"


# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
