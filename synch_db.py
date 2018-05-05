import sentiment
import settings
from models import *
from sqlalchemy.orm import sessionmaker
import time


def main():
    api = sentiment.TwitterClient()
    full_set = []
    engine = create_engine('sqlite:///sqlite.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    for i in range(len(settings.gps_array)):
        try:
            session = DBSession()
            time.sleep(10)
            tweets = api.get_tweets(query=' ', point=settings.gps_array[i])
            clean_tweets = []
            if tweets is not None:
                for tweet in tweets:
                    tweet['latitude'] = settings.gps_array[i][0]
                    tweet['longitude'] = settings.gps_array[i][1]
                    try:
                        # print tweet
                        clean_tweets.append(tweet)
                    except:
                        pass
                full_set += clean_tweets
                if len(clean_tweets) > 0:
                    new_tweets = []
                    for tweet in clean_tweets:
                        if session.query(Tweet).filter_by(id=tweet['id']).first() is None:
                            new_tweets.append(Tweet(**tweet))
                        else:
                            pass
                    if len(new_tweets) > 0:
                        session.add_all(new_tweets)
                        session.commit()
        except:
            pass


if __name__ == '__main__':
    while True:
        main()
        time.sleep(900)
