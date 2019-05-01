# encoding: utf-8

import praw
import praw.models
import re
import authenticate as auth
import time


class Bot:

    def __init__(self):
        self.reddit = praw.Reddit(client_id=auth.client_id,
                                  client_secret=auth.client_secret,
                                  username=auth.username,
                                  password=auth.password,
                                  user_agent='Non-political shapirofier-bot by u/AgentElement'
                                  )

        self.keyphrase = '!shapirofy'
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
    def check_if_replied(comment):
        comment.refresh()
        for reply in comment.replies:
            if reply.author is None:
                continue
            if reply.author.name == auth.username:
                return True
        return False

    @staticmethod
    def check_if_replied_submission(submission):  # TODO needs rewrite
        for comment in submission.comments:
            if isinstance(comment, praw.models.MoreComments):
                for more_comments in comment.comments():
                    if Bot.check_if_replied(more_comments):
                        return True
                    return False
            if Bot.check_if_replied(comment):
                return True
        return False

    def return_parent_text(self, comment):
        parent_id = comment.parent_id
        if parent_id[0:2] == 't3':
            return comment.submission.selftext
        else:
            return self.reddit.comment(id=parent_id[3:]).body

    def run(self):
        for comment in self.subreddits.stream.comments():
            try:
                if not comment.body == self.keyphrase or self.check_if_replied(comment):
                    continue

                text = self.return_parent_text(comment)

                if text is None or text == '':
                    continue

                comment.reply(self.shapirofy(text))
                print(comment.id)

            except Exception as e:
                print(e)
                time.sleep(10)

    def test_for_replies(self):
        for submission in self.subreddits.new(limit=25):
            print(submission.id,
                  '****' if self.check_if_replied_submission(submission) else '    ',
                  submission.title)


def main():
    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
