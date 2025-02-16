# - *- coding: utf- 8 - *-
from aiogram.types import ReplyKeyboardMarkup

from utils.db_api.sqlite import get_paymentx


def payment_default():
    payment = get_paymentx()
    payment_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    payment_kb.row("🤍 Изменить PayPal 🖍")
    if payment[5] == "True":
        payment_kb.row("🔴 Выключить пополнения")
    else:
        payment_kb.row("🟢 Включить пополнения")
    payment_kb.row("🔵 Изменить apirone 🖍")
    if payment[6] == "True":
        payment_kb.row("🔴 Выключить apirone")
    else:
        payment_kb.row("🟢 Включить apirone")
    payment_kb.row("🔵 Изменить банк трансфер 🖍")
    if payment[8] == "True":
        payment_kb.row("🔴 Выключить банк трансфер")
    else:
        payment_kb.row("🟢 Включить банк трансфер")
    payment_kb.row("⬅ На главную")
    return payment_kb
