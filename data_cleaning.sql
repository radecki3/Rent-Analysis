## First combine data from each city into one table, then add a identifier to each row (a new column) with the city name

####Chicago####
DROP TABLE IF EXISTS chicago_rentals;

CREATE TABLE chicago_rentals AS
(SELECT * FROM chicago_apartment_rentals_pages_1_50
UNION ALL
SELECT * FROM chicago_apartment_rentals_pages_50_100
UNION ALL
SELECT * FROM chicago_apartment_rentals_pages_100_150
UNION ALL
SELECT * FROM chicago_apartment_rentals_pages_150_200);

ALTER TABLE chicago_rentals
ADD COLUMN City varchar(50);

UPDATE chicago_rentals
SET City = 'Chicago';


#####Dallas####
DROP TABLE IF EXISTS dallas_rentals;

CREATE TABLE dallas_rentals AS
(SELECT * FROM dallas_apartment_rentals_pages_1_50
UNION ALL
SELECT * FROM dallas_apartment_rentals_pages_50_100
UNION ALL
SELECT * FROM dallas_apartment_rentals_pages_100_150
UNION ALL
SELECT * FROM dallas_apartment_rentals_pages_150_200);

ALTER TABLE dallas_rentals
ADD COLUMN City varchar(50);

UPDATE dallas_rentals
SET City = 'Dallas';


####Houston####
DROP TABLE IF EXISTS houston_rentals;

CREATE TABLE houston_rentals AS
(SELECT * FROM houston_apartment_rentals_pages_1_50
UNION ALL
SELECT * FROM houston_apartment_rentals_pages_50_100
UNION ALL
SELECT * FROM houston_apartment_rentals_pages_100_150
UNION ALL
SELECT * FROM houston_apartment_rentals_pages_150_200);

ALTER TABLE houston_rentals
ADD COLUMN City varchar(50);

UPDATE houston_rentals
SET City = 'Houston';


####Jacksonville####
DROP TABLE IF EXISTS jacksonville_rentals;

CREATE TABLE jacksonville_rentals AS
(SELECT * FROM jacksonville_apartment_rentals_pages_1_50
UNION ALL
SELECT * FROM jacksonville_apartment_rentals_pages_50_100);

ALTER TABLE jacksonville_rentals
ADD COLUMN City varchar(50);

UPDATE jacksonville_rentals
SET City = 'Jacksonville';


####LA####
DROP TABLE IF EXISTS la_rentals;

CREATE TABLE la_rentals AS
(SELECT * FROM la_apartment_rentals_pages_1_50
UNION ALL
SELECT * FROM la_apartment_rentals_pages_50_100
UNION ALL
SELECT * FROM la_apartment_rentals_pages_100_150
UNION ALL
SELECT * FROM la_apartment_rentals_pages_150_200);

ALTER TABLE la_rentals
ADD COLUMN City varchar(50);

UPDATE la_rentals
SET City = 'Los Angeles';


####New York####
DROP TABLE IF EXISTS ny_rentals;

CREATE TABLE ny_rentals AS
(SELECT * FROM newyork_apartment_rentals_pages_1_50
UNION ALL
SELECT * FROM newyork_apartment_rentals_pages_50_100
UNION ALL
SELECT * FROM newyork_apartment_rentals_pages_100_150
UNION ALL
SELECT * FROM newyork_apartment_rentals_pages_150_200);

ALTER TABLE ny_rentals
ADD COLUMN City varchar(50);

UPDATE ny_rentals
SET City = 'New York';


####Philly####
DROP TABLE IF EXISTS philly_rentals;

CREATE TABLE philly_rentals AS
(SELECT * FROM philly_apartment_rentals_pages_1_50
UNION ALL
SELECT * FROM philly_apartment_rentals_pages_50_100
UNION ALL
SELECT * FROM philly_apartment_rentals_pages_100_150
UNION ALL
SELECT * FROM philly_apartment_rentals_pages_150_200);

ALTER TABLE philly_rentals
ADD COLUMN City varchar(50);

UPDATE philly_rentals
SET City = 'Philadelphia';


####Phoenix####
DROP TABLE IF EXISTS phoenix_rentals;

CREATE TABLE phoenix_rentals AS
(SELECT * FROM phoenix_apartment_rentals_pages_1_50
UNION ALL
SELECT * FROM phoenix_apartment_rentals_pages_50_100
UNION ALL
SELECT * FROM phoenix_apartment_rentals_pages_100_150
UNION ALL
SELECT * FROM phoenix_apartment_rentals_pages_150_200);

ALTER TABLE phoenix_rentals
ADD COLUMN City text;

UPDATE phoenix_rentals
SET City = 'Phoenix';


####San Antonio####
DROP TABLE IF EXISTS sa_rentals;

CREATE TABLE sa_rentals AS
(SELECT * FROM sanantonio_apartment_rentals_pages_1_50
UNION ALL
SELECT * FROM sanantonio_apartment_rentals_pages_50_100
UNION ALL
SELECT * FROM sanantonio_apartment_rentals_pages_100_150
UNION ALL
SELECT * FROM sanantonio_apartment_rentals_pages_150_200);

ALTER TABLE sa_rentals
ADD COLUMN City text;

UPDATE sa_rentals 
SET City = 'San Antonio';


####San Diego####
DROP TABLE IF EXISTS sd_rentals;

CREATE TABLE sd_rentals AS
(SELECT * FROM sandiego_apartment_rentals_pages_1_50
UNION ALL
SELECT * FROM sandiego_apartment_rentals_pages_50_100
UNION ALL
SELECT * FROM sandiego_apartment_rentals_pages_100_150);

ALTER TABLE sd_rentals
ADD COLUMN City text;

UPDATE sd_rentals 
SET City = 'San Diego';


## Now combine all of the city tables
DROP TABLE IF EXISTS rentals;

CREATE TABLE rentals AS
(SELECT * FROM chicago_rentals
UNION ALL
SELECT * FROM dallas_rentals
UNION ALL
SELECT * FROM houston_rentals
UNION ALL
SELECT * FROM jacksonville_rentals
UNION ALL
SELECT * FROM la_rentals
UNION ALL
SELECT * FROM ny_rentals
UNION ALL
SELECT * FROM philly_rentals
UNION ALL
SELECT * FROM sa_rentals
UNION ALL
SELECT * FROM phoenix_rentals
UNION ALL
SELECT * FROM sd_rentals);

SELECT *
FROM rentals
LIMIT 20000;

##Start cleaning
DROP TABLE IF EXISTS rentals_staging;

CREATE TABLE rentals_staging
LIKE rentals;

INSERT INTO rentals_staging
SELECT *
FROM rentals;

#adds a unique identifier to every entry
ALTER TABLE rentals_staging 
ADD COLUMN id int UNSIGNED AUTO_INCREMENT PRIMARY KEY;

#removes the blank entries
DELETE FROM rentals_staging
WHERE Price = 0 AND Beds = 0 AND Bath = 0 AND Sqft = 0;

SELECT *
FROM rentals_staging
LIMIT 20000;

#remove duplicates
WITH duplicate_cte AS (
  SELECT id, 
	ROW_NUMBER() OVER(
	  PARTITION BY Price, Beds, Bath, Sqft, `Type`, `Name`, Address,`Page`
	  ORDER BY id #ensures first occurence is kept
    ) AS row_num
  FROM rentals_staging
)
DELETE FROM rentals_staging
WHERE id IN (
	SELECT id FROM duplicate_cte WHERE row_num >1);

#gets rid of this unncessary column
ALTER TABLE rentals_staging
DROP COLUMN MyUnknownColumn;

SELECT *
FROM rentals_staging
LIMIT 20000;

#Fix the Type column
SELECT DISTINCT `Type`
FROM rentals_staging;

UPDATE rentals_staging
SET `Type` = REPLACE(`Type`, 'For Rent - ','');

#Fix the Price column
UPDATE rentals_staging
SET 
	Price = REPLACE(Price, '$', ''),
    Price = REPLACE(Price, ',', '');
    
ALTER TABLE rentals_staging
ADD COLUMN min_price INT,
ADD COLUMN max_price INT,
ADD COLUMN avg_price INT;  
    
#gets the min, max, avg price for the ones with a range
UPDATE rentals_staging
SET 
  avg_price = (
	(CAST(SUBSTRING_INDEX(Price, ' - ', 1) AS UNSIGNED) +
    CAST(SUBSTRING_INDEX(Price, ' - ', -1) AS UNSIGNED)) / 2),
  min_price = CAST(SUBSTRING_INDEX(Price, ' - ', 1) AS UNSIGNED),
  max_price = CAST(SUBSTRING_INDEX(Price, ' - ', -1) AS UNSIGNED)  
WHERE Price LIKE '% - %';

UPDATE rentals_staging
SET Price = NULL
WHERE Price = 'Contact for price';

UPDATE rentals_staging
SET 
  avg_price = CAST(Price AS UNSIGNED),
  min_price = CAST(Price AS UNSIGNED),
  max_price = CAST(Price AS UNSIGNED)
WHERE PRICE IS NOT NULL AND Price NOT LIKE '% - %';

ALTER TABLE rentals_staging
DROP COLUMN Price;

SELECT *
FROM rentals_staging
LIMIT 20000;

#Fix the Beds Column
SELECT DISTINCT Beds
FROM rentals_staging;

UPDATE rentals_staging
SET
  Beds = REPLACE(Beds,'bed',''),
  Beds = REPLACE(Beds,'Bed','');

#remove beds > 10
UPDATE rentals_staging
SET
  Beds = NULL
WHERE Beds = "" OR Beds = "15" OR Beds = "20" OR Beds = "16" OR Beds = "17" OR Beds = "12" OR Beds = "11" OR Beds = "69" OR Beds = "14" OR Beds = "13" OR Beds = "280" OR Beds = "460" OR Beds = "44";

#Let's say studio = 0 beds (as it technically is)
UPDATE rentals_staging
SET Beds = REPLACE(Beds,'Studio','0');

ALTER TABLE rentals_staging
ADD COLUMN min_beds INT,
ADD COLUMN max_beds INT,
ADD COLUMN avg_beds INT;  

UPDATE rentals_staging
SET
  avg_beds = CAST(Beds AS UNSIGNED),
  min_beds = CAST(Beds AS UNSIGNED),
  max_beds = CAST(Beds AS UNSIGNED)
WHERE Beds NOT LIKE '% - %';

UPDATE rentals_staging
SET 
  avg_beds = (
	(CAST(SUBSTRING_INDEX(Beds, ' - ', 1) AS UNSIGNED) +
    CAST(SUBSTRING_INDEX(Beds, ' - ', -1) AS UNSIGNED)) / 2),
  min_beds = CAST(SUBSTRING_INDEX(Beds, ' - ', 1) AS UNSIGNED),
  max_beds = CAST(SUBSTRING_INDEX(Beds, ' - ', -1) AS UNSIGNED)  
WHERE Beds LIKE '% - %';

ALTER TABLE rentals_staging
DROP COLUMN Beds;

SELECT *
FROM rentals_staging
LIMIT 20000;

#Fix the Bath Column
SELECT DISTINCT Bath
FROM rentals_staging;

UPDATE rentals_staging
SET
  Bath = REPLACE(Bath,'bath',''),
  Bath = REPLACE(Bath,'Bath','');

UPDATE rentals_staging
SET
  Bath = NULL
WHERE Bath LIKE '%+%' OR Bath = '';

#remove baths > 10
UPDATE rentals_staging
SET
  Bath = NULL
WHERE Bath = '13' OR Bath = '11' OR Bath = '14' OR Bath = '18' OR Bath = '10.5' OR Bath = '12' OR Bath = '16' OR Bath = '99' OR Bath = '15';

ALTER TABLE rentals_staging
ADD COLUMN min_bath DECIMAL(3,1),
ADD COLUMN max_bath DECIMAL(3,1),
ADD COLUMN avg_bath DECIMAL(3,1);  

UPDATE rentals_staging
SET
  avg_bath = CAST(Bath AS DECIMAL(3,1)),
  min_bath = CAST(Bath AS DECIMAL(3,1)),
  max_bath = CAST(Bath AS DECIMAL(3,1))
WHERE Bath NOT LIKE '% - %';

UPDATE rentals_staging
SET 
  avg_bath = (
	(CAST(SUBSTRING_INDEX(Bath, ' - ', 1) AS DECIMAL(3,1)) +
    CAST(SUBSTRING_INDEX(Bath, ' - ', -1) AS DECIMAL(3,1))) / 2),
  min_bath = CAST(SUBSTRING_INDEX(Bath, ' - ', 1) AS DECIMAL(3,1)),
  max_bath = CAST(SUBSTRING_INDEX(Bath, ' - ', -1) AS DECIMAL(3,1))  
WHERE Bath LIKE '% - %';

ALTER TABLE rentals_staging
DROP COLUMN Bath;

SELECT *
FROM rentals_staging
LIMIT 20000;

#Fix Sqft Column 
UPDATE rentals_staging
SET
  Sqft = REPLACE(Sqft, ',',''),
  Sqft = REPLACE(Sqft, '-13','');
  
UPDATE rentals_staging
SET
  Sqft = NULL
WHERE Sqft = '';

ALTER TABLE rentals_staging
ADD COLUMN min_sqft INT,
ADD COLUMN max_sqft INT,
ADD COLUMN avg_sqft INT;

UPDATE rentals_staging
SET
  avg_sqft = CAST(Sqft AS UNSIGNED),
  min_sqft = CAST(Sqft AS UNSIGNED),
  max_sqft = CAST(Sqft AS UNSIGNED)
WHERE Sqft NOT LIKE '% - %';

UPDATE rentals_staging
SET 
  avg_sqft = (
	(CAST(SUBSTRING_INDEX(Sqft, ' - ', 1) AS UNSIGNED) +
    CAST(SUBSTRING_INDEX(Sqft, ' - ', -1) AS UNSIGNED)) / 2),
  min_sqft = CAST(SUBSTRING_INDEX(Sqft, ' - ', 1) AS UNSIGNED),
  max_sqft = CAST(SUBSTRING_INDEX(Sqft, ' - ', -1) AS UNSIGNED)  
WHERE Sqft LIKE '% - %';

ALTER TABLE rentals_staging
DROP COLUMN Sqft;
  
SELECT *
FROM rentals_staging
LIMIT 20000;

#Get Zip Codes
ALTER TABLE rentals_staging
ADD COLUMN zipcode VARCHAR(5);

UPDATE rentals_staging
SET zipcode = RIGHT(TRIM(Address),5);

SELECT *
FROM rentals_staging
LIMIT 20000;

#done for now.