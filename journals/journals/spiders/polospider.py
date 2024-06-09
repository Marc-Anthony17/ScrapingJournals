import scrapy
from selenium import webdriver
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
# from journals.items import JournalsItem
import time
class polospiderSpider(scrapy.Spider):
    name = "polospider"
    start_urls = ['https://journals.plos.org/plosone/search?filterJournals=PLoSONE&q=south%20africa&page=1']
    
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.page_number = 1
        self.scraped_count = 0 
        self.LIMIT = 4

    def closed(self, reason):
        self.driver.quit() 



    def parse(self, response):
        try:
            self.driver.get(response.url)
            time.sleep(2.5)
            self.clickCookies()
            time.sleep(1)
            sel = Selector(text=self.driver.page_source)

            alldt = sel.css('dt')
            alldd = sel.css('dd')
            for item,info in zip(alldd,alldt):
                if self.scraped_count > self.LIMIT:
                    break
                self.scraped_count += 1
                journal_url = "https://journals.plos.org"+(info.css('a ::attr(href)').get().replace("\n", "").strip())
                journal_item = dict(
                    title=info.css('a::text').get().replace("\n", "").strip(),
                    authors=item.css('p.search-results-authors ::text').get().replace("\n", "").strip(),
                    type=item.css('p span::text').getall()[0].replace("\n", "").strip(),
                    date_published=item.css('p span::text').getall()[1].replace("\n", "").strip(),
                    journal_name=item.css('p span::text').getall()[2].replace("\n", "").strip(),
                    doi=item.css('p a::text').get().replace("\n", "").strip(),
                    number_of_citation=item.css("div.search-results-alm a::text")[1].get().replace("Citations: ", "").replace("\n", "").strip(),
                    url= journal_url
                )
                linkData = self.scrapeUrl(journal_url,journal_item)
                journal_item.update(linkData)

                yield journal_item
        
            if self.scraped_count < self.LIMIT:
                self.page_number += 1
                next_url = f'https://journals.plos.org/plosone/search?filterJournals=PLoSONE&q=south%20africa&page={self.page_number}'
                yield response.follow(next_url, callback=self.parse)
        except:
            self.parse
    def clean(self,text):
        text.replace("\n", "").strip()


    def clickCookies(self):
        try:
            button_xpath = "//div[contains(@class, '_19RPUZBjdy2iuONl+jvOiQ==')]//button[text()='Accept All Cookies']"
            button = self.driver.find_element(By.XPATH, button_xpath)
            button.click()
        except:
            print("no cookies")
############################################################################################################


    def scrapeUrl(self, url,journal_items):
        result = {}
        self.driver.get(url)
        time.sleep(2.5)
        sel = Selector(text=self.driver.page_source)
        REAO = self.extract_REAO(sel)
        detailList = []
        tempDict = {}
        result["author_details"] = {}
        for i,j in zip(journal_items["authors"].split(","),REAO):
            tempDict["author_name"] = i
            tempDict.update(j)
            detailList.append(tempDict)
            tempDict= {}
        result["author_details"] = detailList
        result["abstract_data"] = self.get_abstract_data(sel)
        result["domain"] = "none"
        result["keywords"] ="none"
        result["introduction"] = "Todo"
        result["methods"] = self.get_methods(sel)[0 :20]
        result["conclution"] = "Todo"
        s_files = self.get_SFiles(sel)
        if s_files:
            result["s_files"] = s_files
        else:
            result["s_files"] = "none"
        result["issn"] = "Todo"

        return result
    def get_roles_email_affiliation_orcid(self,person):
        roles = []
        email = []
        affiliations = []
        results = {}
        
        has_roles = False
        has_email = False
        has_affiliation = False
        orcid = ""
        for i in person:
            if "http://orcid" in i:
                orcid = i.strip()
            elif i == 'Roles': 
                has_email  = False
                has_roles = True
                has_affiliation = False
            elif i == '* E-mail:':
                has_email = True
                has_roles = False
                has_affiliation = False
            elif i == 'Affiliation':
                has_email = False
                has_roles = False
                has_affiliation = True
            elif len(i) == 0:
                continue
            elif has_email:
                email.append(i.strip())
            elif has_roles:
                roles.append(i.strip())
            elif has_affiliation:
                affiliations.append(i.strip())
            
            
            
        if email:
            results["email"] = [i.strip() for i in email if len(i)>0][0]
        else:
            results["email"] = "none"
        if affiliations:
            results["affiliations"] = [i.strip() for i in affiliations if len(i)>0][0]
        else:
            results["affiliations"] = "none"
        if roles:
            results["roles"] = [i.replace("\n\n","").replace("   ","") for i in roles if len(i)>0][0]
        else:
            results["roles"] ="none"
        if orcid:
            results["orcid"] = orcid
        else:
            results["orcid"] ="none"
        return results


    def extract_REAO(self,html):
        result = []
        authors_infos = html.css('div.author-info')

        for person in authors_infos:
            result.append(self.get_roles_email_affiliation_orcid(person.css("p ::text").getall()))
        return result


    def is_data_point(self,word):
        listOfWords = ["Data Availability: ","Funding: ","Competing interests: "]
        return word in listOfWords



    def get_abstract_data(self,sel):
        abstract_data = {}
        article_infos = sel.css('div.articleinfo')
        lissa = article_infos.css( '::text').getall()

        copyright_number = 1
        copyright_info =""

        da_num = 1
        da_info=""

        abstract_data["abstract_text"] = sel.css('div.abstract-content').css( 'p ::text').get()
        for i in range(len(lissa)):
            if lissa[i] == 'Citation: ':
                abstract_data["citations"] = lissa[i+1].replace("\n      ","")
            elif lissa[i] == 'Editor: ':
                abstract_data["editor"] = lissa[i+1]
            elif lissa[i] == 'Received: ':
                abstract_data["date_received"] = lissa[i+1]
            elif lissa[i] == 'Accepted: ':
                abstract_data["date_accepted"] = lissa[i+1]
            elif lissa[i] == 'Copyright: ':
                
                while not self.is_data_point(lissa[i+copyright_number]):
                
                    copyright_info = copyright_info + lissa[i+copyright_number]           
                    copyright_number += 1
                
                abstract_data["copyright"] = copyright_info
        
            elif lissa[i] == 'Data Availability: ':

                while not self.is_data_point(lissa[i+da_num]):
                
                    da_info = da_info + lissa[i+da_num]           
                    da_num += 1
                
                abstract_data["data_availability"] = da_info
            elif lissa[i] == 'Funding: ':
                abstract_data["funding"] = lissa[i+1]
            elif lissa[i] == 'Competing interests: ':
                abstract_data["competing_interests"] = lissa[i+1]
                
        return abstract_data

    def get_methods(self, sel):
        data={}
        article_infos = sel.css('div#section2 ::text').getall()
        result = ' '.join((i.strip())for i in article_infos)
        data["method_text"] = result
        return result

    def get_SFiles(self,sel):
        result = {}
        article_infos = sel.css('div.supplementary-material')
        for info in article_infos:
            s_type = info.css("h3 ::text").get()
            result[s_type]= {}

            file_link = "https://journals.plos.org/plosone/" +info.css("a ::attr(href)").getall()[0]
            if "#" not in info.css("a ::attr(href)").getall()[1]:
                doi = info.css("a ::attr(href)").getall()[1]
                
            else:
                doi = "None"
            file_title = ""
            file_title_text = info.css("p ::text").getall()
            doctype = info.css("p.postSiDOI ::text").get()
            
            for i in file_title_text:
                if "doi.org" in i:
                    break
                file_title = file_title + i
            only_title = file_title.split(".")[0]
            
            only_info = "".join(file_title.split(".")[1:]).strip()
            result[s_type]["sfile_title"]= only_title
            if only_info:
                result[s_type]["sfile_text"] = only_info
            else:
                result[s_type]["sfile_text"] = "none"
            result[s_type]["sfile_doctype"] = doctype
            result[s_type]["sfile_url"] = file_link
            result[s_type]["sfile_doi"] = doi 
            
        return result
