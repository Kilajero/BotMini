# - *- coding: utf- 8 - *-
import asyncio
import datetime
import time

import requests
from aiogram import Dispatcher
from bs4 import BeautifulSoup
from admin_panel.entities.admin import Admin
from data.config import bot_version, bot_description
from loader import bot
from utils.db_api.sqlite import get_settingsx, update_settingsx


# Уведомление и проверка обновления при запуске скрипта
async def on_startup_notify(dp: Dispatcher):
    if len(Admin.admins()) >= 1:
        update_link = "https://example.com"

        response = requests.get(update_link)
        soup_parse = BeautifulSoup(response.text, "html.parser")
        await send_all_admin(f"<b>✅ Бот был успешно запущен</b>\n"
                                 f"➖➖➖➖➖➖➖➖➖➖\n"
                                 f"{bot_description}")


# Рассылка сообщения всем администраторам
async def send_all_admin(message, markup=None, not_me=0):
    if markup is None:
        for admin in Admin.admins():
            try:
                if str(admin) != str(not_me):
                    await bot.send_message(chat_id=admin, text=message, reply_markup=reply_markup1, disable_web_page_preview=True)
            except:
                pass
    else:
        for admin in Admin.admins():
            try:
                if str(admin) != str(not_me):
                    await bot.send_message(chat_id=admin, text=message, reply_markup=markup, disable_web_page_preview=True)
            except:
                pass


# Очистка имени пользователя от тэгов
def clear_firstname(firstname):
    if "<" in firstname: firstname = firstname.replace("<", "*")
    if ">" in firstname: firstname = firstname.replace(">", "*")
    return firstname


# Проверка на обновление счётчика 24-х часов при запуске
def update_profit():
    settings = get_settingsx()
    now_unix = int(time.time())
    if now_unix - int(settings[4]) >= 86400:
        update_settingsx(profit_buy=now_unix)
    if now_unix - int(settings[5]) >= 86400:
        update_settingsx(profit_refill=now_unix)


# Автоматическая ежечасовая проверка на обновление счётчика 24-х часов
async def update_last_profit():
    while True:
        await asyncio.sleep(3600)
        settings = get_settingsx()
        now_unix = int(time.time())
        if now_unix - int(settings[4]) >= 86400:
            update_settingsx(profit_buy=now_unix)
        if now_unix - int(settings[5]) >= 86400:
            update_settingsx(profit_refill=now_unix)


# Автоматическая проверка обновления каждые 24 часа
async def check_update_bot():
    while True:
        await asyncio.sleep(86400)
        update_link = "https://example.com"

        response = requests.get(update_link)
        soup_parse = BeautifulSoup(response.text, "html.parser")
        get_bot_info = soup_parse.select("p[class$='CDt4Ke zfr3Q']")[0].text.split("=")
        if float(get_bot_info[0]) > float(bot_version):
            update_description = get_bot_info[2].split("**")
            update_description = "\n".join(update_description)
            await send_all_admin(f"<b>❇ Вышло обновление ❇</b>\n"
                                 f"▶ <a href='{get_bot_info[1]}'><b>Скачать обновление</b></a>\n"
                                 f"➖➖➖➖➖➖➖➖➖➖\n"
                                 f"{update_description}")

# Получение текущей даты
def get_dates():
    return datetime.datetime.today().replace(microsecond=0)
