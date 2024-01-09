import os
from dotenv import load_dotenv

from pathlib import Path

import disnake
from disnake.ext import commands
from disnake.ui import View, button
import aiohttp

import aiosqlite as sql

import json


load_dotenv(Path("./config/.env"))

api_uri = os.getenv("API_URI")
access_token = os.getenv("API_ACCESS_TOKEN")
user = os.getenv("API_USER")
password = os.getenv("API_PASSWORD")


class MainBot(commands.Bot):

    def __init__(self):
        intents = disnake.Intents.default()
        intents.guilds = True
        intents.message_content = True
        super().__init__(
            command_prefix=self.get_command_prefix,
            intents=intents
        )
        self.db = "./config/database/db.db"
        self.load_dotenv = load_dotenv(Path("./config/.env"))
        self.invisible_colour = 0x2b2d31
        self.error_colour = 0xFF4F4F
        self.green_colour = 0x4FFF4F
        

    async def get_command_prefix(self, message: disnake.Message):
        async with sql.connect(self.db) as db:
            cursor = await db.cursor()
            prefix = await cursor.execute(
                "SELECT command_prefix FROM guild_config WHERE guild_id = (?)", 
                (message.guild.id,)
            )
            prefix = await prefix.fetchone()
            if prefix is None:
                prefix = "~"
            else:
                prefix = prefix[0]
        return prefix
    
    async def create_tables(self):
        async with sql.connect(self.db) as db:
            cursor = await db.cursor()
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS guild_tickets_config(
                    guild_id INTEGER,
                    tickets_log_channel_id INTEGER,
                    category_tickets_id INTEGER,
                    tickets_limit_count INTEGER,
                    create_ticket_channel_id INTEGER,
                    create_ticket_message_id INTEGER,
                    ticket_channel_name TEXT
                )
            """)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS guild_tickets_moderation(
                    guild_id INTEGER,
                    role_id INTEGER
                )
            """)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS guild_main_config(
                    guild_id INTEGER,
                    command_prefix TEXT,
                    log_channel INTEGER
                )                     
            """)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets(
                    guild_id INTEGER,
                    idx INTEGER,
                    channel_id INTEGER,
                    creator_id INTEGER,
                    claimer_id INTEGER,
                    created_at INTEGER
                )                     
            """)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_waiting_ticket(
                    guild_id INTEGER,
                    user_id INTEGER
                )
            """)
            await db.commit()

    async def load_cogs(self):
        for folder in os.listdir("./bot/cogs"):
            for file in os.listdir(f"./bot/cogs/{folder}"):
                if file.startswith("COG_") and file.endswith(".py"):
                    self.load_extension(f"cogs.{folder}.{file[:-3]}")
        
        
async def author_interaction_error(inter: disnake.Interaction, data: str = None):
    inputed_data = ""
    if data is not None:
        inputed_data = f"\nДанные поля:\n{data}"
    embed = disnake.Embed(
        title="Ошибка!",
        description=f"{inter.author.mention}, вы не можете использовать это!{inputed_data}",
        colour=0xFF4F4F
    )
    return await inter.send(
        embed=embed,
        ephemeral=True,
        delete_after=15
    )
    
    
async def get_request(path: str, get_data: list = None) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=f"{api_uri}{path}",
            data={
                "access_token": access_token,
                "user": user,
                "password": password,
                "data": get_data
            },
            headers={
                "Content-Type": "application/json"
            }
        ) as resp:
            try:
                return json.loads(await resp.text(encoding="utf-8"))
            except Exception as e:
                print(await resp.text(encoding="utf-8"))
    
async def post_request(path: str, post_data: list | set = None):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=f"{api_uri}{path}",
            data={
                "access_token": access_token,
                "user": user,
                "password": password,
                "data": post_data
            },
            headers={
                "Content-Type": "application/json"
            }
        ) as resp:
            return resp
        
async def delete_request(path: str, delete_data: list | set = None):
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            url=f"{api_uri}{path}",
            data={
                "access_token": access_token,
                "user": user,
                "password": password,
                "data": delete_data
            },
            headers={
                "Content-Type": "application/json"
            }
        ) as resp:
            return resp    


class DeleteMessageView(View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @button(
        label="Удалить сообщение",
        style=disnake.ButtonStyle.red,
        emoji="🗑️",
        custom_id="delete_message_btn"
    )
    async def delete_message_btn(self, btn: disnake.Button, inter: disnake.MessageInteraction):
        await inter.message.delete()