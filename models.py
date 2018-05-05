import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime

Base = declarative_base()


class Tweet(Base):
    __tablename__ = 'tweet'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    sentiment = Column(Text, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)


class TopicModel(Base):
    __tablename__ = 'topic_model'
    model_id = Column(Integer, primary_key=True, index=True)
    start_datetime = Column(Text, nullable=False)
    end_datetime = Column(Text, nullable=False)
    serialized_model = Column(BLOB, nullable=False)


class TopicResults(Base):
    __tablename__ = 'topic_results'
    topic_result_id = Column(Integer, primary_key=True, index=True)
    topic_model_id = Column(Integer, ForeignKey('topic_model.model_id'))
    topic_model = relationship(TopicModel)


class TweetImage(Base):
    __tablename__ = 'image_tweets'
    tweet_image_id = Column(Integer, primary_key=True, index=True)
    filename = Column(Text)
    params = Column(Text)
    created_date = Column(Text, default=datetime.datetime.now().isoformat())
    processed = Column(Text, server_default='0')
    twitter_id = Column(Text, nullable=True, server_default='')


engine = create_engine('sqlite:///sqlite.db')
Base.metadata.create_all(engine)
