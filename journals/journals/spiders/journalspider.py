import scrapy


class JournalspiderSpider(scrapy.Spider):
    name = "journalspider"
    allowed_domains = ["journals.plos.org"]
    start_urls = ["https://journals.plos.org/plosone/search?filterJournals=PLoSONE&q=Hypertension&page=1"]

    def parse(self, response):
        pass
