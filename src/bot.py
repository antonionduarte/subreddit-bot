import praw
import sqlite3
import time
import datetime
import config

from praw import Reddit
from praw.models import Submission, Comment, Redditor, Subreddit


"""
Functions to connect to Reddit and Database
"""


# Function that connects to the account to use as bot
def connect_to_reddit():
    reddit = praw.Reddit(username=config.username, password=config.password, client_id=config.client_id,
                         client_secret=config.client_secret, user_agent=config.user_agent)
    return reddit


# Function that connects the bot to the database
def connect_to_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(
        'CREATE TABLE IF NOT EXISTS Users(Username TEXT PRIMARY KEY NOT NULL, Date DATE)')
    conn.commit()
    print('Connected to DB')
    return c, conn


# Function that retrieves the saved subscribed users from the DB
def get_subscribed_users(c, conn):
    users = list()
    c.execute('SELECT Username FROM Users')
    for username in c.fetchall():
        users.append(username[0])
    return users


# Function that removes users that haven't posted in an entire week
def remove_users(reddit: Reddit, users, subreddit, c, conn):
    moderator_relationship = subreddit.moderator()
    to_delete = list()
    moderators = list()
    for moderator in moderator_relationship:
        moderators.append(moderator)
    for user in users:
        redditor = reddit.redditor(user)
        in_subreddit = False
        join_date = get_user_join_date(user, c, conn)
        today = datetime.date.today()
        delta_time = today - join_date
        if delta_time.days <= 7:
            in_subreddit = True
            continue
        if not moderators.count(user) == 0:
            in_subreddit = True
            continue
        in_subreddit = iterate_over_days(redditor.comments.new(limit=1000),
                                         subreddit, config.removal_time)
        in_subreddit = iterate_over_days(redditor.submissions.new(limit=1000),
                                         subreddit, config.removal_time)
        if not in_subreddit:
            to_delete.append(user)
            subreddit.contributor.remove(user)
            c.execute('DELETE FROM Users WHERE Username=?', (user,))
            conn.commit()
    print('Users deleted:')
    for user in to_delete:
        print(user)
    print('Amount of users deleted: ', len(to_delete))
    print('')
    return to_delete


# Helper function to remove, to iterate over submissions and comments made
# during the time-frame considered
def iterate_over_days(to_iterate, subreddit, time_to_iterate):
    today = datetime.date.today()
    in_subreddit = False
    for element in to_iterate:
        element_utc = element.created_utc
        element_date = convert_utc_datetime(element_utc)
        delta_time = today - element_date
        if delta_time.days > time_to_iterate:
            break
        if element.subreddit == subreddit:
            in_subreddit = True
            break
    return in_subreddit


# Function that updates the database, adding the new contributor
def update_database(c, conn, users, subreddit: Subreddit):
    date = datetime.date.today()
    contributors = list()
    for contributor in subreddit.contributor(limit=0x7D0):
        contributors.append(contributor)
    for contributor in contributors:
        if users.count(contributor) == 0:
            contributor_name = contributor.name
            c.execute('INSERT INTO Users VALUES(?, ?)',
                      (contributor_name, date,))
            conn.commit()
    for user in users:
        if contributors.count(user) == 0:
            c.execute('DELETE FROM Users WHERE Username=?', (user,))
            conn.commit()
    print('Updated database\n')


"""
Functions related to inviting users
"""


# Function that gets the list of users to invite from a random subreddit
def get_user_list(reddit: Reddit):
    subreddit = reddit.subreddit(config.subreddit)
    users = list()
    added = 0
    for comment in subreddit.comments(limit=500):
        if users.count(comment.author) == 0:
            if (comment.author.link_karma + comment.author.comment_karma) > config.min_karma:
                users.append(comment.author)
                added += 1
        if added == config.number_users_invite:
            break
    print('Users to invite: ')
    for user in users:
        print(user.name)
        print(user.link_karma + user.comment_karma)
    print('Amount of users to invite: ', len(users))
    print('')
    return users


# Function that invites a list of users to a subreddit
def invite_users_subreddit(users, users_to_add, subreddit: Subreddit):
    for user in users_to_add:
        if users.count(user) == 0:
            subreddit.contributor.add(user)


"""
Date related helper functions
"""


# Get the join date of a specific user from the database
def get_user_join_date(user, c, conn):
    c.execute('SELECT Date from Users WHERE Username=?', (user,))
    date_list = c.fetchall()
    date_tuple = date_list[0]
    date_str = date_tuple[0]
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    return date


# Converts date from float format to datetime
def convert_utc_datetime(utc):
    to_date = datetime.datetime.utcfromtimestamp(utc)
    return to_date.date()


"""
Functions related to user flairs
"""


def update_flairs(subreddit: Subreddit, users, c, conn):
    moderators = list()
    for moderator in subreddit.moderator():
        moderators.append(moderator)
    for user in users:
        flair_set = False
        if not moderators.count(user) == 0:
            flair_set = True
            continue
        join_date = get_user_join_date(user, c, conn)
        days = (datetime.date.today() - join_date).days
        print(days)
        flairs = config.flairs
        for flair in flairs:
            if flair[2] >= days:
                subreddit.flair.set(user, flair[0], flair_template_id=flair[1])
                print(flair[0])
                flair_set = True
                break
            if not flair_set:
                to_set = flairs[len(flairs) - 1]
                subreddit.flair.set(
                    user, to_set[0], flair_template_id=to_set[1])
                print(to_set[0])
    print('Flairs updated\n')


"""
Functions related to the post when adding and removing users
"""


def make_post(reddit: Reddit, subreddit: Subreddit, invited, removed):
    date = datetime.date.today()
    date_str = date.strftime("%Y-%m-%d")
    title = date_str + ' - Bot Recap'
    selftext = ''
    if config.remove_users:
        if not len(removed) == 0:
            selftext = selftext + 'Kicked users:  \n'
            for user in removed:
                selftext = selftext + '* u/' + user.name + '\n'
    if config.invite_users:
        selftext = selftext + '\nAdded users:  \n'
        for user in invited:
            selftext = selftext + '* u/' + user.name + '\n'
    reddit.validate_on_submit = True
    subreddit.submit(title, selftext=selftext)
    print('Post made\n')


"""
Main function
"""


# Main function
def main():
    c, conn = connect_to_database()
    reddit = connect_to_reddit()
    subreddit = reddit.subreddit(config.owned_subreddit)
    users = get_subscribed_users(c, conn)
    update_database(c, conn, users, subreddit)
    users = get_subscribed_users(c, conn)
    removed_users = list()
    invited_users = list()
    if config.remove_users:
        removed_users = remove_users(reddit, users, subreddit, c, conn)
    if config.invite_users:
        invited_users = get_user_list(reddit)
        invite_users_subreddit(users, invited_users, subreddit)
    if config.update_flairs:
        update_flairs(subreddit, users, c, conn)
    if config.updates_post:
        make_post(reddit, subreddit, invited_users, removed_users)
    print('Everything worked.')
    print(len(users))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Fatal error - ' + str(e))
        print('System Message - Sleeping for 1 minute.')
