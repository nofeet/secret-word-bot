import datetime
import json
import time
from pprint import pprint

from twython import Twython

CONFIG_FILE = './config.json'


def load_config():
    """Load and return config dict from JSON file."""
    with open(CONFIG_FILE) as f:
        return json.load(f)


class SecretWordBot(object):

    def __init__(self):
        self.config = load_config()
        self.client = self.get_twitter_client()

    def get_twitter_client(self):
        keys = self.config['keys']
        return Twython(keys['APP_KEY'], keys['APP_SECRET'],
                       keys['OAUTH_TOKEN'], keys['OAUTH_TOKEN_SECRET'])

    def find_tweet_since_date(self, query, date):
        """Search and return last tweet for query since given date.

        Return None if no tweet found.

        Does not include screen names or mentions in search.
        """
        q = '{0} -from:{0} -@{0}'.format(query)
        results = self.client.search(q=q, since=date)
        if results['statuses']:
            tweet = results['statuses'][-1]
            pprint(tweet['text'])
            return tweet

    def write_success_tweet(self, user, status_id, word):
        screen_name = user['screen_name']
        msg = '@{} Aaaaaah! You said the word of the day: "{}"'.format(screen_name, word)
        return self.client.update_status(status=msg, in_reply_to_status_id=status_id)

    def write_fail_tweet(self, word):
        msg = 'Boo! No one guessed the word of the day: {}'.format(word)
        self.client.update_status(status=msg)

    def pop_word_from_queue(self):
        with open(self.config['word_queue']) as f:
            words = f.readlines()
        word = words.pop(0)
        with open(self.config['word_queue'], 'w') as f:
            f.writelines(words)
        return word.rstrip()

    def run(self):

        active_day = None
        active_word = None
        word_found = False

        while True:
            today = datetime.datetime.utcnow().date()
            if active_day != today:
                if not word_found:
                    self.write_fail_tweet(active_word)
                # it's a new day. get new word.
                active_day = today
                active_word = self.pop_word_from_queue()
                word_found = False
                print('New word for {} is "{}"'.format(active_day, active_word))

            if not word_found:
                tweet = self.find_tweet_since_date(active_word, active_day)

                if tweet:
                    word_found = True
                    self.write_success_tweet(tweet['user'], tweet['id'], active_word)

            print('Sleeping.')
            time.sleep(60)



def main():
    bot = SecretWordBot()
    bot.run()


if __name__ == '__main__':
    main()