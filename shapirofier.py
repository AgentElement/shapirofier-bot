# encoding: utf-8

import praw
import re
import authenticate as auth
import time


class Bot:

    def __init__(self):
        self.reddit = praw.Reddit(client_id=auth.client_id,
                                  client_secret=auth.client_secret,
                                  username=auth.username,
                                  password=auth.password,
                                  user_agent='Non-political shapirofier-bot by u/AgentElement and u/agenttux.'
                                  )
        self.subreddits = self.reddit.subreddit(auth.subreddit)

    @staticmethod
    def shapirofy(comment_contents):
        words = comment_contents.split(' ')
        with open('whitelist.txt', 'r') as word_whitelist:
            word_list = word_whitelist.read()

            for index, word in enumerate(words):
                sanitized_word = '\n' + re.sub(r'\W+', '', word.lower()) + '\n'
                if sanitized_word in word_list:
                    words[index] = words[index].upper()

        return "".join(word + ' ' for word in words)

    @staticmethod
    def add_submission(submission):
        with open("__submission_cache.txt", 'a') as cache:
            cache.write("{} {}\n".format(submission.id, int(submission.created)))

    @staticmethod
    def check_if_replied(submission):
        for comment in submission.comments:
            if comment.author.name == auth.username:
                return True
        return False

    @staticmethod
    def check_submission(submission):
        with open("__submission_cache.txt") as cache:
            for replied in cache.readlines():
                if submission.id == replied.split()[0]:
                    return True
        return False

    def run(self):
        for submission in self.subreddits.stream.submissions():
            try:
                if submission.selftext == '' or self.check_if_replied(submission):
                    continue
                print(submission.title)
                reply = self.shapirofy(submission.selftext)
                submission.reply(reply).disable_inbox_replies()
            except Exception as e:
                print(e)
                time.sleep(10)

    def test_for_replies(self):
        for submission in self.subreddits.hot(limit=25):
            print(submission.title)
            if self.check_if_replied(submission):
                print('***')


def main():
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
