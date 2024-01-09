import os

import aiosqlite as sql

import disnake
from disnake.ui import channel_select, View, string_select, Modal, TextInput

from core import MainBot


class UpdateGuildTicketsConfig(View):
    
    options = [
        disnake.SelectOption(
            label="Канал Создания",
            description="Изменить канал, в котором можно создать тикет через кнопку \"Создать Тикет\"",
            value="create_ticket_channel"
        ),
        disnake.SelectOption(
            label="Категория",
            description="Категория, в которой будут создаваться тикеты",
            value="ticket_category"
        ),
        disnake.SelectOption(
            label="Название Тикета",
            description="Изменить стиль названия тикет-канала",
            value="ticket_name"
        ),
        disnake.SelectOption(
            label="Лог Тикетов",
            description="Информация о закрытых тикетах",
            value="ticket_log"
        ),
        disnake.SelectOption(
            label="Лимит Тикетов",
            description="Изменить максимальное количество тикетов",
            value="ticket_limit"
        ),
    ]
    
    def __init__(self, bot: MainBot):
        super().__init__(timeout=None)
        self.bot = bot
        
    @string_select(
        options=options,
        placeholder="Меню выбора",
        custom_id="update_guild_tickets_config",
    )
    async def update_guild_tickets_config(self, select: disnake.SelectMenu, inter: disnake.MessageInteraction):
        await inter.response.defer(with_message=False)
        
        if inter.values[0] == "create_ticket_channel":
            return await inter.send(view=UpdateCreateTicketChannelView(bot=self.bot))
        elif inter.values[0] == "ticket_category":
            return await inter.send(view=UpdateTicketCategoryView(bot=self.bot))
        elif inter.values[0] == "ticket_name":
            return await inter.send(view=UpdateTicketNameView(bot=self.bot))
        elif inter.values[0] == "ticket_log":
            return await inter.send(view=UpdateTicketLogView(bot=self.bot))
        elif inter.values[0] == "ticket_limit":
            return await inter.response.send_modal(UpdateTicketLimitModal)
        
      
class UpdateCreateTicketChannelView(View):
    def __init__(self, bot: MainBot):
        super().__init__(timeout=None)
        self.bot = bot
        
    @channel_select(
        channel_types=[disnake.ChannelType.text], 
        custom_id="update_create_ticket_channel",
        placeholder="Выберите канал"
    )
    async def update_create_ticket_channel(self, select: disnake.ChannelSelectMenu, inter: disnake.MessageInteraction):
        await inter.response.defer(with_message=False)
        
        create_ticket_channel_id = int(inter.values[0])
        async with sql.connect(self.bot.db) as db:
            cursor = await db.cursor()
            await cursor.execute("UPDATE guild_tickets_config SET create_ticket_channel_id = (?) WHERE guild_id = (?)", (create_ticket_channel_id, inter.guild.id,))
            await db.commit()
        
        embed = disnake.Embed(
            title="Изменено!",
            description=f"{inter.author.mention}, вы изменили канал, в котором можно будет создать тикет!",
            colour=self.bot.invisible_colour
        )
        return await inter.send(embed=embed, ephemeral=True)        
    
            
class UpdateTicketLogView(View):
    def __init__(self, bot: MainBot):
        super().__init__(timeout=None)
        self.bot = bot
        
    @channel_select(
        channel_types=[disnake.ChannelType.text], 
        custom_id="update_ticket_log",
        placeholder="Выберите канал"
    )
    async def update_ticket_log(self, select: disnake.ChannelSelectMenu, inter: disnake.MessageInteraction):
        await inter.response.defer(with_message=False)
        
        log_channel_id = int(inter.values[0])
        async with sql.connect(self.bot.db) as db:
            cursor = await db.cursor()
            await cursor.execute("UPDATE guild_tickets_config SET tickets_log_channel_id = (?) WHERE guild_id = (?)", (log_channel_id, inter.guild.id,))
            await db.commit()
        
        embed = disnake.Embed(
            title="Изменено!",
            description=f"{inter.author.mention}, вы изменили категорию для тикетов!",
            colour=self.bot.invisible_colour
        )
        return await inter.send(embed=embed, ephemeral=True)
    
            
class UpdateTicketCategoryView(View):
    def __init__(self, bot: MainBot):
        super().__init__(timeout=None)
        self.bot = bot
        
    @channel_select(
        channel_types=[disnake.ChannelType.category], 
        custom_id="update_ticket_category",
        placeholder="Выберите категорию"
    )
    async def update_ticket_category(self, select: disnake.ChannelSelectMenu, inter: disnake.MessageInteraction):
        await inter.response.defer(with_message=False)
        
        category_id = int(inter.values[0])
        async with sql.connect(self.bot.db) as db:
            cursor = await db.cursor()
            await cursor.execute("UPDATE guild_tickets_config SET category_tickets_id = (?) WHERE guild_id = (?)", (category_id, inter.guild.id,))
            await db.commit()
        
        embed = disnake.Embed(
            title="Изменено!",
            description=f"{inter.author.mention}, вы изменили категорию для тикетов!",
            colour=self.bot.invisible_colour
        )
        return await inter.send(embed=embed, ephemeral=True)
    
    

class UpdateTicketNameView(View):
    
    options = [
        disnake.SelectOption(
            label="ticket-username",
            description="Пример: #ticket-mortyah",
            value="ticket-username"
        ),
        disnake.SelectOption(
            label="ticket-idx",
            description="Пример: #ticket-125",
            value="ticket-idx"
        ),
        disnake.SelectOption(
            label="username-ticket",
            description="Пример: #mortyah-ticket",
            value="username-ticket"
        ),
        disnake.SelectOption(
            label="idx-ticket",
            description="Пример: #125-ticket",
            value="idx-ticket"
        )
    ]
    
    def __init__(self, bot: MainBot):
        super().__init__(timeout=None)
        self.bot = bot
        
    @string_select(
        options=options,
        custom_id="update_ticket_name",
        placeholder="Выберите имя"
    )
    async def update_ticket_name(self, select: disnake.SelectMenu, inter: disnake.MessageInteraction):
        await inter.response.defer(with_message=False)
        
        async with sql.connect(self.bot.db) as db:
            cursor = await db.cursor()
            await cursor.execute("UPDATE guild_tickets_config SET ticket_channel_name = (?) WHERE guild_id = (?)", (inter.values[0], inter.guild.id,))
            await db.commit()
            
        embed = disnake.Embed(
            title="Изменено!",
            description=f"{inter.author.mention}, вы изменили названия для новых тикетов, теперь тикеты будут создаваться по типу **{inter.values[0]}**",
            colour=self.bot.invisible_colour
        )
        return await inter.send(embed=embed, ephemeral=True)
    
    
class UpdateTicketLimitModal(Modal):
    def __init__(self, bot: MainBot):
        
        options = [
            TextInput(
                label="Введите лимит тикетов:",
                custom_id="tickets_limit",
                max_length=2
            )
        ]
        
        super().__init__(
            components=options,
            title="Изменить лимит тикетов",
            custom_id="UpdateTicketLimitModal",
        )
        self.bot = bot
        
    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(with_message=False)
        
        limit = int(inter.text_values.get("tickets_limit"))
        
        async with sql.connect(self.bot.db) as db:
            cursor = await db.cursor()
            await cursor.execute("UPDATE guild_tickets_config SET tickets_limit_count = (?) WHERE guild_id = (?)", (limit, inter.guild.id,))
            await db.commit()
            
        embed = disnake.Embed(
            title="Изменено!",
            description=f"{inter.author.mention}, вы изменили лимит тикетов на сервере.",
            colour=self.bot.invisible_colour
        )
        return await inter.send(embed=embed, ephemeral=True)