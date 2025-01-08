from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

#Realtor.com rentals URL
url = 'https://www.realtor.com/apartments/Chicago_IL/pg-1'
#set up selenium to load all of the listings

#firefox driver 
driver = webdriver.Firefox()
driver.get(url)

all_listings = []

#let page load
time.sleep(5)

#smooth scrolling
total_height = int(driver.execute_script("return document.body.scrollHeight"))
for i in range(1,total_height,5):
    driver.execute_script("window.scrollTo(0,{});".format(i))
    time.sleep(0.01)

#scrape data over multiple pages
soup = BeautifulSoup(driver.page_source,'html.parser')
#filter out the desired listings
correct_listings = soup.find('section', class_ = 'PropertiesList_propertiesContainer__Vox4I PropertiesList_listViewGrid__bttyS')
#extract all the useful info
if correct_listings:
    listings = correct_listings.find_all('div',recursive=False)
    for listing in listings:
        price = listing.find('span', class_ = 'base__StyledType-rui__sc-108xfm0-0 cfGYDq')
        ul_element = listing.find('ul')
        beds = None
        if ul_element:
            beds_li = listing.find('li', class_ = 'PropertyBedMetastyles__StyledPropertyBedMeta-rui__a4nnof-0 cHVLag')
            if beds_li:
                beds = beds_li.text.strip()
        all_listings.append({
            'Price': price.text.strip() if price else None,
            'Beds': beds
            })

driver.quit()

#output
df = pd.DataFrame(all_listings)
print(df.head(50))