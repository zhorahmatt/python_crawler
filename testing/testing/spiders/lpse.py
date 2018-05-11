from scrapy.spiders import Spider
from testing.items import LpseItem
from scrapy.http import Request
import urllib2
import json

class Lpse(Spider):
    name = "lpse-crawl"
    allowed_domains = ["lpse.majenekab.go.id"]
    start_urls = ["http://lpse.majenekab.go.id/"]
    
    def parse(self, response):
        crawled_links = []

        #http request, get index tender
        content = urllib2.urlopen("http://lpse.majenekab.go.id/eproc4/dt/lelang").read()
        result = json.loads(content)

        #loop to append link to crawled_links variable
        for record in result["data"]:
            link = "http://lpse.majenekab.go.id/eproc4/lelang/"+record[0]+"/pengumumanlelang"
            crawled_links.append(link)
            yield Request(link, self.parse)

        #crawling process
        nama_lelangs = response.css('tr:nth-child(2) td strong::text').extract()
        kode_lelangs = response.css('tr:nth-child(1) td strong::text').extract()
        nilai_pagu_lelangs = response.css('tr:nth-child(14) td::text').extract()
        for lelang in zip(nama_lelangs, kode_lelangs, nilai_pagu_lelangs):
            item = LpseItem()
            item["nama_lelang"] = lelang[0]
            item["kode_lelang"] = lelang[1]
            item["nilai_pagu_lelang"] = lelang[2]
            yield item
