# - *- coding: utf- 8 - *-
from aiogram.dispatcher.filters.state import State, StatesGroup


class StorageQiwi(StatesGroup):
    here_input_qiwi_secret = State()
    here_input_qiwi_login = State()
    here_input_qiwi_token = State()
    here_input_qiwi_amount = State()
    here_input_apirone_amount = State()
    here_input_apirone_token = State()
    here_input_apirone_login = State()
    here_input_apirone_secret = State()
    here_input_karta_login = State()
