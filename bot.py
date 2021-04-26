import discord
import logging
import os
import asyncio

class MyClient(discord.Client):
  async def on_ready(self):
    print(f'Hello World! We have logged in as {client.user}.')

# Configure logger
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='dicord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Configure client
token = os.environ.get("DISCORD_BOTKEY")
client = MyClient()
client.run(token)