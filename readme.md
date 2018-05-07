**before running project:**

pip install from requirements.txt

setup the settings.py file
- this will require you to change the variables in the settings.py file in private_settings.py file

- modify the paths to your instance of ArcGIS python

**Project Descriptions**

requirements.txt
- requirements file that is excluding arcpy

run_project.py
- file that runs all of the necessary files query local db, create maps, and upload maps to twitter

run_arcmap.py
- helper that calls arcgis installation of python executable for the map rendering

synch_db.py
- program to stream geospatially dependent tweets and writes to local db

models.py
- program that defines data models of database

sentiment.py
- largely repurposed from https://www.geeksforgeeks.org/twitter-sentiment-analysis-using-python/
    - slight modifications surrounding authentication referencing
    - large modification in the tweet fetching
- during the process of fetching and writing tweets sentiment from the tweet is determined prioir to writing to the database

arcpy_create_feature_class.py
- Processes going on:
    - creates new feature class SentimentEstimate
        - deletes feature class if it exists
        - adds fields to feature class
        - leverages proper spatial referencing
        - specifies point feature
    - uses insert cursor for newly created feature class
        - queries data base and summarizes sentiment value basedon geospatial reference
        - tracks the min and max values of sentiment found as records are inserted into the db
    - leverages three premade arcmap documents as templates
        - all sentiment | tweet_template.mxd
        - positive sentiment | positive_template.mxd
        - negative sentiment | negative_template.mxd
    - all sentiment map processing
        - renders both positive and negative sentiment on one map
        - updates the title for the date range of values that are being used
        - exports the map document to a jpg
        - inserts a record in the database for the newly created image and flagged as 0 for not being uploaded
    - positive and negative map processing
        - each arcmap document has a built in definition layer query for the feature class SentimentValue
            - negative sentiment for negative
            - positive sentiment for positive
        - title is updated with the proper date range
        - symbology is updated based upon the extremum values that were being tracked during the inserting of the records into the database
            - larger radius corresponds with a more positive sentiment value
        - map is exported as a jpg to the images directory
        - inserts a record in the database for the newly created image and flagged as 0 for not being uploaded

upload_tweet.py
- file that uploads newly created images to twitter
    - queries that local db for all of the twitter images that have not been uploaded to twitter
    - uploads each image to twitter and changes the upload_status to 1 so it is not uploaded twice

settings.py
- file that houses the global settings
    - references to system variables
    - references to location of where the twitter api should be pointed at
    - references to the degree of resolution that the points should be referenced
    - generates the geospatial grids of points that will be used to obtain geographic points of interest
    - settings for time windows that the program uses to query against the database
