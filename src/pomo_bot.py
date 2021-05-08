import discord
from discord.ext import tasks, commands
import logging
import asyncio
import time

logger = logging.getLogger(__name__)

class PomodoroState():
    cog = None
    def __init__(self, cog):
        self.cog = cog


class Pomodoro(commands.Cog):
    """Pomodoro related commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.pomodoro_states = {}

    def get_pomodoro_state(self, author):
        state = self.pomodoro_states.get(author.id)
        if state is None:
            state = PomodoroState(self)
            self.pomodoro_states[author.id] = state

        return state

    @commands.command()
    async def play(self, ctx):
        state = self.get_pomodoro_state(ctx.author)
        await ctx.send(f'Started timer for {ctx.author.mention}')

    @commands.command()
    async def pause(self, ctx):
        state = self.get_pomodoro_state(ctx.author)
        await ctx.send(f'Paused timer for {ctx.author.mention}')

    @commands.command()
    async def stop(self, ctx):
        state = self.get_pomodoro_state(ctx.author)
        await ctx.send(f'Stopped timer for {ctx.author.mention}')

    @commands.command()
    async def display(self, ctx):
        state = self.get_pomodoro_state(ctx.author)
        await ctx.send(f'Displaying for {ctx.author.mention}')
    

bot = commands.Bot(command_prefix=commands.when_mentioned_or('^'), description='A discord pomodoro timer')
bot.add_cog(Pomodoro(bot))


@bot.event
async def on_ready():
    logger.info('-------------------------')
    logger.info('We have logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    logger.info('-------------------------')
