import scrapy
from selenium import webdriver
from scrapy.selector import Selector
# from journals.items import JournalsItem
import time
class JournalspiderSpider(scrapy.Spider):
    name = "journalspider"
    start_urls = ['https://journals.plos.org/plosone/search?filterJournals=PLoSONE&q=Hypertension&page=1']
    
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.page_number = 1
        self.scraped_count = 0 
        self.LIMIT = 5

    def closed(self, reason):
        self.driver.quit() 

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(5)
        sel = Selector(text=self.driver.page_source)

        alldt = sel.css('dt')
        alldd = sel.css('dd')
        for item,info in zip(alldd,alldt):
            if self.scraped_count == self.LIMIT:
                break
            self.scraped_count += 1
            journal_item = dict(
                title=info.css('a::text').get().replace("\n", "").strip(),
                authors=item.css('p.search-results-authors ::text').get().replace("\n", "").strip(),
                publish_date=item.css('p span::text').getall()[1].replace("\n", "").strip(),
                journal_name=item.css('p span::text').getall()[2].replace("\n", "").strip(),
                doi=item.css('p a::text').get().replace("\n", "").strip(),
                citations=item.css("div.search-results-alm a::text")[1].get().replace("Citations: ", "").replace("\n", "").strip()
            )

            yield journal_item
       
        if self.scraped_count < self.LIMIT:
            self.page_number += 1
            next_url = f'https://journals.plos.org/plosone/search?filterJournals=PLoSONE&q=Hypertension&page={self.page_number}'
            yield response.follow(next_url, callback=self.parse)
    def clean(self,text):
        text.replace("\n", "").strip()


############################################################################################################
