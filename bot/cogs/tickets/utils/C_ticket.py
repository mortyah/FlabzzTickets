import os

import time

import aiosqlite as sql

import disnake
from disnake.ui import Button, View, Modal, TextInput

from core import MainBot, get_request, delete_request

from typing import List


class CreateTicketView(View):
    def __init__(self, bot: MainBot, data: dict):
        super().__init__(timeout=None)
        self.add_item(CreateTicketButton(bot=bot, data=data))
        
        
class CreateTicketButton(Button):
    def __init__(self, bot: MainBot, data: dict):
        label = data.get("label")
        emoji = data.get("emoji")
        style = data.get("style")
        match style:
            case "red":
                style = disnake.ButtonStyle.red
            case "green":
                style = disnake.ButtonStyle.green
            case "blue":
                style = disnake.ButtonStyle.blurple
            case _:
                style = disnake.ButtonStyle.gray
        
        super().__init__(
            style=style,
            label=label,
            custom_id="CreateTicketButton",
            emoji=emoji
        )
        self.bot = bot
        
    async def callback(self, inter: disnake.MessageInteraction):
        async with sql.connect(self.bot.db) as db:
            cursor = await db.cursor()
            check_limit = await cursor.execute("SELECT tickets_limit_count FROM guild_tickets_config WHERE guild_id = (?)", (inter.guild.id,))
            check_limit = await check_limit.fetchone()
            try:
                limit_tickets = check_limit[0]
            except:
                limit_tickets = 25
            guild_tickets = await cursor.execute("SELECT * FROM tickets WHERE guild_id = (?)", (inter.guild.id,))
            guild_tickets = await guild_tickets.fetchall()
            if limit_tickets <= len(guild_tickets):
                embed_error = disnake.Embed(
                    title="Ошибка!",
                    description=f"{inter.author.mention}, на сервере стоит лимит тикетов в количестве **{limit_tickets}** штук! Вы не можете привысить этот лимит, мы уведомим вас, как только появится место для вас.",
                    colour=self.bot.error_colour
                )
                return await inter.send(
                    embed=embed_error,
                    ephemeral=True,
                    delete_after=15
                )
            return await inter.response.send_modal(CreateTicketModal(bot=self.bot))
            
            
class CreateTicketModal(Modal):
    def __init__(self, bot: MainBot):
        options = [
            TextInput(
                label="Введите причину открытия тикета:",
                custom_id="ticket_reason",
                style=disnake.TextInputStyle.multi_line,
                placeholder="Хочу получить роль"
            )
        ]
        super().__init__(
            title="Создание тикета",
            components=options
        )
        self.bot = bot
        
    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(with_message=False)
        
        reason = inter.text_values.get("ticket_reason")

        async with sql.connect(self.bot.db) as db:
            cursor = await db.cursor()
            
            category_id = await cursor.execute("SELECT category_tickets_id FROM guild_tickets_config WHERE guild_id = (?)", (inter.guild.id,))
            category_id: int | None = await category_id.fetchone()
            if category_id is None:
                category = None
            else:
                try:
                    category: disnake.CategoryChannel = await inter.guild.fetch_channel(category_id[0])
                except:
                    category = None
                    await cursor.execute("UPDATE guild_tickets_config SET category_tickets_id = (?) WHERE guild_id = (?)", (category, inter.guild.id,))
                    await db.commit()
                    
            ticket_channel_name = await cursor.execute("SELECT ticket_channel_name FROM guild_tickets_config WHERE guild_id = (?)", (inter.guild.id,))
            ticket_channel_name: str | None = await ticket_channel_name.fetchone()
            
            ticket_idx = await cursor.execute("SELECT idx FROM tickets WHERE guild_id = (?) ORDER BY idx DESC", (inter.guild.id,))
            ticket_idx: int | None = await ticket_idx.fetchone()
            if ticket_idx is None:
                ticket_idx = 0
            else:
                ticket_idx = ticket_idx[0]
            
            ticket_channel_name = ticket_channel_name[0].replace(
                "username", 
                f"{inter.author.nick if inter.author.nick is not None else inter.author.name}"
            )
            ticket_channel_name = ticket_channel_name.replace("idx", f"{ticket_idx+1}")

            ticket_overwrites = {
                inter.guild.me: disnake.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_messages=True,
                    add_reactions=True,
                    attach_files=True
                ),
                inter.guild.default_role: disnake.PermissionOverwrite(
                    view_channel=False
                ),
                inter.author: disnake.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_messages=True,
                    add_reactions=True,
                    attach_files=True,
                ),
            }
            
            moderation_roles: List[int] = await get_request(f"/{inter.guild.id}/tickets_moderation")
            moderation_roles = moderation_roles.get("roles")
            
            for data in moderation_roles:
                try:
                    role = inter.guild.get_role(data[0])
                    ticket_overwrites.update({
                        role: disnake.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True,
                            read_messages=True,
                            add_reactions=True,
                            attach_files=True,
                        ),
                    })
                except:
                    await delete_request(path=f"{inter.guild.id}/tickets_moderation", delete_data={
                        "column": "role_id",
                        "value": data[0]
                    })
            
            new_ticket_channel = await inter.guild.create_text_channel(
                name=ticket_channel_name,
                category=category,
                overwrites=ticket_overwrites,
                reason=f"{inter.author.name}: {reason}"
            )
            values = (inter.guild.id, ticket_idx+1, new_ticket_channel.id, inter.author.id, None, int(time.time()))
            await cursor.execute("INSERT INTO tickets VALUES (?,?,?,?,?,?)", values)
            await db.commit()
            
            embeds = []
            embeds_data = await get_request(f"{inter.guild.id}/embeds_data")
            if embeds_data is None:
                embed_exception = disnake.Embed(
                    title="Тикеты еще не настроены!",
                    colour=self.bot.invisible_colour
                )
                embeds.append(embed_exception)
            else:
                for embed_type in embeds_data.keys():
                    embed_type = dict(sorted(embed_type.items()))
                    for em_data in embed_type.keys():
                        embed = disnake.Embed().from_dict(em_data)
                        embeds.append(embed)
            embed_reason = disnake.Embed(
                title="Причина тикета:",
                description=reason,
                colour=self.bot.invisible_colour
            )
            embeds.append(embed_reason)
            
            await new_ticket_channel.send(embeds=embeds)