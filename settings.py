import numpy as np
import datetime
import os
import private_settings


geo_code = '37.781157,-122.398720'
radius = '10mi'

deg_per_mile = 69.0
delta_mile_resolution = 0.5
degree_delta = round(delta_mile_resolution * deg_per_mile**-1, 6)
locations = [37.510860, -122.499944, 38.749762, -120.974991]
nw = '38.692881,-121.576820'
se = '38.443239,-121.305595'
gps_array = []

for xval in np.arange(float(se.split(',')[0]), float(nw.split(',')[0]), degree_delta):
    for yval in np.arange(float(nw.split(',')[1]), float(se.split(',')[1]), degree_delta):
        gps_array.append([xval, yval])


twitter_consumer_key = private_settings.twitter_consumer_key
twitter_consumer_secret = private_settings.twitter_consumer_secret
twitter_access_token = private_settings.twitter_access_token
twitter_access_secret = private_settings.twitter_access_secret
twitter_status_update = 'LOS RIOS GEO 375'


armap_python = r'C:\Python27\ArcGIS10.5\python.exe'

gis_template_directory = os.getcwd()

database_name = 'sqlite.db'

start_date = (datetime.datetime.today() + datetime.timedelta(days=-2)).strftime('%Y-%m-%d')
end_date = (datetime.datetime.today() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')

image_directory = os.path.join(os.getcwd(), 'images')


if os.path.exists(image_directory):
    pass
else:
    os.mkdir(image_directory)

