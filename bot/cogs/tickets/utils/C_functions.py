import os

import aiosqlite as sql

import disnake
from disnake.ui import View, string_select

from core import get_request, MainBot

from .C_ticket import CreateTicketView


class FunctionsView(View):
    
    options = [
        disnake.SelectOption(
            label="Отправить сообщение",
            description="Отправить сообщение с кнопкой \"Создать Тикет\"",
            value="send_message"
        )
    ]
    
    def __init__(self, bot: MainBot):
        super().__init__(timeout=None)
        self.bot = bot
        
    @string_select(
        options=options,
        custom_id="functions_select",
        placeholder="Выберите действие",
    )
    async def functions_select(self, select: disnake.SelectMenu, inter: disnake.MessageInteraction):
        await inter.response.defer(with_message=False)
        
        async with sql.connect(self.bot.db) as db:
            cursor = await db.cursor()
            channel_send = await cursor.execute("SELECT create_ticket_channel_id FROM guild_tickets_config WHERE guild_id = (?)", (inter.guild.id,))
            channel_send = await channel_send.fetchone()
            if channel_send[0] == None:
                embed_error = disnake.Embed(
                    title="Ошибка!",
                    description=f"{inter.author.mention}, перед тем как отправить сообщение, необходимо настроить канал кнопки \"Создать тикет\"",
                    colour=self.bot.error_colour
                )
                return await inter.send(
                    embed=embed_error,
                    ephemeral=True,
                    delete_after=15
                )
            channel_send = await inter.guild.fetch_channel(channel_send[0])
         
        data = await get_request(f"/{inter.guild.id}/embeds_data")
        embeds = data.get(f"{inter.guild.id}")
        embeds_send = []
        if embeds is None:
            embed = disnake.Embed(
                title="Тикеты еще не настроены!",
                colour=self.bot.invisible_colour
            )
            embeds_send.append(embed)
        else:
            for embed_type in embeds.keys():
                embed_type = dict(sorted(embed_type.items()))
                for em_data in embed_type.keys():
                    embed = disnake.Embed().from_dict(em_data)
                    embeds_send.append(embed)
                    
        await channel_send.send(
            embeds=embeds_send,
            view=CreateTicketView(bot=self.bot, data={"label": "Создать Тикет"})
        )