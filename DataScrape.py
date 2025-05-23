from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import time
import pandas as pd
import random

#meant to be a one time script to fetch the desired data.
#could be turned into a function but repeated requests will get you blocked and this
#takes a long time to run, so not super useful in that way.
#running this with too many pages will cause a memory crash, I like to do intervals of 50. 

#select desired pages
page_start = 150
page_end = 200

#Realtor.com rentals URL
start_url = f'https://www.realtor.com/apartments/Chicago_IL/pg-{page_start}/'

all_listings = []

#set up fake user agent
ua = UserAgent()
options = Options()
options.set_preference("general.useragent.override", ua.random)

#set up a proxy, and choose from a list to evade blocking 
proxy_host_list = ["199.60.103.160","104.19.138.4","104.16.109.207","104.17.248.164","104.23.126.8","104.25.87.42"]
proxy_port = '80'
options.set_preference("network.proxy.type", 1)
proxy_host = random.choice(proxy_host_list)
options.set_preference("network.proxy.http", proxy_host)
options.set_preference("network.proxy.http_port", int(proxy_port))
#use firefox history + extensions, reset value of navigator.webdriver, disable tracking protection
options.set_preference("dom.webdriver.enabled", False)
options.set_preference('useAutomationExtension', False)
options.set_preference("privacy.trackingprotection.enabled", False)

#setupfirefox driver, make sure it's in path 
driver = webdriver.Firefox(options=options)
#change page size
width = 1920
height = 1080
driver.set_window_size(width,height)
#load page
driver.get(start_url)
time.sleep(random.uniform(5, 10))

#set up action chaings for mouse click
actions = ActionChains(driver)

#loop through pages
for page in range(page_start,page_end+1):
    try:
        print(f'Scraping page {page}...')

        #let page load randomly
        time.sleep(random.uniform(5,15))

        #mouse movement
        #actions.move_by_offset(random.randint(-100,100),random.randint(-100,100)).perform()
        #time.sleep(0.5)

        #smooth scrolling
        total_height = int(driver.execute_script("return document.body.scrollHeight"))
        for i in range(1,total_height,10):
            driver.execute_script("window.scrollTo(0,{});".format(i))
            time.sleep(random.uniform(0.005,0.02))

        #scrape data
        soup = BeautifulSoup(driver.page_source,'html.parser')
        #filter out the desired listings
        #correct_listings = soup.find('section', class_ = 'PropertiesList_propertiesContainer__Vox4I PropertiesList_listViewGrid__bttyS')
        correct_listings = soup.find('section', class_ = 'PropertiesList_propertiesContainer__HTNbx PropertiesList_listViewGrid__U_BlK') #this gets changed every so often
        #extract all the useful info
        if correct_listings:
            listings = correct_listings.find_all('div',recursive=False)
            for listing in listings:
                price = listing.find('span', class_ = 'base__StyledType-rui__sc-108xfm0-0 cfGYDq')
                rent_type = listing.find('div', class_ = 'base__StyledType-rui__sc-108xfm0-0 cWxXjc message')
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
                    'Type': rent_type.text.strip() if price else None,
                    'Name': name.text.strip() if name else None,
                    'Address': address.text.strip() if address else None,
                    'Page': page
                })
        
        #click the next page button
        next_button = WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.LINK_TEXT, "Next")))
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
df.to_csv(f'chicago_apartment_rentals_pages_{page_start}-{page_end}.csv')
#checks
print('first 50 rows:')
print(df.head(10))
print('last 50 rows:')
print(df.tail(10))
print('Row Counts per Column:')
print(df.count())
print('Found Listings Per page:')
print(df["Price"].count()/(page_end-page_start))