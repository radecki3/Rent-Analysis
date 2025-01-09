from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
import time
import pandas as pd
import random

#meant to be a one time script to fetch the desired data.
#could be turned into a function but repeated requests will get you blocked and this
#takes a long time to run, so not super useful in that way.

#select desired pages
page_start = 1
page_end = 10

#Realtor.com rentals URL
start_url = 'https://www.realtor.com/apartments/Chicago_IL/pg-{}'

all_listings = []

#loop through pages
for page in range(page_start,page_end+1):
    print(f'Scraping page {page}...')

    #set up fake user agent
    ua = UserAgent()
    options = Options()
    options.set_preference("general.useragent.override", ua.random)

    #set up a proxy, use firefox history + extensions, reset value of navigator.webdriver
    #mostly obtained from https://stackoverflow.com/questions/58873022/how-can-i-make-a-selenium-script-undetectable-using-geckodriver-and-firefox-thro
    #profile = webdriver.FirefoxProfile("C:\\Users\\Martin\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\pwyu1bkp.default-release")
    proxy_host = "199.60.103.160"
    proxy_port = '80'
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.http", proxy_host)
    options.set_preference("network.proxy.http_port", int(proxy_port))
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)
    #profile.update_preferences()
    #capabilities = webdriver.DesiredCapabilities.FIREFOX

    #firefox driver, make sure it's in path 
    driver = webdriver.Firefox(options=options)
    #change page size
    width = 2560
    height = 1440
    driver.set_window_size(width,height)

    #set up action chaings for mouse click
    actions = ActionChains(driver)
    url = start_url.format(page)
    driver.get(url)

    #let page load randomly
    time.sleep(random.uniform(5,15))

    #mouse movement
    actions.move_by_offset(100,100).perform()
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

    #close the webdriver
    driver.quit()

    #random delay
    time.sleep(random.uniform(5,10))

#output to dataframe and csv
df = pd.DataFrame(all_listings)
df.to_csv(f'chicago_apartment_rentals_pages_{page_start}-{page_end}.csv')

#checks
print('first 50 rows:')
print(df.head(50))
print('last 50 rows:')
print(df.tail(50))
print('Row Counts per Column:')
print(df.count())