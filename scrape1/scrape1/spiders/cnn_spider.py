# CODE IS INSPIRED BY THE FOLLOWING ARTICLE: https://medium.com/codex/scraping-and-analyzing-news-articles-with-scrapy-and-selenium-cbbd94381d78

import scrapy
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class CnnSpider(scrapy.Spider):
  name = 'cnn'
  #allowed_domain = ['https://www.cnn.com/search?q=palestine&sections=politics']
  #start_urls = ['https://www.cnn.com/search?q=palestine&sections=politics']
  allowed_domains = ['www.cnn.com']
  start_urls = ['https://www.cnn.com']


  def __init__(self):
    
    # the driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')  
    chrome_options.add_argument('--disable-dev-shm-usage')  

    driver = webdriver.Chrome(executable_path=str('/usr/local/bin/chromedriver'), options=chrome_options)
    #driver.get("https://www.cnn.com/search?q=palestine&sections=politics")
    driver.get("https://www.cnn.com")

    # begin search
    search_input = driver.find_element_by_id("footer-search-bar") # find the search bar
    search_input.send_keys("palestine") 
    search_btn = driver.find_element_by_xpath("(//button[contains(@class, 'Flex-sc-1')])[2]") # find the search button
    search_btn.click()

    # NEW
    #driver.implicitly_wait(10)
    #wait = WebDriverWait(driver, 10)
    #wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='radio'][value='politics']")))
    # time.sleep(5)
    # driver.find_element(By.CSS_SELECTOR,"input[type='radio'][id='left_politics']").click()

    #driver.find_element_by_css_selector("input[type='radio'][value='politics']").click()

    # record the first page
    self.html = [driver.page_source]

    # start turning pages
    i = 0
    while i < 50: 
      i += 1
      time.sleep(5) # just in case the next button hasn't finished loading
      next_btn = driver.find_element_by_xpath("(//div[contains(@class, 'pagination-arrow')])[2]") # click next button
      next_btn.click()
      self.html.append(driver.page_source) 
    
    driver.close()


  def parse(self, response):
    for page in self.html:
      resp = Selector(text=page)
      results = resp.xpath("//div[@class='cnn-search__result cnn-search__result--article']/div/h3/a")
      # times = resp.xpath("//div[@class='cnn-search__result-publish-date']/span")
      # results = resp.xpath("//div[@class='cnn-search__result cnn-search__result--article']")
      for result in results:
        title = result.xpath(".//text()").get()
        # title = result.xpath(".//div/h3/a/text()").get()
        # time = result.xpath(".//div[@class='cnn-search__result-publish-date']/span/text()").get()
        if ("Video" in title) | ("coronavirus news" in title) | ("http" in title):
            continue # ignore videos and search-independent news or ads
        else:
            link = result.xpath(".//@href").get()[13:] # cut off the domain; had better just use request in fact
            #time = times[i]
            yield response.follow(url=link, callback=self.parse_article, meta={"title": title})#, "time": time})

  def parse_article(self, response):
        title = response.request.meta['title']
        #time = response.request.meta['time']
  
        # two variations of article body's locator
        # content = ' '.join(response.xpath("//section[@id='body-text']/div[@class='l-container']//text()").get())#.getall())
      
        # UNCOMMENT WHEN U UPLOAD
        content = ''.join(response.xpath("//section[@id='body-text']/div[@class='l-container']//text()").getall()[:3])
        #content = ''.join(response.xpath("//section[@id='body-text']/div[@class='l-container']//text()").getall())
        
        if content is None or content is '':
          print("HERE")
            #content = ' '.join(response.xpath("//div[@class='Article__content']//text()").getall())
            #content = response.xpath("//div[@class='article__content']//p//text()[1]").getall()
          content = ''.join(response.xpath("//div[@class='article__content']//p//text()").getall()[:3])
        yield {
            "title": title,
            "u-time": response.xpath("//p[@class='update-time']/text()").get(),
            "content": content
        }

# response.css('p::text').re(r'palestine') you can use an re to get # of instances of a word