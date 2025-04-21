# Purpose 

The Purpose of this project is to analyze aparment rental data from the top 10 most populated U.S. cities and determine patterns within factors such as price, square footage, neighborhood, and number of beds and baths, within each city.

I also aim to compare the cities' overall statistics against each other to hopefully return some valuable insight about the nature of apartment rentals in major U.S. cities.

# Methods and Data

The data is gathered from popular realtor site, Realtor.com, which hosts apartment listings similar to Zillow or Apartments.com. 

![Image](https://github.com/user-attachments/assets/0c7306d3-e79e-45c6-a8e3-22dcba7cb9e6)

I obtain data via webscraping in Python by examining the html structure of Realtor.com and locating relevant information, which is the DataScrape.py file within this repo. 

![Image](https://github.com/user-attachments/assets/d32d9c25-7e05-4ad2-91bc-338b25494dd5)

![Image](https://github.com/user-attachments/assets/74269632-ccf3-42b4-8808-1954193f5456)

![Image](https://github.com/user-attachments/assets/6432b6cd-d35e-473d-8491-766d425fb2d9)

Webscraping is a gray area, however, all data used is very easily accessible public data, and is not limited to only one website, so I feel that this is a fair use case. 

*Note: Some of the code purposefully omits some data-cleaning-esque steps in an effort to perform these with SQL instead. Furthurmore, the class names and general HTML structure utilized for the scraping procedure will vary widely from website to website, and can even change within a particular website from day-to-day or week-to-week.*

The data amounts to ~ 5000-10000 listings per city as I scrape only the first 200 pages, or less, of listings - around where realtor.com stops loading more pages. The smaller the city, the fewer rentals there are, naturally. 

Based on available online statistics, it seems as though this number is a decent representation of the overall rental availability at any given moment in the given cities. Thus, I suspect any findings from this data can be applied with relative confidence to a larger population. 

# Cleaning

I first did some brief examination of the data in Excel to get a feel for what I'd have to take care of.

![Image](https://github.com/user-attachments/assets/dc349cfc-0657-4eaf-bd4e-6a687f0f676c)

Most of the data cleaning was done in SQL, and I aimed to accomplish this in one SQL script for simplicity.

The data is split into ~4 files per city (to conserve memory whilst scraping) and I do all imports/exports using MySQL's Table Import Wizard.

![Image](https://github.com/user-attachments/assets/ae971888-f4bc-444d-981f-10d7dbf1256b)

![Image](https://github.com/user-attachments/assets/95ba4410-12c1-4536-988f-e8922015932c)

(1) I first combine the data from each city into one file per city.

(2) I then add a 'City' identifier for each entry in the dataset, which will be useful later.

![Image](https://github.com/user-attachments/assets/19bc154a-c034-4489-9a50-10d3dc6eabe5)

(3) I then combine all of the data into one large dataset, encompassing listings from all cities. From here I create a duplicate staging table to work from.

![Image](https://github.com/user-attachments/assets/e1cc1ec4-0348-4a08-9948-6f55d7723440)

(4) I then remove duplicate entries (I find the easiest way to do this in SQL is to add a unique identifier, i.e. primary key, to all of the values in the original dataset and then do a row count which assigns values >1 to rows which appear 2+ times, then you can drop all matched ids where the row count is >1).

(5) I then go through each column in the dataset and standardize the format of all of the entires, remove outliers or values that are clearly wrong, and handle missing values.

(6) A 'quirk' of of this dataset is that many listings have prices/beds/baths/etc listed as ranges (e.g. Studio-3 beds), which looks pretty messy if we want to visualize this later on. So I opted to create, for each column where something like this occurs, new columns labeled "min_x", "max_x", and "avg_x", which act as their names suggest (where Studio = 0). I then drop the original columns after calculating these values. This both cleans up the dataset and preserves all original values.

(7) I finally extract zip codes from all of the listing addresses which is very helpful when making map-style visualizations in Tableau.

![Image](https://github.com/user-attachments/assets/60ff24d2-1952-422d-8d09-8e9f9bdcf094)

Here is what the final, cleaned data looks like: 

![Image](https://github.com/user-attachments/assets/352dff85-2db1-4d96-a011-9a54c6bc5080)

# Visualization
