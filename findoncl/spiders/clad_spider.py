import re
import datetime

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request

from findoncl.helpers import absurl
from findoncl.models import CLAd, CLAttr

class CLAdSpider(CrawlSpider):
    name = "clad"
    allowed_domains = ["washingtondc.craigslist.org"]
    start_urls = [
        "http://washingtondc.craigslist.org/search/cto/"
    ]
     # Not sure why I even bother with rules, this won't work unless I parse the fucking links myself.
#    rules = [Rule(LxmlLinkExtractor(restrict_xpaths='//span[@class="pl"]'), callback='parse_ad', follow=True)]

    # Override parse method from CrawlSpider, this isn't even a crawlspider anymore. thefuck.
    def parse(self, response):
        sel = Selector(response)
        #domain =
        for l in sel.xpath('//div[@class="content"]//p[@class="row"]'):
            ad_id = l.xpath('@data-pid')[0].extract()
            ad_title = l.xpath('span[@class="txt"]/span[@class="pl"]/a/text()')[0].extract()
            if CLAd.exists(ad_id):
                continue

            yield Request(absurl(self.allowed_domains[0],
                                 l.xpath('a[@class="i"]/@href')[0].extract()),
                          callback=self.parse_ad, meta={'pid': ad_id,
                                                        'title': ad_title})
        next_page = absurl(self.allowed_domains[0], sel.css('a.next.button').xpath('@href')[0].extract())
        yield Request(next_page, callback=self.parse)

    def parse_ad(self, response):
        sel = Selector(response)
        item = CLAd()
        item['id'] = response.meta['pid']
        item['title'] = response.meta['title']
        item['link'] = response.url
        item['description'] = map(unicode.strip, sel.xpath('//section[@id="postingbody"]//text()').extract())
        item['attrs'] = {}
        for a in sel.xpath('//p[@class="attrgroup"]//span'):
            try:
                akey, aval = self.parse_attrs(a)
            except ValueError:
                continue

            if akey:
                if not CLAttr.exists(akey):
                    clattr = CLAttr()
                    clattr['id'] = akey
                    clattr.save()
            else:
                akey = '_'
            item['attrs'][akey] = aval
        item['images'] = sel.xpath('//div[@id="thumbs"]//a/@href').extract() or sel.xpath('//div[@class="tray"]//img/@src').extract()
        item['posted'] = sel.xpath('//time/@datetime')[0].extract()
        item['updated'] = sel.xpath('//time/@datetime')[-1].extract()
        item['seen'] = datetime.datetime.utcnow()
        title_xtra = sel.xpath('//h2[@class="postingtitle"]/text()').extract()[-1].encode('UTF-8').replace(item['title'], '').replace('-', '').strip()
        if title_xtra:
            d = re.match(r'(\D)?(\d+)', title_xtra)
            if d:
                item['currency'] = d.group(1)
                item['price'] = d.group(2)
        item.save()

    def parse_attrs(self, path):
        attr_key = path.xpath('text()').extract()
        attr_val = path.xpath('b/text()').extract()
        if not attr_key:
            attr_key = [""]

        if not attr_val:
            if 'VIN' in attr_key[0]:
                attr_key, attr_val = attr_key[0].split(':')
            else:
                raise ValueError('Unknown attribute without value: %s' % attr_key[0])

        else:
            attr_key = attr_key[0]
            attr_val = attr_val[0]

        key = attr_key.encode('UTF-8').replace(':', "").strip().replace(' ', '_')
        val = attr_val.encode('UTF-8').strip()

        return (key, val)
