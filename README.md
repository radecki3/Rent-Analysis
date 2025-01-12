# Purpose 

The Purpose of this project is to analyze aparment rental data from the top 10 most populated U.S. cities and determine patterns within factors such as price, square footage, neighborhood, and number of beds and baths, within each city.

I also aim to compare the cities' overall statistics against each other to hopefully return some valuable insight about the nature of apartment rentals in major U.S. cities.

# Methods

The data is gathered from popular realtor site, Realtor.com, which hosts apartment listings similar to Zillow or Apartments.com. 

I obtain data via webscraping in Python, which is the DataScrape.py file. 
*Note: this is a script and is not necessarily meant to be implemented in any wider or regular use cases. It is simply meant to serve as a one-time use for myself to gather the required data. As such, some of the code is inefficient and, in fact, purposefully omits some data-cleaning-esque steps in an effort to perform these with SQL instead. Furthurmore, the class names and general HTML structure utilized for the scraping procedure will vary widely from website to website, and can even change within a particular website from day-to-day or week-to-week.*