# Subreddit to get the users from
subreddit = 'random'  # WARNING: Not recommended to change this setting

# Your subreddit
owned_subreddit = ''

# User invitation
# Enabling this feature will make it so the bot invites
# A specified number of users from a random subreddit
# With a specified minimum karma
invite_users = True
min_karma = 1000
number_users_invite = 50

# User removal
# Enabling this feature will make the bot remove users
# That haven't been active (submissions or comments)
# In the subreddit, in removal_time days.
remove_users = True
removal_time = 7  # Time of inactivity until removal in days

# Post with updates that the bot performed
# Enabling this feature, will make the bot create a post with the recap
# Of it's actions
# Warning: User invitation and removal should also be True
updates_post = True

# OAuth into Reddit Account
username = ''
password = ''
client_id = ''
client_secret = ''
user_agent = 'Just a rando unique identifier'  # No need to change this setting

# Update flairs
# This feature will assign a specified number of flairs,
# Related to the amount of time a user has been in the subreddit
#
# WARNING: Days need to be sequential, you can't have a flair that requires
# 5 days in between flairs that require 3 and 4 days.
# You also can't have flairs with repeated number of days.
#
# Format: ('flair-text', 'flair-template', days)
# - 'flair-text' - text that is displayed in the flair
# - 'flair-template' - ID of the template that you create in subreddit
# - days - the number of days required for a user to have this flair assigned
update_flairs = False
flairs = [('Week 1', 'flair-template', 3),
          ('Week 2', 'flair-template-2', 6)]
