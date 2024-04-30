import scrapy
from selenium import webdriver
from scrapy.selector import Selector
from journals.items import JournalsItem
import time
class JournalspiderSpider(scrapy.Spider):
    name = "journalspider"
    start_urls = ['https://journals.plos.org/plosone/search?filterJournals=PLoSONE&q=Hypertension&page=1']

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.page_number = 1
        self.scraped_count = 0  # Custom attribute to keep track of the number of items scraped

    def closed(self, reason):
        self.driver.quit()  # Close the browser when the spider closes

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(5)
        sel = Selector(text=self.driver.page_source)

        alldt = sel.css('dt')
        alldd = sel.css('dd')
        for item,info in zip(alldd,alldt):
            if self.scraped_count == 100:
                break
            self.scraped_count += 1
            journal_item = JournalsItem(
                title=info.css('a::text').get(),
                authors=item.css('p.search-results-authors ::text').get(),
                publish_date=item.css('p span::text').getall()[1],
                journal_name=item.css('p span::text').getall()[2],
                doi=item.css('p a::text').get(),
                citations=item.css("div.search-results-alm a::text")[1].get()
            )

            yield journal_item
        if self.scraped_count < 100:
            self.page_number += 1
            next_url = f'https://journals.plos.org/plosone/search?filterJournals=PLoSONE&q=Hypertension&page={self.page_number}'
            yield response.follow(next_url, callback=self.parse)
