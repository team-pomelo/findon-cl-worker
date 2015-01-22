from scrapy.spider import Spider
from scrapy.selector import Selector
from findoncl.items import CLItem

class CLSpider(Spider):
    name = "cl-basic"
    allowed_domains = ["washingtondc.craigslist.org"]
    start_urls = [
        "http://washingtondc.craigslist.org/search/cto/"
    ]

    def parse(self, response):
        responseSelector = Selector(response)
        for sel in responseSelector.css('article#pagecontainer .rightpane .content p.row'):
            item = CLItem()
            item['title'] = sel.css('span.txt span.pl .hdrlnk::text').extract()
            item['link'] = sel.xpath('a/@href').extract()
            yield item
