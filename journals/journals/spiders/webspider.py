
import pickle
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from scrapy.selector import Selector
# from journals.items import JournalsItem
import time
class WebspiderSpider(scrapy.Spider):
    name = "webspider"
    allowed_domains = ["webofscience.com"]
    start_urls = ['https://www.webofscience.com/wos/author/search']

    
    def __init__(self):
        cookies = pickle.load(open("cookies.pkl", "rb"))
        self.driver = webdriver.Chrome()
        self.page_number = 1
        self.scraped_count = 0 
        self.results = {"search_results":[]}
        self.driver.implicitly_wait(13)
        self.url_debug = 0
       
    
    def closed(self, reason):
        print(self.url_debug)
        done = pickle.load(open("author_relevance.pkl", "rb"))
        print(f"_________________________________________________________________________________number of dictionaries:{len(done)}")
        print(f"_________________________________________________________________________________nuber of url:{self.url_debug}")

        self.driver.quit() 

    def parse(self, response):
        self.driver.get(response.url)
        self.click_cookies(self.driver)
        time.sleep(5)
        # self.sign_in(self.driver)
        # self.search_name_org(self.driver)
        # self.all_html(self.driver)
        # self.results["search_results"].append({"author_page" : {"url":"https://www.webofscience.com/wos/author/record/53843916"}})
        self.layer_two(self.driver)
        # self.lastLayer(self.driver,"https://www.webofscience.com/wos/woscc/full-record/WOS:000943850100001")
    

        yield self.results
    
    def clean(self,text):
        text.replace("\n", "").strip()
    
    def click_cookies(self, driver):
        time.sleep(2)
        try:
            cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            cookie_button.click()
        except:
            print("no button to press")
    
    def search_name_org(self,driver):
        name_drop_down = driver.find_element(By.CLASS_NAME, "dropdown")
        name_drop_down.click()
        # time.sleep(1)
        organisation1 = driver.find_elements(By.CSS_SELECTOR, ".wrap-mode.ng-star-inserted")[2]
        actions = ActionChains(driver)
        actions.move_to_element(organisation1).perform()
        organisation2 = driver.find_element(By.CSS_SELECTOR, ".wrap-mode.ng-star-inserted.active")
        organisation2.click()
        # time.sleep(1)
        driver.find_element(By.ID, "mat-radio-4").click()
        search_bar = driver.find_element(By.ID, "org-search")
        search_bar.send_keys("University of Witwatersrand")
        try:
            driver.find_element(By.CSS_SELECTOR , ".bb-button._pendo-button-secondaryButton._pendo-button").click()
        except:
            print("no notification popped up")
        time.sleep(1)

        driver.find_element(By.CSS_SELECTOR,".mat-focus-indicator.search.wat-search-button.mat-flat-button.mat-button-base.mat-primary").click()
        # time.sleep(10)

## check
    def useful(self,driver):
        return driver.find_element(By.CSS_SELECTOR, ".end-page.ng-star-inserted").text
    
    def sign_in(self,driver):
        driver.find_element(By.CSS_SELECTOR, ".mat-focus-indicator.mat-button.mat-button-base.mat-primary.sign-in.ng-star-inserted").click()
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR,".mat-focus-indicator.mat-menu-user.mat-menu-item.ng-star-inserted").click()
        time.sleep(5)
        email = driver.find_element(By.ID,"mat-input-0")
        password = driver.find_element(By.ID, "mat-input-1")
        email.send_keys("marcanthonyjones17@gmail.com")
        password.send_keys("Hellofriend1!")
        driver.find_element(By.CSS_SELECTOR, ".mat-focus-indicator.wui-btn--login.mat-flat-button.mat-button-base.mat-primary").click() 
        time.sleep(25)
       
    def checkPoint(self,number):
        pickle.dump(self.results, open(f"save_point{number}.pkl","wb"))
    

    def all_html(self , driver):
        
        list_of_pages = []
        time.sleep(25)
        total_pages = int(self.useful(driver))
        driver.find_elements(By.CSS_SELECTOR,".mat-focus-indicator.wat-more-authors.mat-button.mat-button-base.ng-star-inserted")
        time.sleep(4)
        # self.click_more_buttons(driver.find_elements(By.CSS_SELECTOR,".mat-focus-indicator.wat-more-authors.mat-button.mat-button-base.ng-star-inserted"))
        # list_of_pages.append(Selector(text=driver.page_source))
        # self.layer_one(Selector(text=driver.page_source))

        # total_pages = 3
        
        # ended at 270

        for i in range(401, total_pages+1):
            print(f" +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ {total_pages}")
            driver.get(f"https://www.webofscience.com/wos/author/results/1/relevance/{i}")
            time.sleep(20)
            
            buttons = driver.find_elements(By.CSS_SELECTOR,".mat-focus-indicator.wat-more-authors.mat-button.mat-button-base.ng-star-inserted")
            self.click_more_buttons(buttons)
            time.sleep(2)
            self.layer_one(Selector(text=driver.page_source))
            try:
                driver.find_element(By.CSS_SELECTOR , ".bb-button._pendo-button-secondaryButton._pendo-button").click()
            except:
                print("no notification popped up")
            # if i == 406:
            #     self.checkPoint(i)
        return list_of_pages
    
    def click_more_buttons(self, buttons):
       
        for button in buttons:
            button.click()
                
    
    def layer_one(self , page):
        first_json = {}
        #############Save point
        all_divs = page.css("app-author-search-result-card.ng-star-inserted")
        # div = all_divs[0]
        for div in all_divs:
            first_json["name"] = div.css("span.ng-star-inserted ::text").get()
            first_json["institiution"] = div.css("p ::text").getall()[0]
            first_json["location"] = div.css("p ::text").getall()[-1]
            first_json["researcher_id"] = div.css("div.wat-rid.ng-star-inserted::text").get()
            name_container = div.css("div.wat-published-names.ng-star-inserted")
            
            first_json["published_names"] = name_container.css("span.mr-10px.ng-star-inserted ::text").getall()
            first_json["URL"] = "https://www.webofscience.com"+div.css("a ::attr(href)").get()
            first_json["author_page"] = {"url":"https://www.webofscience.com"+div.css("a ::attr(href)").get()}
            self.results["search_results"].append(first_json)
            first_json = {}
        

  
  
    def layer_two(self, driver):
        relevance_results = pickle.load(open("relavent_results.pkl", "rb"))["search_results"]
        new_data = []
        reference = len(pickle.load(open("author_relevance.pkl", "rb")))-1
        dictionary1 = {}

        for index, dictionary in enumerate(relevance_results): 
            if index <= reference:
                continue
            # if "published_names" in dictionary["author_page"]["published_names"]:
            #     continue
            url = dictionary["author_page"]["url"]
            driver.get(url)
            
            buttons = driver.find_elements(By.CSS_SELECTOR,".mat-focus-indicator.display-data-button.mat-button.mat-button-base.ng-star-inserted")
            if buttons:
                self.click_more_buttons(buttons)
            
            time.sleep(9)
            
            html = Selector(text= driver.page_source)
            published_names = []
            published_organizations = []
            subject_categories = []

            published_data = html.css("app-display-data ::text").getall()
            
            has_names = False
            has_org = False
            has_subject = False
            for i in published_data:
                if i == ' Published names ': 
                    has_org = False
                    has_names = True
                    has_subject = False
                elif i == ' Published Organizations ':
                    has_org = True
                    has_names = False
                    has_subject = False
                elif i == ' Subject Categories ':
                    has_org = False
                    has_names = False
                    has_subject = True
                elif i == 'BETA':
                    continue
                elif has_names:
                    published_names.append(i)
                elif has_org:
                    published_organizations.append(i)
                elif has_subject:
                    subject_categories.append(i)                


            


            # published_organizations = html.css("span.display-data-value")[1].css(" ::text").getall()
            # subject_categories = html.css("span.display-data-value")[2].css(" ::text").getall()
            ####### profile_summary_metrics
            
            total_documents = html.css("span.summary-count")[0].css(" ::text").get()
            Publications_indexed_in_Web_of_Science = html.css("span.summary-count")[1].css(" ::text").get() 
            web_of_science_core_collection_publications = html.css("span.summary-count")[2].css(" ::text").get() 
            preprints = html.css("span.summary-count")[3].css(" ::text").get() 
            dissertations_or_theses = html.css("span.summary-count")[4].css(" ::text").get() 
            non_indexed_publications = html.css("span.summary-count")[5].css(" ::text").get() 
            verified_peer_reviews = html.css("span.summary-count")[6].css(" ::text").get() 
            verified_editor_records = html.css("span.summary-count")[7].css(" ::text").get() 

            ###### wos matrix
            total_publications = html.css("div.wat-author-metric-inline-block.wat-author-metric-inline-block")[1].css(" ::text").get()
            Sum_of_Times_Cited = self.toInt(html.css("div.wat-author-metric-inline-block.wat-author-metric-inline-block")[2].css(" ::text").get())
            Citing_Articles = self.toInt(html.css("div.wat-author-metric-inline-block.wat-author-metric-inline-block")[3].css(" ::text").get())
            Sum_of_Times_Cited_by_Patents = self.toInt(html.css("div.wat-author-metric-inline-block.wat-author-metric-inline-block")[4].css(" ::text").get())
            Citing_Patents = self.toInt(html.css("div.wat-author-metric-inline-block.wat-author-metric-inline-block")[4].css(" ::text").get())
            total_citations = Sum_of_Times_Cited + Citing_Articles + Sum_of_Times_Cited_by_Patents + Citing_Patents
            h_index = html.css("div.wat-author-metric-inline-block.wat-author-metric-inline-block")[0].css(" ::text").get()


            ######## publications 
            publications_dictionaries = []
            urls_to_visit = []
            current_section = 1
            max_num = self.toInt(html.css("span.end-page.ng-star-inserted ::text").get())
            
            while current_section <= max_num:
                # time.sleep(13)
                # if current_section > 35:
                #     time.sleep(2)
                #     current_section += 1

                #     driver.find_element(By.CSS_SELECTOR, 'button[cdxanalyticscategory="wos_navigation_next_page"]').click()
                #     continue
                time.sleep(4)
                driver.find_element(By.CSS_SELECTOR, 'app-publication-card.ng-star-inserted')
                html = Selector(text= driver.page_source)
                for i in self.get_publications_urls(html):
                    urls_to_visit.append(i)
                current_section += 1
                driver.find_element(By.CSS_SELECTOR, 'button[cdxanalyticscategory="wos_navigation_next_page"]').click()

    

            for url in urls_to_visit:
                print(f"_________________________________________________________________________________current url: {url}")
                # self.url_debug.append(url)
                publications_dictionaries.append(self.lastLayer(driver,url))
            
            if published_names:
                dictionary1["published_names"] = published_names
            if published_organizations:
                dictionary["published_organizations"] = published_organizations
            if subject_categories:
                dictionary["subject_categories"] = subject_categories

            # profile_summary_metrics
            dictionary1["profile_summary_metrics"]= {}
            dictionary1["profile_summary_metrics"]["total_documents"] = total_documents
            dictionary1["profile_summary_metrics"]["publications_indexed_in_Web_of_Science"] = Publications_indexed_in_Web_of_Science
            dictionary1["profile_summary_metrics"]["wos_core_collection_publications"] = web_of_science_core_collection_publications
            dictionary1["profile_summary_metrics"]["preprints"] = preprints
            dictionary1["profile_summary_metrics"]["dissertations_or_theses"] = dissertations_or_theses
            dictionary1["profile_summary_metrics"]["non_indexed_publications"] = non_indexed_publications
            dictionary1["profile_summary_metrics"]["verified_peer_reviews"] = verified_peer_reviews
            dictionary1["profile_summary_metrics"]["verified_editor_records"] = verified_editor_records

            # wos_core_collection_metrics
            dictionary1["wos_core_collection_metrics"] ={}
            dictionary1["wos_core_collection_metrics"]["total_publications"] = total_publications
            dictionary1["wos_core_collection_metrics"]["total_citations"] = total_citations
            dictionary1["wos_core_collection_metrics"]["h_index"] = h_index

            # publications
            dictionary1["publications"] = publications_dictionaries

            time.sleep(5)
            new_data.append(dictionary1)
            dictionary1={}
            pickle.dump(new_data, open(f"author_relevance2.pkl","wb"))

            
    
    def lastLayer(self,driver,url):
        self.url_debug +=1

        return {"url" : url}
        
        
        # try:
        #     driver.get(url)
        #     driver.find_element(By.CSS_SELECTOR,".mat-focus-indicator.mat-tooltip-trigger.no-left-padding.mat-button.mat-button-base.mat-primary.ng-star-inserted").click()
        #     html = Selector(text= driver.page_source)
        #     title = html.css("h2.title.text--large.cdx-title ::text").get()
        #     source =  html.css("a.mat-focus-indicator.mat-tooltip-trigger.font-size-14.summary-source-title-link.remove-space.no-left-padding.mat-button.mat-button-base.mat-primary.ng-star-inserted ::text").get()
        #     author_id = self.get_author_identifiers(html)
        #     try:
        #         published_year = html.css('span[name="pubdate"] ::text').get()[-4:]
        #     except:
        #         published_year = "none"
        #     document_type = html.css('span#FullRTa-doctype-0 ::text').get()
        #     accession_number = url[-19:]
        #     # issn = html.css("div.journal-content-row.margin-top-5.cdx-two-column-grid-container.ng-star-inserted span.value.cdx-grid-data ::text").get()
        #     items_list = html.css("div.journal-content-row.cdx-two-column-grid-container.ng-star-inserted ::text").getall()
        #     ids_nunmber = html.css("span#HiddenSecTa-recordIds ::text").getall()
        #     # print(f"==================================================================={items_list2}===============================================================================================")

        #     export = {
        #         "url" : url,
        #         "title" : title,
        #         "source" : source,
        #         "author_identifiers" : author_id,
        #         "published_year" : published_year,
        #         "document_type" : document_type,
        #         "accession_number" : accession_number,
                
        #     }
            
        #     if items_list[0] == 'ISSN':
        #         export["issn"] = items_list[1]
        #     if items_list[0] == 'eISSN':
        #         export["eissn"] = items_list[1]
        #     if items_list[2] == 'eISSN':
        #         export["eissn"] = items_list[3]
        #     if ids_nunmber:
        #         export["ids_nunmber"] = ids_nunmber[0]
        #     if published_year == "none":
        #         export.pop("published_year")
        #     return export
        # except:
        #     self.lastLayer(self,driver,url)


    def get_author_identifiers(self,html):
        table = html.css("table")[0].css("tbody tr")
        author_identifiers = []
        temp_container = {}
        for i in table:
            td_list = i.css("td ::text").getall()
            temp_container["name"] = td_list[0]
            temp_container["researcher_id"] = td_list[1]
            
            if len(td_list) == 4:
                temp_container["orcid"] = td_list[2]
            author_identifiers.append(temp_container)
            temp_container = {}
        return author_identifiers


    def get_publications_urls(self,html):
        url_list = []
        publication_cards = html.css('app-publication-card')
        incomplete_list = publication_cards.css('a[cdxanalyticsaction="click"][cdxanalyticscategory="WOS-authorrecord-publication"]::attr(href)').getall()

        for url in incomplete_list:
            url_list.append("https://www.webofscience.com"+url)
        return url_list 
    

    def toInt(self,string):
        string = string.replace(",","").strip()
        return int(string)