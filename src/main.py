import logging
import os
from pomo_bot import bot

def main():
    # Probably shouldn't have configured all of this logging stuff b/c I really don't need it
    # But wanted to try it so w/e

    # Create formatter
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    # Create console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    # Set up pomo_profile logger
    pomo_log = logging.getLogger('pomo_bot')
    pomo_log.setLevel(logging.DEBUG)
    # Create file handler
    pomo_fh = logging.FileHandler(filename='pomowonder.log', encoding='utf-8', mode='w')
    pomo_fh.setFormatter(formatter)
    # Attach handlers
    pomo_log.addHandler(pomo_fh)
    pomo_log.addHandler(ch)

    # Set discord.py logger to log to a file
    dis_log = logging.getLogger('discord')
    dis_log.setLevel(logging.WARN)
    # Create file handler
    dis_fh = logging.FileHandler(filename='dicord.log', encoding='utf-8', mode='w')
    dis_fh.setFormatter(formatter)
    # Attach handlers
    dis_log.addHandler(dis_fh)

    # Run bot
    token = os.environ.get("DISCORD_BOTKEY")
    bot.run(token)

if __name__ == '__main__':
    main()