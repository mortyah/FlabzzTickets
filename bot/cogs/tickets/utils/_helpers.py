import os

import disnake


def get_translate_data(data_type: str):
    match data_type:
        case "banner":
            return "Баннер"
        case "image":
            return "Изображение"
        case "description":
            return "Описание"
        case "title":
            return "Заголовок"
        case "color":
            return "Цвет"
        
def get_translate_embeds(embed_type: str):
    match embed_type:
        case "open_ticket":
            return "Открыть Тикет"
        case "ticket_reply":
            return "Ответ на Тикет"
        case "ticket_log":
            return "Лог Тикетов"
        
def get_translate_data_of_label(data_type: str):
    match data_type:
        case "banner":
            return "Введите URL Баннера:"
        case "image":
            return "Введите URL Изображения:"
        case "description":
            return "Введите текст Описания:"
        case "title":
            return "Введите текст Заголовка"
        case "color":
            return "Введите HEX-code Цвета:"
        
def get_translate_data_of_placeholder(data_type: str):
    match data_type:
        case "banner" | "image":
            return "Example: https://media.tenor.com/../anime.gif"
        case "description":
            return "Example: Приветствуем вас, {user}!"
        case "title":
            return "Example: Вы открыли тикет!"
        case "color":
            return "Example: 37FF37"
    
    
def get_data_type_options(data: dict):
    return [
        disnake.SelectOption(
            label="Banner",
            value="banner",
            description="Настроить баннер эмбеда.",
            emoji=data.get("emoji_banner")
        ),
        disnake.SelectOption(
            label="Title",
            value="title",
            description="Настроить заголовок эмбеда.",
            emoji=data.get("emoji_title")
        ),
        disnake.SelectOption(
            label="Description",
            value="description",
            description="Настроить описание эмбеда.",
            emoji=data.get("emoji_description")
        ),
        disnake.SelectOption(
            label="Image",
            value="image",
            description="Настроить изображение эмбеда.",
            emoji=data.get("emoji_image")
        ),
        disnake.SelectOption(
            label="Color",
            value="color",
            description="Настроить цвет эмбеда.",
            emoji=data.get("emoji_color")
        )
    ]