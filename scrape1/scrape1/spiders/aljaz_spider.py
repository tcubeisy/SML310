import scrapy
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json


class AlJazSpider(scrapy.Spider):
  name = 'aljaz'
  allowed_domain = ['https://www.aljazeera.com/where/palestine/']
  start_urls = ['https://www.aljazeera.com/where/palestine/']

  def __init__(self):
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=str('/usr/local/bin/chromedriver'), options=chrome_options)
    driver.get("https://www.aljazeera.com/where/palestine/")

    i = 0
    while i < 50:
      i += 1
      time.sleep(5)
      next_btn = driver.find_element_by_xpath("//button[@class=('show-more-button big-margin')]")
      driver.execute_script("arguments[0].click();", next_btn)
    
    print("button loaded")
    self.html = [driver.page_source]
    driver.close() 

  def parse(self, response):

    for page in self.html:
      resp = Selector(text=page)
      results = resp.xpath("//a[@class=('u-clickable-card__link')]")
      for result in results:
        link = result.xpath(".//@href").get()
        print("link: " + str(link)) # cut off the domain; had better just use request in fact
        yield response.follow(url=link, callback=self.parse_article)

  def parse_article(self, response):
    title = response.xpath("//h1").extract()
    time = response.xpath("//div[contains(@class,'date-simple css-1yjq2zp')]//span[@class='screen-reader-text']/text()").extract()
    content = response.xpath("//main[contains(@id,'main-content-area')]//p/text()").get()
    yield {
      "title": title,
      "time": time,
      "content": content
    }
# response.css('p::text').re(r'palestine') you can use an re to get # of instances of a word