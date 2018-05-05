synch_db.py

- program to stream geospatially dependent tweets and writes to local db

models.py

- program that defines data models of database

arcpy_create_feature_class.py
- Processes going on:
    - creates new feature class SentimentEstimate
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
