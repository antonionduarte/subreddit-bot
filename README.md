# Subreddit Moderation Bot

**WARNING** - This is old code from when I was dumb, you should probably **not** use this.

*Invites a configurable amount of random users, retrieved from the comments of a randomly chosen subreddit.*  
*Removes users that haven't posted in the subreddit in a configurable amount of days.*  
*Makes a post containing the bot actions in the current run (a list of removed and invited users)*  
*Updates user flairs, you can have a specific list of flairs that are assigned to users that have been in the subreddit during x amount of configurable time*  

# Setup

- Download Python 3.9 from the Python website - https://www.python.org/downloads/
- Follow the instructions and intall it. We recommend you select the option "add python to PATH environment"
- Install praw using python's package manager - *pip install praw*
- To run the bot, simply run *python3 bot.py* while in the folder of the bot. (You must move to it using the terminal's *cd* command).

# Configuration

- Configuring the bot must be done through the config.py file.
- The "owned_subreddit" field must have the name of your subreddit, (the one the bot should act uppon).
- You must configure the OAuth to the user account of your specific bot. You also need to create an application on that Bot account.
- You must activate your deactivate the desired features with *True* or *False* in the fields *invite_users*, *remove_users*, *updates_post*, *update_flairs*.
- In the *flairs* field, you must configure the list of flairs, each flair must contain the flair text and the ID of the flair template for each flair, which you can create in your subreddit's mod tools, and the number of days for each user to have assigned a specific flair.

# Warnings

- All the functionality that is related to a specific time frames, is not the actual time that the user has been in the subreddit, but the time since you first ran the bot.
- You shouldn't delete the generated *users.db* file, it's the database that contains information related to each user necessary for the bot to run, unless you want to reset the user dates.
