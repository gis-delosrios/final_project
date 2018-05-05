import os
import settings
from sentiment import TwitterClient
import sqlite3
import time
import tweepy


def upload_tweet():
    conn = sqlite3.connect(settings.database_name)
    images = conn.execute('''
        select 
            tweet_image_id, 
            filename 
        from 
            image_tweets 
        where 
            processed = 0 ''').fetchall()
    api = TwitterClient()
    if len(images) > 0:
        for image in images:
            time.sleep(3)
            id = image[0]
            fname = os.path.join(os.getcwd(), image[1])
            resp = api.api.update_with_media(filename=os.path.join(os.getcwd(), fname), status=settings.twitter_status_update)
            if resp.id is not None:
                conn.execute('''UPDATE image_tweets
                                SET processed = 1,
                                twitter_id = {tweet_id}
                                WHERE tweet_image_id = {id}
                             '''.format(tweet_id=str(resp.id), id=id))
                conn.commit()


if __name__ == '__main__':
    upload_tweet()
