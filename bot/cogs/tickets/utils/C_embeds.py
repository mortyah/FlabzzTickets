import os
import traceback

import disnake
from disnake.ui import string_select, View, Select, Modal, TextInput

from core import MainBot, author_interaction_error, get_request, post_request, delete_request, DeleteMessageView
from config import choose_embed_type_text, choose_embed_data_type_text, choose_setting_type_mod_roles_text
from ._helpers import (
    get_translate_data, 
    get_translate_embeds, 
    get_translate_data_of_label, 
    get_translate_data_of_placeholder,
    get_data_type_options
)
from .C_modroles import ChooseSettingTypeModRolesView
from .C_change_config import UpdateGuildTicketsConfig
from .C_functions import FunctionsView

from typing import List


class ChooseSettingTypeView(View):
    
    options = [
        disnake.SelectOption(
            label="・Embeds",
            value="embeds",
            description="Настроить эмбеды тикетов."
        ),
        disnake.SelectOption(
            label="・Moderation Roles",
            value="mod_roles",
            description="Настроить модераторские роли.",
        ),
        # disnake.SelectOption(
        #     label="・Buttons",
        #     value="buttons",
        #     description="Настроить кнопки тикетов."
        # ),
        disnake.SelectOption(
            label="・Конфигурация",
            value="config",
            description="Настроить конфигурацию тикетов."
        ),
        disnake.SelectOption(
            label="・Functions",
            value="functions",
            description="Изменить статус функций бота."
        )
    ]
    
    def __init__(self, bot: MainBot, author: disnake.Member):
        super().__init__(timeout=None)
        self.bot = bot
        self.author = author
        
    @string_select(
        placeholder="Меню выбора",
        options=options,
        custom_id="ChooseSettingTypeSelect"
    )
    async def choose_setting_type_select(self, select: disnake.SelectMenu, inter: disnake.MessageInteraction):
        if inter.author != self.author: return await author_interaction_error(inter)
        if inter.values[0] == "embeds":
            embed = disnake.Embed(
                title="Выберите тип эмбеда который вы хотите настроить.",
                description=choose_embed_type_text,
                colour=self.bot.invisible_colour
            )
            return await inter.response.edit_message(
                embed=embed, 
                view=ChooseEmbedTypeView(
                    bot=self.bot, 
                    author=self.author
                )
            )
        elif inter.values[0] == "mod_roles":
            embed = disnake.Embed(
                title="Выберите тип поля, который вы хотите настроить",
                description=choose_setting_type_mod_roles_text,
                colour=self.bot.invisible_colour
            )
            return await inter.response.edit_message(
                embed=embed,
                view=ChooseSettingTypeModRolesView(self.bot)
            )
        elif inter.values[0] == "config":
            embed = disnake.Embed(
                title="Выберите тип поля, который вы хотите настроить",
                colour=self.bot.invisible_colour
            )
            return await inter.response.edit_message(
                embed=embed,
                view=UpdateGuildTicketsConfig(self.bot)
            )
        elif inter.values[0] == "functions":
            embed = disnake.Embed(
                title="Выберите компонент, который вам необходим",
                colour=self.bot.invisible_colour
            )
            return await inter.response.edit_message(
                embed=embed,
                view=FunctionsView(self.bot)
            )


class ChooseEmbedTypeView(View):
    
    options = [
        disnake.SelectOption(
            label="・Embed \"Open Ticket\"",
            description="Изменить баннер для эмбеда",
            value="open_ticket"
        ),
        disnake.SelectOption(
            label="・Embed \"Ticket Reply\"",
            description="Изменить заголовок эмбеда",
            value="ticket_reply",
        ),
        disnake.SelectOption(
            label="・Embed \"Ticket Log\"",
            description="Изменить описание эмбеда",
            value="ticket_log"
        ),
    ]    
    
    def __init__(self, bot: MainBot, author: disnake.Member):
        super().__init__(timeout=None)
        self.bot = bot
        self.author = author        

    @string_select(
        options=options,
        placeholder="Выберите пункт",
        custom_id="ChooseEmbedTypeSelect"
    )
    async def choose_embed_type_select(self, select: disnake.SelectMenu, inter: disnake.MessageInteraction):
        if inter.author != self.author: return await author_interaction_error(inter)
        if inter.values[0] == "ticket_log":
            embed = disnake.Embed(
                title="Упс...",
                description=f"{inter.author.mention}, эта функция находится в стадии разработки! Заходите на наш **[сервер](https://discord.gg/Hpeueugn57)**, чтобы следить за обновлениями!",
                colour=self.bot.invisible_colour
            )
            return await inter.send(
                embed=embed,
                ephemeral=True,
            )
        embed = disnake.Embed(
            title="Выберите тип поля, которое вы хотите настроить.",
            description=choose_embed_data_type_text,
            colour=self.bot.invisible_colour
        )
        data = await get_request(f"/{inter.guild.id}/emoji_select_options/{inter.values[0]}")
        options = get_data_type_options(data)
        return await inter.response.edit_message(
            embed=embed,
            view=ChooseEmbedDataTypeView(
                bot=self.bot, 
                author=self.author, 
                options=options, 
                embed_type=inter.values[0]
            )
        )

       
            
class ChooseEmbedDataTypeView(View):
    def __init__(self, bot: MainBot, author: disnake.Member, options: List[disnake.SelectOption], embed_type: str):        
        super().__init__(timeout=None)
        self.add_item(ChooseEmbedDataTypeSelect(bot, author, options, embed_type))


class ChooseEmbedDataTypeSelect(Select):
    def __init__(self, bot: MainBot, author: disnake.Member, options: List[disnake.SelectOption], embed_type: str):
        super().__init__(
            custom_id="ChooseEmbedDataTypeSelect",
            placeholder="Меню выбора",
            options=options
        )
        self.bot = bot
        self.author = author
        self.embed_type = embed_type
        
    async def callback(self, inter: disnake.MessageInteraction):
        if inter.author != self.author: return await author_interaction_error(inter)
        await inter.message.edit(view=self.view)
        if "image" not in inter.values or "banner" not in inter.values:
            await inter.response.send_modal(UpdateEmbedDataModal(
                bot=self.bot,
                author=self.author,
                embed_type=self.embed_type,
                data_type=inter.values[0],
            ))
        else:
            ...
      
            
class UpdateEmbedDataModal(Modal):
    def __init__(self, bot: MainBot, author: disnake.Member, embed_type: str, data_type: str):
        embed_type_rus = get_translate_embeds(embed_type)
        data_type_rus = get_translate_data(data_type)
        label = get_translate_data_of_label(data_type)
        placeholder = get_translate_data_of_placeholder(data_type)
        
        options = [
            TextInput(
                label=label,
                style=disnake.TextInputStyle.multi_line,
                placeholder=placeholder,
                custom_id="data"
            )
        ]
        
        super().__init__(
            title=f"Изменить {data_type_rus} эмбеда \"{embed_type_rus}\"",
            custom_id="UpdateEmbedDataModal",
            timeout=3600,
            components=options
        )
        self.author = author
        self.embed_type = embed_type
        self.data_type = data_type
        self.data_type_rus = data_type_rus
        self.embed_type_rus = embed_type_rus
        self.bot = bot
        
    async def update_embeds_image(self, inter: disnake.Interaction, url: str):
        guild = await self.bot.fetch_guild(self.bot.guild_test)
        channel = await guild.fetch_channel(self.bot.channel_test)
        try:
            embed = disnake.Embed().set_image(url)
            await channel.send(embed=embed, delete_after=0.1)
            return True
        except:
            embed_error = disnake.Embed(
                title="Ошибка!",
                description=f"{inter.author.mention}, вы ввели невалидный URL картинки.",
                colour=self.bot.error_colour
            )
            await inter.send(
                embed=embed_error,
                ephemeral=True,
                delete_after=15
            )
            return False

    async def update_embeds_color(self, inter: disnake.Interaction, color: str):
        guild = await self.bot.fetch_guild(self.bot.guild_test)
        channel = await guild.fetch_channel(self.bot.channel_test)
        try:
            embed = disnake.Embed(colour=int(f"0x{color}", 16), title="check color")
            await channel.send(embed=embed, delete_after=0.1)
            return True
        except Exception as e:
            embed_error = disnake.Embed(
                title="Ошибка!",
                description=f"{inter.author.mention}, вы ввели неправильный HEX-code цвета.",
                colour=self.bot.error_colour
            )
            await inter.send(
                embed=embed_error,
                ephemeral=True,
                delete_after=15
            )
            return False
        
    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(with_message=False)
        value = inter.text_values.get("data")
        if inter.author != self.author: 
            return await author_interaction_error(inter, data=value)
        if value.strip().lower() == "remove" or value.strip().lower() == "удалить":
            data = await get_request(f"/{inter.guild.id}/emoji_select_options/{self.embed_type}")
            if data.get(f"emoji_{self.data_type}") == "🟥":
                embed_error = disnake.Embed(
                    title="Ошибка!",
                    description=f"{inter.author.mention}, Вы не можете удалить то, чего не существует!",
                    colour=self.bot.error_colour
                )
                return await inter.send(
                    embed=embed_error,
                    ephemeral=True,
                    delete_after=15
                )
            await delete_request(
                path=f"/{inter.guild.id}/embeds_data", 
                post_data=[
                    self.embed_type,
                    self.data_type,
                    value
                ]
            )
            embed = disnake.Embed(
                title=f"Удаление!",
                description=f"{inter.author.mention}, вы удалили **{self.data_type_rus}** для эмбеда **\"{self.embed_type_rus}\"**. Больше информации можно узнать в логе",
                colour=self.bot.invisible_colour
            )
            await inter.send(
                embed=embed,
                view=DeleteMessageView(self.bot)
            )
            data = await get_request(f"/{inter.guild.id}/emoji_select_options/{self.embed_type}")
            options = get_data_type_options(data)
            await inter.message.edit(view=None)
            return await inter.message.edit(
                view=ChooseEmbedDataTypeView(
                    bot=self.bot,
                    author=self.author,
                    options=options,
                    embed_type=self.embed_type
                )
            )
        else:
            if self.data_type in ["banner", "image"]:
                if not await self.update_embeds_image(inter, value): 
                    return
            if self.data_type == "color":
                if not await self.update_embeds_color(inter, value):
                    return
            await post_request(
                path=f"/{inter.guild.id}/embeds_data", 
                post_data=[
                    self.embed_type,
                    self.data_type,
                    value
                ]
            )
        data = await get_request(f"/{inter.guild.id}/emoji_select_options/{self.embed_type}")
        options = get_data_type_options(data)
        embed = disnake.Embed(
            title="Изменено!",
            description=f"{inter.author.mention}, вы изменили **{self.data_type_rus}** для эмбеда **\"{self.embed_type_rus}\"**. Больше информации можно узнать в логе",
            colour=self.bot.invisible_colour
        )
        await inter.message.edit(view=None)
        await inter.message.edit(
            view=ChooseEmbedDataTypeView(
                bot=self.bot,
                author=self.author,
                options=options,
                embed_type=self.embed_type
            )
        )
        return await inter.send(
            embed=embed,
            view=DeleteMessageView(self.bot)
        )