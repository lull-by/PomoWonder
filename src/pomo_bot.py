import discord
from discord.ext import tasks, commands
import logging
import asyncio
import time

logger = logging.getLogger(__name__)
default_work_time = 25 * 60
default_break_time = 5 * 60

class PomodoroTimer():
    is_paused = False

    def __init__(self, state, timer_duration):
        self.start_time = None
        self.is_paused = False
        self.pause_update_time = None
        self.pause_duration = 0
        self.state = state
        self.timer_duration = timer_duration
    
    def start(self):
        logger.debug("start")
        if (self.start_time is None):
            self.start_time = time.time()
            self._tick.start()
        else:
            raise(RuntimeError("Timer already started"))
    
    def pause(self):
        if (not self.is_paused):
            self.pause_update_time = time.time()
            self.is_paused = True
            self._tick.stop()
        else:
            raise(RuntimeError("Cannot pause when already paused"))
    
    def unpause(self):
        if (self.is_paused):
            self._update_pause_duration()
            self.pause_update_time = None
            self.is_paused = False
            self._tick.start()
        else:
            raise(RuntimeError("Cannot unpause when already unpaused"))
    
    def stop(self):
        if (self.start_time is not None):
            self.is_paused = False
            self.pause_update_time = None
            self.start_time = None
            self._tick.stop()
        else:
            raise(RuntimeError("Cannot stop timer that hasn't been started"))

    def get_time_elapsed(self):
        self._update_pause_duration()
        if self.start_time is None:
            return 0
        elif self.pause_duration is None:
            return time.time() - self.start_time
        else:
            return time.time() - self.start_time - self.pause_duration

    def _update_pause_duration(self):
        if (self.pause_update_time is not None):
            # update the pause_duration since the last update_pause_duration
            self.pause_duration += time.time() - self.pause_update_time
            self.pause_update_time = time.time()

    @tasks.loop(seconds=1)
    async def _tick(self):
        elapsed = self.get_time_elapsed()
        duration = self.timer_duration
        logger.debug(f"tick elapsed: {elapsed} duration: {duration}")

        if elapsed >= duration:
            self.stop()
            await self.state.on_timer_end()
            logger.debug("end")


class PomodoroState():
    is_work = True

    def __init__(self, cog, ctx, is_work, work_timer_duration, break_timer_duration):
        self.cog = cog
        self.ctx = ctx
        self.is_work = is_work
        self.work_timer_duration = work_timer_duration
        self.break_timer_duration = break_timer_duration
        self.timer = PomodoroTimer(self, work_timer_duration)

    def start_timer(self):
        self.timer.start()

    def pause_timer(self):
        self.timer.pause()

    def unpause_timer(self):
        self.timer.unpause()

    def stop_timer(self):
        self.timer.stop()
    
    def set_timer(self, is_work):
        self.is_work = is_work
        if is_work:
            self.timer = PomodoroTimer(self, self.work_timer_duration)
        else:
            self.timer = PomodoroTimer(self, self.break_timer_duration)
    
    def set_next_timer(self):
        if self.is_work:
            self.set_timer(False)
        else:
            self.set_timer(True)
    
    async def on_timer_end(self):
        await self.cog.on_timer_end(self.ctx)
        self.set_next_timer()
        self.start_timer()
    
    def is_paused(self):
        return self.timer.is_paused
    
    def get_time_elapsed(self):
        return self.timer.get_time_elapsed()


class Pomodoro(commands.Cog):
    """Pomodoro related commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.pomodoro_states = {}

    def get_pomodoro_state(self, author):
        return self.pomodoro_states.get(author.id)

    def set_pomodoro_state(self, author, state):
        self.pomodoro_states[author.id] = state

    @commands.command()
    async def play(self, ctx):
        state = self.get_pomodoro_state(ctx.author)
        if state is None:
            new_state = PomodoroState(self, ctx, True, default_work_time, default_break_time)
            self.set_pomodoro_state(ctx.author, new_state)
            state = new_state
        
        if state.is_paused():
            state.unpause_timer()
            await ctx.send(f'Unpaused timer for {ctx.author.mention}')

        else:
            state.start_timer()
            await ctx.send(f'Started timer for {ctx.author.mention}')

    @commands.command()
    async def pause(self, ctx):
        state = self.get_pomodoro_state(ctx.author)
        if state is None:
            await ctx.send(f'No timer created for {ctx.author.mention}')
        else:
            state.pause_timer()
            await ctx.send(f'Paused timer for {ctx.author.mention}')

    @commands.command()
    async def unpause(self, ctx):
        state = self.get_pomodoro_state(ctx.author)
        if state is None:
            await ctx.send(f'No timer created for {ctx.author.mention}')
        else:
            state.unpause_timer()
            await ctx.send(f'Unpaused timer for {ctx.author.mention}')

    @commands.command()
    async def stop(self, ctx):
        state = self.get_pomodoro_state(ctx.author)
        if state is None:
            await ctx.send(f'No timer created for {ctx.author.mention}')
        else:
            state.stop_timer()
            await ctx.send(f'Stopped timer for {ctx.author.mention}')

    @commands.command()
    async def display(self, ctx):
        state = self.get_pomodoro_state(ctx.author)
        if state is None:
            await ctx.send(f'No timer created for {ctx.author.mention}')
        else:
            time_elapsed = state.get_time_elapsed()
            time_elapsed_min = int(time_elapsed // 60)
            time_elapsed_sec = int(time_elapsed % 60)
            is_work = state.is_work
            if is_work:
                await ctx.send(f'Work time elapsed for {ctx.author.mention} is {time_elapsed_min:02}:{time_elapsed_sec:02}')
            else:
                await ctx.send(f'Break time elapsed for {ctx.author.mention} is {time_elapsed_min:02}:{time_elapsed_sec:02}')


    async def on_timer_end(self, ctx):
        state = self.get_pomodoro_state(ctx.author)
        is_work = state.is_work
        if is_work:
            await ctx.send(f'Work timer complete notification for {ctx.author.mention}, starting break timer')
        else:
            await ctx.send(f'Break timer complete notification for {ctx.author.mention}, starting work timer')


bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    '^'), description='A discord pomodoro timer')
bot.add_cog(Pomodoro(bot))


@bot.event
async def on_ready():
    logger.info('-------------------------')
    logger.info('We have logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    logger.info('-------------------------')
