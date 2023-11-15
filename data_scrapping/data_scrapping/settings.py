BOT_NAME = "data_scrapping"

SPIDER_MODULES = ["data_scrapping.spiders"]
NEWSPIDER_MODULE = "data_scrapping.spiders"

SPLASH_URL = 'localhost:8050'
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'

ROBOTSTXT_OBEY = False
MEDIA_ALLOW_REDIRECTS = False
DOWNLOAD_DELAY = 10
RANDOMIZE_DOWNLOAD_DELAY = True

REDIRECT_ENABLED = True

ITEM_PIPELINES = {
   "data_scrapping.pipelines.DataScrappingPipeline": 300,
}
MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "ScrappedData"
MONGODB_COLLECTION = "articles"
MONGODB_URI = "mongodb://localhost:27017"
