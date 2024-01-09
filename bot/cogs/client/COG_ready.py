import os

from disnake.ext import commands
from core import MainBot, DeleteMessageView


class Cog_on_bot(commands.Cog):
    def __init__(self, bot: MainBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.create_tables()
        self.bot.add_view(DeleteMessageView(self.bot))
        print(f"{self.bot.user.name} is ready!")


def setup(bot: commands.Bot):
    bot.add_cog(Cog_on_bot(bot))