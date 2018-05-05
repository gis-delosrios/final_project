import os
import upload_tweet


def run_project():
    os.system('python run_arcmap.py')
    upload_tweet.upload_tweet()


if __name__ == '__main__':
    run_project()


