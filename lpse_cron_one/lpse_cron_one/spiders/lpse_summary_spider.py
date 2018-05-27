import scrapy
import pymongo
from pymongo import MongoClient
from scrapy.spider import Spider
from scrapy.http import Request

class LpseSpider(scrapy.Spider):
    name = "lpse_spider"

    #connect to database mongo
    client = MongoClient('localhost', 27017)
    
    #set database used
    db = client.eproc_research
    
    #set collections
    mongo_lpse_url_list = db.eproc_url_lists
    mongo_lpse_summaries = db.eproc_summaries_tender

    def start_requests(self, mongo_lpse_url_list):
        urls = []

        for url in mongo_lpse_url_list:
            link_summary = url+"eproc4/dt/lelang"
            urls.append(link_summary)
            yield Request(link_summary, self.parse)
        
    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
