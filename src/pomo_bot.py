import logging
import discord
from discord.ext import tasks, commands
import asyncio
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class Timer:
    def __init__(self, duration: timedelta):
        self.duration = duration
        self.time_started = None 
        self.time_paused = None 
        self.paused = False
    
    def start(self) -> None:
        self.time_started = datetime.now()
        logger.debug('started')

    def pause(self) -> None:
        if self.time_started is None:
            raise ValueError("Timer not started")
        if self.paused:
            raise ValueError("Timer already paused")
        self.time_paused = datetime.now()
    
    def reset(self) -> None:
        self.time_started = None
    
    def get(self) -> float:
        if self.paused:
            return self.time_paused - self.time_started
        else:
            return datetime.now() - self.time_started
    
    def is_done(self) -> bool:
        return self.get() >= self.duration
    
    async def timeout(self):
        while not self.is_done():
        
        logger.debug('stopped')
        self.reset()


class PomodoroState:
    def __init__(self, bot, is_work: bool):
        self.voice = None
        self.bot = None
        self.timer = None
        self.is_work = is_work

    def get_timer(self) -> Timer:
        if self.timer is None:
            if self.is_work:
                self.timer = Timer(timedelta(seconds = 10))
            else:
                self.timer = Timer(timedelta(seconds = 2))

        return self.timer
    
    def start_timer(self):
        timer = self.get_timer()
        timer.start()

    def pause_timer(self):
        timer = self.get_timer()
        timer.pause()

    def reset_timer(self):
        timer = self.get_timer()
        timer.reset()
    
    async def timeout(self):
        timer = self.get_timer()
        await timer.timeout()
        

class Pomodoro(commands.Cog):
    """Pomodoro related commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.pomodoro_states = {}

    def get_pomodoro_state(self, guild):
        state = self.pomodoro_states.get(guild.id)
        if state is None:
            state = PomodoroState(self.bot, True)
            self.pomodoro_states[guild.id] = state

        return state

    @commands.command()
    async def play(self, ctx):
        state = self.get_pomodoro_state(ctx.guild)
        asyncio.ensure_future(self.timer_end_task(ctx))
        state.start_timer()
        await ctx.send(f'{ctx.author.mention} Started a timer!')

    @commands.command()
    async def pause(self, ctx):
        state = self.get_pomodoro_state(ctx.guild)
        state.pause_timer()
        await ctx.send(f'{ctx.author.mention} Paused a timer!')

    @commands.command()
    async def stop(self, ctx):
        state = self.get_pomodoro_state(ctx.guild)
        state.stop_timer()
        await ctx.send(f'{ctx.author.mention} Stopped a timer!')
    
    async def timer_end_task(self, ctx):
        state = self.get_pomodoro_state(ctx.guild)
        await state.timeout()
        state = self.get_pomodoro_state(ctx.guild)
        await ctx.send(f'{ctx.author.mention} Timer ended!')


bot = commands.Bot(command_prefix=commands.when_mentioned_or('^'), description='A discord pomodoro timer')
bot.add_cog(Pomodoro(bot))


@bot.event
async def on_ready():
    logger.info('-------------------------')
    logger.info('We have logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    logger.info('-------------------------')
