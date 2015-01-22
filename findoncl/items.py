# -*- coding: utf-8 -*-

from scrapy import Item, Field

class CLItem(Item):
    id = Field()
    title = Field()
    link = Field()
    description = Field()
    images = Field()
    attrs = Field()


class CLAttr(Item):
    id = Field()
    _type = Field(default="cl_attr")
