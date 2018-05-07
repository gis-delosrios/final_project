import sentiment
import settings
from models import *
from sqlalchemy.orm import sessionmaker
import time


def main():
    # instantiate twitter client
    api = sentiment.TwitterClient()
    # define the list of cleaned tweets
    full_set = []
    # create the necessary tools for inserting newly created records into the tweet table
    engine = create_engine('sqlite:///sqlite.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    # iterate over each geographic location
    for i in range(len(settings.gps_array)):
        try:
            # instantiate a session
            session = DBSession()
            # hard wait before querying twitter
            time.sleep(10)
            # get the tweets at the geographic point
            tweets = api.get_tweets(query=' ', point=settings.gps_array[i])
            clean_tweets = []
            # if tweets are not none
            if tweets is not None:
                # iterate over each tweet and assign the lat and long to the record that is to be inserted
                for tweet in tweets:
                    tweet['latitude'] = settings.gps_array[i][0]
                    tweet['longitude'] = settings.gps_array[i][1]
                    # attempt to clean the tweet
                    try:
                        # print tweet
                        clean_tweets.append(tweet)
                    except:
                        pass
                # append the cleaned tweet to the full_set of tweets
                full_set += clean_tweets
                # if the cleaned tweet is greater than 0
                if len(clean_tweets) > 0:
                    new_tweets = []
                    # check to make sure that the tweet does not exist in the database already
                    # this ensures that tweets are not added to the database twice
                    for tweet in clean_tweets:
                        if session.query(Tweet).filter_by(id=tweet['id']).first() is None:
                            new_tweets.append(Tweet(**tweet))
                        else:
                            pass
                    # save all of the new tweets
                    if len(new_tweets) > 0:
                        session.add_all(new_tweets)
                        session.commit()
        except:
            pass


if __name__ == '__main__':
    while True:
        main()
        time.sleep(900)
