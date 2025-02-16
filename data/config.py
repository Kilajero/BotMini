# - *- coding: utf- 8 - *-
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")
BOT_TOKEN = config["settings"]["token"]
main_admin = config["settings"]["main_admin"]
withdraw_ltc = config["settings"]["withdraw_ltc"]
withdraw_usdt = config["settings"]["withdraw_usdt"]
bot_description = '1'
bot_version = "00.00"

