import os
from dotenv import load_dotenv
from pathlib import Path

import aiosqlite as sql

from flask import Blueprint, request

from urllib.parse import parse_qs
from typing import List

from core import get_data, update_data


db_path = "./config/database/db.db"

load_dotenv(Path("./config/.env"))

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')              

def get_api_request_data(main: List[str] = ["access_token", "password", "user", "data"]) -> dict:
    data = parse_qs(request.get_data(as_text=True))
    if len(data) < len(main):
        return {
            "error": f"Request data hasn't all need keys in data",
            "code": False
        }
    for key in data.keys():
        if key not in main:
            return {
                "error": f"Request data has undefined key in data (key: {key})",
                "code": False
            }
    access_token = os.getenv("API_ACCESS_TOKEN")
    user = os.getenv("API_USER")
    password = os.getenv("API_PASSWORD")
    print(data.get("access_token")[0], access_token, data.get("access_token")[0] == access_token)
    if data.get("access_token")[0] != access_token:
        return {
            "error": "Unknown access token",
            "code": False
        }
    if data.get("password")[0] != password:
        return {
            "error": "Unknown password",
            "code": False
        }
    if data.get("user")[0] != user:
        return {
            "error": "Unknown user",
            "code": False
        }
    data.update({"code": True})
    return data
 

@api_bp.route("<guild_id>/emoji_select_options/<embed_type>", methods=["GET"])
async def get_emoji_select_options(guild_id: str, embed_type: str):
    if request.method == "GET":
        data = get_api_request_data()
        if not data.get("code"):
            return data
        data: dict = get_data("embeds").get(guild_id)
        if data is not None:
            data = data.get(f"{str(embed_type)}")
            banner = "🟥" if data.get("banner") is None else "🟩"
            try:
                title = "🟥" if data.get("main").get("title") is None else "🟩"
            except AttributeError:
                title = "🟥"
            try:
                description = "🟥" if data.get("main").get("description") is None else "🟩"
            except AttributeError:
                description = "🟥"
            try:
                image = "🟥" if data.get("main").get("image") is None else "🟩"
            except AttributeError:
                image = "🟥"
            try:
                color = "🟥" if data.get("main").get("color") is None else "🟩"
            except AttributeError:
                color = "🟥"
    return {
        "emoji_banner": banner,
        "emoji_title": title,
        "emoji_description": description,
        "emoji_image": image,
        "emoji_color": color 
    }
                

@api_bp.route("/<guild_id>/embeds_data", methods=["GET", "POST", "DELETE"])
async def execute_embeds_data(guild_id: str):
    data = get_api_request_data()
    if not data.get("code"):
        return {
            "code": 401,
            "message": "Unauthorizated user"
        }
        
    if request.method == "GET":
        server_data: dict = get_data("embeds").get(guild_id)
        return server_data

    elif request.method == "POST":
        server_data: dict = get_data("embeds")
        embed_type = data.get("data")[0]
        data_type = data.get("data")[1]
        field_value = data.get("data")[2]
        if server_data.get(guild_id) is None:
            temp = {
                "main": {
                    data_type: field_value
                }
            } if data_type != "banner" else {
                "banner": {
                    "image": {
                        "url": field_value
                    }
                }
            }
            execute_data = {
                guild_id: {
                    embed_type: temp
                }
            }
            server_data.update(execute_data)
        else:
            execute_data: dict = server_data.get(guild_id).get(embed_type)
            if data_type != "banner":
                execute_data.get("main").update({data_type: field_value}) if execute_data.get("main") is not None else execute_data.update({"main": {data_type: field_value}})
            else:
                execute_data.update({
                    "banner": {
                        "image": {
                            "url": field_value
                        }
                    }
                })
            server_data.get(guild_id).get(embed_type).update(execute_data)
        update_data("embeds", server_data)
        return {
            "code": 200
        }
    
    elif request.method == "DELETE":
        server_data: dict = get_data("embeds")
        embed_type = data.get("data")[0]
        data_type = data.get("data")[1]
        field_value = data.get("data")[2]
        if data_type == "banner":
            del server_data.get(guild_id).get(embed_type)[data_type]
        else:
            del server_data.get(guild_id).get(embed_type).get("main")[data_type]
            if len(server_data.get(guild_id).get(embed_type).get("main")) == 0: 
                del server_data.get(guild_id).get(embed_type)["main"]
        update_data("embeds", server_data)
        return {
            "code": 200
        }
    

@api_bp.route("<guild_id>/tickets_moderation", methods=["GET", "POST", "DELETE"])
async def tickets_moderation(guild_id: str):
    data = get_api_request_data()
    if not data.get("code"):
        return {
            "code": 401,
            "message": "Unauthorizated user"
        }
        
    if request.method == "GET":
        async with sql.connect(db_path) as db:
            cursor = await db.cursor()
            roles = await cursor.execute("SELECT role_id FROM guild_tickets_moderation WHERE guild_id = (?)", (int(guild_id),))
            roles = await roles.fetchall()
            return {
                "roles": roles
            }
        
    elif request.method == "POST":  
        async with sql.connect(db_path) as db:
            cursor = await db.cursor()
            roles = data.get("data")[0].split(", ")
            for role in roles:
                role = int(role)
                fetch_role = await cursor.execute(
                    "SELECT role_id FROM guild_tickets_moderation WHERE guild_id = (?) AND role_id = (?)",
                    (int(guild_id), role,)    
                )
                fetch_role = await fetch_role.fetchone()
                if fetch_role is None:
                    await cursor.execute(
                        "INSERT INTO guild_tickets_moderation VALUES (?,?)",
                        (int(guild_id), role,)
                    )
                else:
                    cursor = await db.cursor()
                    await cursor.execute(f"DELETE FROM guild_tickets_moderation WHERE {data.get('column')} = (?)", (data.get("value")))
                    await db.commit()
                await db.commit()
        return {
            "code": 200
        }
