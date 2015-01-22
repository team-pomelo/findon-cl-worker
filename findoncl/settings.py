# -*- coding: utf-8 -*-

# Scrapy settings for findoncl project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'findoncl'

SPIDER_MODULES = ['findoncl.spiders']
NEWSPIDER_MODULE = 'findoncl.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'findoncl-dev (+http://findon.cl)'

ITEM_PIPELINES = [
  'scrapyelasticsearch.scrapyelasticsearch.ElasticSearchPipeline',
]

ELASTICSEARCH_SERVER = '10.0.3.98' 
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_INDEX = 'cl'
ELASTICSEARCH_TYPE = 'cl_ad'
ELASTICSEARCH_UNIQ_KEY = 'id'
