from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
import time
import pandas as pd
import random

#meant to be a one time script to fetch the desired data.
#could be turned into a function but repeated requests will get you blocked and this
#takes a long time to run, so not super useful in that way.

#select desired pages
#page_start = 1
#page_end = 5

#Realtor.com rentals URL
start_url = 'https://www.realtor.com/apartments/Chicago_IL/'

all_listings = []

#set up fake user agent
ua = UserAgent()
options = Options()
options.set_preference("general.useragent.override", ua.random)

#set up a proxy, use firefox history + extensions, reset value of navigator.webdriver
proxy_host_list = ["199.60.103.160","104.19.138.4","104.16.109.207","104.17.248.164","104.23.126.8","104.25.87.42"]
proxy_port = '80'
options.set_preference("network.proxy.type", 1)
proxy_host = random.choice(proxy_host_list)
options.set_preference("network.proxy.http", proxy_host)
options.set_preference("network.proxy.http_port", int(proxy_port))
options.set_preference("dom.webdriver.enabled", False)
options.set_preference('useAutomationExtension', False)
options.set_preference("privacy.trackingprotection.enabled", False)

#firefox driver, make sure it's in path 
driver = webdriver.Firefox(options=options)
#change page size
width = 1920
height = 1080
driver.set_window_size(width,height)

driver.get(start_url)
time.sleep(random.uniform(5, 10))
#set up action chaings for mouse click
actions = ActionChains(driver)

#loop through pages
#for page in range(page_start,page_end+1):
while True:
    try:
        #print(f'Scraping page {page}...')
        print('Scraping page...')
        #url = start_url.format(page)
        #driver.get(url)

        #let page load randomly
        time.sleep(random.uniform(5,15))

        #mouse movement
        #actions.move_by_offset(random.randint(-100,100),random.randint(-100,100)).perform()
        time.sleep(0.5)

        #smooth scrolling
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        for i in range(1,total_height,10):
            driver.execute_script("window.scrollTo(0,{});".format(i))
            time.sleep(random.uniform(0.005,0.02))

        #scrape data
        soup = BeautifulSoup(driver.page_source,'html.parser')
        #filter out the desired listings
        correct_listings = soup.find('section', class_ = 'PropertiesList_propertiesContainer__Vox4I PropertiesList_listViewGrid__bttyS')
        #extract all the useful info
        if correct_listings:
            listings = correct_listings.find_all('div',recursive=False)
            for listing in listings:
                price = listing.find('span', class_ = 'base__StyledType-rui__sc-108xfm0-0 cfGYDq')
                name = listing.find('div', class_ = 'truncate-line',attrs={'data-testid':'card-address-1'})
                address = listing.find('div',class_ = 'truncate-line',attrs={'data-testid':'card-address-2'})
                ul_element = listing.find('ul')
                #have to set dummy variables else there will be incorrect repeating values
                beds = None
                bath = None
                sqft = None
                if ul_element:
                    beds_li = listing.find('li', class_ = 'PropertyBedMetastyles__StyledPropertyBedMeta-rui__a4nnof-0 cHVLag')
                    bath_li = listing.find('li', class_ = 'PropertyBathMetastyles__StyledPropertyBathMeta-rui__sc-67m6bo-0 bSPXLm')
                    sqft_li = listing.find('li', class_ = 'PropertySqftMetastyles__StyledPropertySqftMeta-rui__sc-1gdau7i-0 fnhaOV')
                    if beds_li:
                        beds = beds_li.text.strip()
                    if bath_li:
                        bath = bath_li.text.strip()
                    if sqft_li:
                        sqft_num = listing.find('span',class_ = 'meta-value')
                        if sqft_num:
                            sqft = sqft_num.text.strip()
                #write info to list
                all_listings.append({
                    'Price': price.text.strip() if price else None,
                    'Beds': beds,
                    'Bath': bath,
                    'Sqft': sqft,
                    'Name': name.text.strip() if price else None,
                    'Address': address.text.strip() if price else None
                })
        
        #click the next page button
        next_button = driver.find_element(By.CLASS_NAME,'Next')
        if next_button:
            next_button.click()
        else:
            print("No 'Next' button found. Exiting pagination.")
            break

    except NoSuchElementException:
        print("Reached the last page or 'Next' button not found. Exiting loop.")
        break

    except TimeoutException:
        print("Timeout occurred. Retrying...")
        time.sleep(random.uniform(5, 10))    

#close the webdriver
driver.quit()

#output to dataframe and csv
df = pd.DataFrame(all_listings)
#df.to_csv(f'chicago_apartment_rentals_pages_{page_start}-{page_end}.csv')
df.to_csv(f'chicago_apartment_rentals_pages.csv')
#checks
print('first 50 rows:')
print(df.head(50))
print('last 50 rows:')
print(df.tail(50))
print('Row Counts per Column:')
print(df.count())