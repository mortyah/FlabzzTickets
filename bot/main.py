import os
from dotenv import load_dotenv
from pathlib import Path

import asyncio

from core import MainBot


def set_bot_variables():
    bot = MainBot()
    bot.guild_test = 1129452068046913596
    bot.channel_test = 1129452068046913599
    return bot

def get_token():
    return os.getenv("TEST_TOKEN")

async def start_bot(bot: MainBot, token):
    await bot.load_cogs()
    await bot.start(token)

def main():
    load_dotenv(Path("./config/.env"))
    bot = set_bot_variables()
    TOKEN = get_token()
    asyncio.run(start_bot(bot, TOKEN))


if __name__ == "__main__":
    main()