import os

import disnake
from disnake.ext import commands
from core import MainBot

from .utils import Cog_control_panel_settings_tickets


class Cog_tickets(Cog_control_panel_settings_tickets):
    def __init__(self, bot: MainBot):
        self.bot = bot
        
    
        
def setup(bot: MainBot):
    bot.add_cog(Cog_tickets(bot))