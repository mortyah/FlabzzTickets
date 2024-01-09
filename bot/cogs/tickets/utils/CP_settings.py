import os

import aiosqlite as sql

import disnake
from disnake.ext import commands
from core import MainBot

from config import choose_setting_type_text
from .C_embeds import ChooseSettingTypeView


class Cog_control_panel_settings_tickets(commands.Cog):
    def __init__(self, bot: MainBot):
        self.bot = bot
        
    @commands.slash_command(
        name="панель-управления-тикетами",
        description="Настроить конфигурацию тикетов."
    )
    async def control_panel_tickets(self, inter: disnake.AppCmdInter):
        async with sql.connect(self.bot.db) as db:
            cursor = await db.cursor()
            check_guild_config = await cursor.execute("SELECT * FROM guild_tickets_config WHERE guild_id = (?)", (inter.guild.id,))
            check_guild_config = await check_guild_config.fetchone()
            if check_guild_config is None:
                await cursor.execute("INSERT INTO guild_tickets_config VALUES (?,?,?,?,?,?,?)", (
                    inter.guild.id,
                    None,
                    None,
                    25,
                    None,
                    None,
                    "ticket-idx"
                ))
                await db.commit()
        embed = disnake.Embed(
            title="Выберите пункт который вы хотите настроить",
            description=choose_setting_type_text,
            colour=self.bot.invisible_colour
        )
        await inter.send(
            embed=embed,
            view=ChooseSettingTypeView(self.bot, inter.author)
        )