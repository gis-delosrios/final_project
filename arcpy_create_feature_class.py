import os
import arcpy, sys, traceback, datetime
from arcpy.mapping import *
import sqlite3
import settings
import time
import sys


def make_map(start_date=None, end_date=None):
    '''
    main function to generate map
    :param start_date: default is none; date needs to be iso format 2017-01-01
    :param end_date: default is none; date needs to be iso format
    :return: True
    '''
    # check if date was past if not then load the date defined in the settings file
    if start_date is None:
        beg_date = settings.start_date
        final_date = settings.end_date
    else:
        beg_date = start_date
        final_date = end_date
    # begin the geoprocessing
    try:
        # define the workspace
        fc_workspace = os.path.join(os.getcwd(), 'out_fgdatabase.gdb')
        # define the new feature class
        fc_name = "SentimentEstimate"
        # define the path to store the feature class
        outpath_table = os.path.join(fc_workspace, fc_name)
        # define the fields that will go into the feature class
        fc_fields = [dict(in_table=None,
                               field_name='tweet_id',
                               field_type='TEXT',
                               field_length=100),
                          dict(in_table=None,
                               field_name='latitude',
                               field_type='FLOAT'),
                          dict(in_table=None,
                               field_name='longitude',
                               field_type='FLOAT'),
                          dict(in_table=None,
                               field_name='sentiment',
                               field_type='TEXT',
                               field_length=50),
                          dict(in_table=None,
                               field_name='SentimentValue',
                               field_type='FLOAT')
                     ]

        # assign the workspace
        arcpy.env.workspace = fc_workspace
        # if the feature class exists then delete the class
        if arcpy.Exists(outpath_table):
            arcpy.Delete_management(outpath_table)
        # define the spatial reference
        sr = arcpy.SpatialReference(4326)
        # create the feature class as a point feature class with the associated spatial reference
        fc = arcpy.CreateFeatureclass_management(fc_workspace, fc_name, "POINT", spatial_reference=sr)
        # iterate over the defined fields and add them to the feature class
        for fc_field in fc_fields:
            fc_field['in_table'] = fc
            arcpy.AddField_management(**fc_field)
        # create a list of the field names
        fields = [val['field_name'] for val in fc_fields]
        # add the definition of the shape xy to the field list
        fields.append("SHAPE@XY")
        # create a connection to the local database that stores the tweet data
        conn = sqlite3.connect('sqlite.db')
        # instantiate the min and max values associated with sentiment value
        min_sent = 0
        max_sent = 0
        # leverage the insert cursor to insert new records into the feature class
        with arcpy.da.InsertCursor(outpath_table, fields) as irows:
            # define the query that will be passed to the database to return the cumulative value of sentiment for a given data point
            query = '''
            select 
                'id' as id, 
                latitude, 
                longitude, 
                sum(case when sentiment = 'positive' then 1 else case when sentiment = 'negative' then -1 else 0 end end) as sent_value 
            from 
                tweet
            where 
                created_date > '{beginning_date}'
            and 
                created_date < '{end_date}'
             group by 1,2,3
            '''.format(beginning_date=beg_date, end_date=final_date)
            tweets = conn.execute(query).fetchall()
            # fetch all of the tweets
            # iterate over all of the tweets and assign the sentiment value based on value sign of the integer
            for tweet in tweets:
                if tweet[3] > 0:
                    sent = 'positive'
                elif tweet[3] < 0:
                    sent = 'negative'
                else:
                    sent = 'none'
                # insert the row of values based on the order of the fields
                irows.insertRow(
                    (str(tweet[0]),
                     round(tweet[1], 6),
                     round(tweet[2], 6),
                     str(sent),
                     tweet[3],
                     (round(tweet[2], 6), round(tweet[1], 6)))
                )
                # re-assign the minimum or maximum values if the tweet value is the new extremum
                if tweet[3] < min_sent:
                    min_sent = tweet[3]
                if tweet[3] > max_sent:
                    max_sent = tweet[3]

        # full map tweet
        # assign the map document
        mxd = MapDocument(os.path.join(settings.gis_template_directory, 'tweet_template.mxd'))
        # create the coloration of the symbology
        for lyr in arcpy.mapping.ListLayers(mxd):
            try:
                if lyr.symbologyType == "GRADUATED_COLORS":
                    lyr.symbology.valueField = "SentimentValue"
                    lyr.symbology.classBreakValues = [min_sent, 0, 0.000001, max_sent]
                    lyr.symbology.classBreakLabels = ["{min} to 0 : Negative".format(min=round(min_sent, 0)), "0 : Neutral",
                                                      "1 to {max} : Positive".format(max=round(max_sent, 0))]
            except:
                pass
        # rewrite the title of the map to show the new date
        titleItem = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
        titleItem.text = "Sacramento Tweet Sentiment\n {start_date} - {end_date}".format(start_date=beg_date,
                                                                                       end_date=final_date)
        # to ensure that collisions of filenames do not occur us the epoch time as the name of the file
        map_image_name = os.path.join('images', str(round(time.time() * 1000)) + '.jpg')
        # export the map document as a jpg
        arcpy.mapping.ExportToJPEG(mxd, map_image_name)
        # insert the name of the exported image into the database
        sql_insert_statement = '''INSERT INTO image_tweets
            (filename, params, created_date)
            VALUES
            ('{name}', '{params}', '{date}')'''.format(name=map_image_name, params=str({"start_date": str(settings.start_date)}).replace("'", '"'),
                                                       date=datetime.datetime.now().isoformat())
        conn.execute(sql_insert_statement)
        conn.commit()

        # negative tweets
        # assign the negative tweet template
        mxd = MapDocument(os.path.join(settings.gis_template_directory, 'negative_template.mxd'))
        # change the symbology breaks base on the the new values
        for lyr in arcpy.mapping.ListLayers(mxd):
            try:
                if lyr.symbologyType == "GRADUATED_SYMBOLS":
                    lyr.symbology.valueField = "SentimentValue"
                    lyr.symbology.numClasses = 3
            except:
                pass
        # assign a new title to the map
        titleItem = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]

        titleItem.text = "Sacramento Negative Tweet Sentiment\n {start_date} - {end_date}".format(start_date=beg_date,
                                                                                       end_date=final_date)
        # assign the name to the image that is going to be created for the map
        map_image_name = os.path.join('images', str(round(time.time() * 1000)) + '.jpg')
        # export the map to jpg
        arcpy.mapping.ExportToJPEG(mxd, map_image_name)
        # insert the newly created image into the database for processing
        sql_insert_statement = '''INSERT INTO image_tweets
                    (filename, params, created_date)
                    VALUES
                    ('{name}', '{params}', '{date}')'''.format(name=map_image_name, params=str(
            {"start_date": str(settings.start_date)}).replace("'", '"'),
                                                               date=datetime.datetime.now().isoformat())
        conn.execute(sql_insert_statement)
        conn.commit()

        # positive tweets
        # assign the positive tweet template
        mxd = MapDocument(os.path.join(settings.gis_template_directory, 'positive_template.mxd'))
        # redefine the symbology based on new values
        for lyr in arcpy.mapping.ListLayers(mxd):
            try:
                if lyr.symbologyType == "GRADUATED_SYMBOLS":
                    lyr.symbology.valueField = "SentimentValue"
                    lyr.symbology.numClasses = 3
            except:
                pass
        # reassign the map a new title
        titleItem = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
        titleItem.text = "Sacramento Positive Tweet Sentiment\n {start_date} - {end_date}".format(start_date=beg_date,
                                                                                       end_date=final_date)
        # assign the name to the exported map image
        map_image_name = os.path.join('images', str(round(time.time() * 1000)) + '.jpg')
        arcpy.mapping.ExportToJPEG(mxd, map_image_name)
        # insert the record into the image table for the file to uploaded into the system
        sql_insert_statement = '''INSERT INTO image_tweets
                    (filename, params, created_date)
                    VALUES
                    ('{name}', '{params}', '{date}')'''.format(name=map_image_name, params=str(
            {"start_date": str(settings.start_date)}).replace("'", '"'),
                                                               date=datetime.datetime.now().isoformat())
        conn.execute(sql_insert_statement)
        conn.commit()
        return True

    except:

        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n     " + str(sys.exc_type) + ": " + str(
            sys.exc_value) + "\n"
        msgs = "ARCPY ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        arcpy.AddError(msgs)
        arcpy.AddError(pymsg)

        print msgs
        print pymsg

        arcpy.AddMessage(arcpy.GetMessages(1))
        print arcpy.GetMessages(1)
        return False


if __name__ == '__main__':
    try:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
        make_map(start_date, end_date)
    except:
        make_map()



