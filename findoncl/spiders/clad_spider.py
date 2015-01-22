from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request

from findoncl.items import CLItem, CLAttr

class CLAdSpider(CrawlSpider):
    name = "clad"
    allowed_domains = ["washingtondc.craigslist.com"]
    start_urls = [
        "http://washingtondc.craigslist.org/search/cto/"
    ]
     # Not sure why I even bother with rules, this won't work unless I parse the fucking links myself.
#    rules = [Rule(LxmlLinkExtractor(restrict_xpaths='//span[@class="pl"]'), callback='parse_ad', follow=True)]

    # Override parse method from CrawlSpider, this isn't even a crawlspider anymore. thefuck.
    def parse(self, response):
        sel = Selector(response)
        for l in sel.xpath('//div[@class="content"]//p[@class="row"]'):
            yield Request('http://%s%s' % (self.allowed_domains[0], l.xpath('a[@class="i"]/@href')[0].extract()),
                          callback=self.parse_ad, meta={'pid': l.xpath('@data-pid')[0].extract()})

    def parse_ad(self, response):
        sel = Selector(response)
        item = CLItem()
        item['id'] = response.meta['pid']
        item['title'] = sel.xpath('//h2[@class="postingtitle"]/text()').extract()[-1].encode('UTF-8').strip()
        item['link'] = response.url
        item['description'] = map(unicode.strip, sel.xpath('//section[@id="postingbody"]//text()').extract())
        #item['attrs'] = [self.parse_attrs(a) for a in sel.xpath('//p[@class="attrgroup"]//span')]
        item['attrs'] = []
        for a in sel.xpath('//p[@class="attrgroup"][0]//span'):
            akey, aval = self.parse_attrs(a)
            if akey:
                clattr = CLAttr()
                clattr['id'] = akey
                yield clattr
            item['attrs'].append({'key': akey, 'val': aval})
        item['images'] = sel.xpath('//div[@id="thumbs"]//a/@href').extract()
        yield item

    def parse_attrs(self, path):
        print(path)
        attr_key = path.xpath('text()').extract()
        attr_val = path.xpath('b/text()').extract()
        if not attr_key:
            attr_key = [""]
        
        if not attr_val:
            if 'VIN' in attr_key[0]:
                attr_key, attr_val = attr_key[0].split(':')
            else:
                raise ValueError('Unknown attribute without value: %s' % attr_key[0])

        return (attr_key[0].encode('UTF-8').replace(':', "").strip().replace(' ', '_'), attr_val[0].encode('UTF-8').strip())
