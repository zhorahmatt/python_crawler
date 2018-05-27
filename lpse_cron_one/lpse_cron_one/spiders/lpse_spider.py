import scrapy
import pymongo
from pymongo import MongoClient

class LpseSpider(scrapy.Spider):
    name = "lpse_spider"

    #connect to database mongo
    client = MongoClient('localhost', 27017)

    def start_requests(self):
        
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
