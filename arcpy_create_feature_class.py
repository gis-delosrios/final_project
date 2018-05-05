import os
import arcpy, sys, traceback, datetime
from arcpy.mapping import *
import sqlite3
import settings
import time
import sys


def make_map(start_date=None, end_date=None):
    if start_date is None:
        beg_date = settings.start_date
        final_date = settings.end_date
    else:
        beg_date = start_date
        final_date = end_date
    try:
        fc_workspace = os.path.join(os.getcwd(), 'out_fgdatabase.gdb')
        fc_name = "SentimentEstimate"
        outpath_table = os.path.join(fc_workspace, fc_name)

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

        arcpy.env.workspace = fc_workspace

        if arcpy.Exists(outpath_table):
            arcpy.Delete_management(outpath_table)

        sr = arcpy.SpatialReference(4326)

        fc = arcpy.CreateFeatureclass_management(fc_workspace, fc_name, "POINT", spatial_reference=sr)

        for fc_field in fc_fields:
            fc_field['in_table'] = fc
            arcpy.AddField_management(**fc_field)

        fields = [val['field_name'] for val in fc_fields]
        fields.append("SHAPE@XY")
        conn = sqlite3.connect('sqlite.db')
        min_sent = 0
        max_sent = 0
        with arcpy.da.InsertCursor(outpath_table, fields) as irows:
            query = '''select 'id' as id, latitude, longitude, sum(case when sentiment = 'positive' 
            then 1 else case when sentiment = 'negative' then -1 else 0 end end) as sent_value 
            from tweet
            where created_date > '{beginning_date}'
            and created_date < '{end_date}'
                 group by 1,2,3
            '''.format(beginning_date=beg_date, end_date=final_date)
            tweets = conn.execute(query).fetchall()
            for tweet in tweets:
                if tweet[3] > 0:
                    sent = 'positive'
                elif tweet[3] < 0:
                    sent = 'negative'
                else:
                    sent = 'none'
                irows.insertRow(
                    (str(tweet[0]),
                     round(tweet[1], 6),
                     round(tweet[2], 6),
                     str(sent),
                     tweet[3],
                     (round(tweet[2], 6), round(tweet[1], 6)))
                )
                if tweet[3] < min_sent:
                    min_sent = tweet[3]
                if tweet[3] > max_sent:
                    max_sent = tweet[3]

        # full map tweet
        mxd = MapDocument(os.path.join(settings.gis_template_directory, 'tweet_template.mxd'))
        for lyr in arcpy.mapping.ListLayers(mxd):
            try:
                if lyr.symbologyType == "GRADUATED_COLORS":
                    lyr.symbology.valueField = "SentimentValue"
                    lyr.symbology.classBreakValues = [min_sent, 0, 0.000001, max_sent]
                    lyr.symbology.classBreakLabels = ["{min} to 0 : Negative".format(min=round(min_sent, 0)), "0 : Neutral",
                                                      "1 to {max} : Positive".format(max=round(max_sent, 0))]
            except:
                pass

        titleItem = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
        titleItem.text = "Sacramento Tweet Sentiment\n {start_date} - {end_date}".format(start_date=beg_date,
                                                                                       end_date=final_date)
        map_image_name = os.path.join('images', str(round(time.time() * 1000)) + '.jpg')
        arcpy.mapping.ExportToJPEG(mxd, map_image_name)
        sql_insert_statement = '''INSERT INTO image_tweets
            (filename, params, created_date)
            VALUES
            ('{name}', '{params}', '{date}')'''.format(name=map_image_name, params=str({"start_date": str(settings.start_date)}).replace("'", '"'),
                                                       date=datetime.datetime.now().isoformat())
        conn.execute(sql_insert_statement)
        conn.commit()

        # negative tweets
        mxd = MapDocument(os.path.join(settings.gis_template_directory, 'negative_template.mxd'))
        for lyr in arcpy.mapping.ListLayers(mxd):
            try:
                if lyr.symbologyType == "GRADUATED_SYMBOLS":
                    lyr.symbology.valueField = "SentimentValue"
                    lyr.symbology.numClasses = 3
            except:
                pass

        titleItem = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]

        titleItem.text = "Sacramento Negative Tweet Sentiment\n {start_date} - {end_date}".format(start_date=beg_date,
                                                                                       end_date=final_date)

        map_image_name = os.path.join('images', str(round(time.time() * 1000)) + '.jpg')
        arcpy.mapping.ExportToJPEG(mxd, map_image_name)
        sql_insert_statement = '''INSERT INTO image_tweets
                    (filename, params, created_date)
                    VALUES
                    ('{name}', '{params}', '{date}')'''.format(name=map_image_name, params=str(
            {"start_date": str(settings.start_date)}).replace("'", '"'),
                                                               date=datetime.datetime.now().isoformat())
        conn.execute(sql_insert_statement)
        conn.commit()

        # positive tweets
        mxd = MapDocument(os.path.join(settings.gis_template_directory, 'positive_template.mxd'))
        for lyr in arcpy.mapping.ListLayers(mxd):
            try:
                if lyr.symbologyType == "GRADUATED_SYMBOLS":
                    lyr.symbology.valueField = "SentimentValue"
                    lyr.symbology.numClasses = 3
            except:
                pass
        titleItem = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")[0]
        titleItem.text = "Sacramento Positive Tweet Sentiment\n {start_date} - {end_date}".format(start_date=beg_date,
                                                                                       end_date=final_date)
        map_image_name = os.path.join('images', str(round(time.time() * 1000)) + '.jpg')
        arcpy.mapping.ExportToJPEG(mxd, map_image_name)
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



