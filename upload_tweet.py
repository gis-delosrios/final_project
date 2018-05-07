import os
import settings
from sentiment import TwitterClient
import sqlite3
import time
import tweepy


def upload_tweet():
    # create connection to local db
    conn = sqlite3.connect(settings.database_name)
    # query the database to retrieve the images that have not been uploaded
    images = conn.execute('''
        select 
            tweet_image_id, 
            filename 
        from 
            image_tweets 
        where 
            processed = 0 ''').fetchall()
    # instantiate a twitter client
    api = TwitterClient()
    # if there are images that have not been uploaded then upload the images
    if len(images) > 0:
        for image in images:
            # hard wait for twitter api
            time.sleep(3)
            id = image[0]
            fname = os.path.join(os.getcwd(), image[1])
            # upload the file and assign the tweet id to a resp variable
            resp = api.api.update_with_media(filename=os.path.join(os.getcwd(), fname), status=settings.twitter_status_update)
            # if the resp variable is not none then assign update the tweet image value of processed to 1
            if resp.id is not None:
                conn.execute('''UPDATE image_tweets
                                SET processed = 1,
                                twitter_id = {tweet_id}
                                WHERE tweet_image_id = {id}
                             '''.format(tweet_id=str(resp.id), id=id))
                conn.commit()


if __name__ == '__main__':
    upload_tweet()
