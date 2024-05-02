# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JournalsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    title = scrapy.Field()
    authors = scrapy.Field()
    publish_date = scrapy.Field()
    journal_name = scrapy.Field()
    doi = scrapy.Field()
    citations = scrapy.Field()

        
