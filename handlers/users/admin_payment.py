# - *- coding: utf- 8 - *-
import asyncio
import json

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from pyqiwip2p import QiwiP2P

from admin_panel.filters import IsAdmin
from keyboards.default import payment_default
from keyboards.inline import choice_way_input_payment_func
from loader import dp, bot
from states import StorageQiwi
from utils import send_all_admin, clear_firstname
from utils.db_api.sqlite import get_paymentx, update_paymentx


###################################################################################
########################### ВКЛЮЧЕНИЕ/ВЫКЛЮЧЕНИЕ ПОПОЛНЕНИЯ #######################
# Включение пополнения
@dp.message_handler(IsAdmin(), text="🔴 Выключить пополнения", state="*")
async def turn_off_refill(message: types.Message, state: FSMContext):
    await state.finish()
    update_paymentx(status="False")
    await message.answer("<b>🔴 Пополнения в боте были выключены.</b>",
                         reply_markup=payment_default())
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🔴 Выключил пополнения в боте.", not_me=message.from_user.id)


# Выключение пополнения
@dp.message_handler(IsAdmin(), text="🟢 Включить пополнения", state="*")
async def turn_on_refill(message: types.Message, state: FSMContext):
    await state.finish()
    update_paymentx(status="True")
    await message.answer("<b>🟢 Пополнения в боте были включены.</b>",
                         reply_markup=payment_default())
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🟢 Включил пополнения в боте.", not_me=message.from_user.id)

@dp.message_handler(IsAdmin(), text="🔴 Выключить apirone", state="*")
async def turn_off_refill(message: types.Message, state: FSMContext):
    await state.finish()
    update_paymentx(apirone_status="False")
    await message.answer("<b>🔴 Пополнения apirone в боте были выключены.</b>",
                         reply_markup=payment_default())
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🔴 Выключил пополнения apirone в боте.", not_me=message.from_user.id)


# Выключение пополнения
@dp.message_handler(IsAdmin(), text="🟢 Включить apirone", state="*")
async def turn_on_refill(message: types.Message, state: FSMContext):
    await state.finish()
    update_paymentx(apirone_status="True")
    await message.answer("<b>🟢 Пополнения apirone в боте были включены.</b>",
                         reply_markup=payment_default())
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🟢 Включил пополнения apirone в боте.", not_me=message.from_user.id)
@dp.message_handler(IsAdmin(), text="🔴 Выключить банк трансфер", state="*")
async def turn_off_refill(message: types.Message, state: FSMContext):
    await state.finish()
    update_paymentx(karta_status="False")
    await message.answer("<b>🔴 Пополнения банк трансфер в боте были выключены.</b>",
                         reply_markup=payment_default())
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🔴 Выключил пополнения банк трансфер в боте.", not_me=message.from_user.id)


# Выключение пополнения
@dp.message_handler(IsAdmin(), text="🟢 Включить банк трансфер", state="*")
async def turn_on_refill(message: types.Message, state: FSMContext):
    await state.finish()
    update_paymentx(karta_status="True")
    await message.answer("<b>🟢 Пополнения банк трансфер в боте были включены.</b>",
                         reply_markup=payment_default())
    await send_all_admin(
        f"👤 Администратор <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>\n"
        "🟢 Включил пополнения банк трансфер в боте.", not_me=message. from_user.id)
###################################################################################
############################# ВЫБОР СПОСОБА ПОПОЛНЕНИЯ ############################
# Выбор способа пополнения
@dp.callback_query_handler(IsAdmin(), text_startswith="change_payment:")
async def input_amount(call: CallbackQuery):
    way_pay = call.data[15:]
    change_pass = False
    get_payment = get_paymentx()
    if way_pay == "nickname":
        try:
            request = requests.Session()
            request.headers["authorization"] = "Bearer " + get_payment[1]
            get_nickname = request.get(f"https://edge.qiwi.com/qw-nicknames/v1/persons/{get_payment[0]}/nickname")
            check_nickname = json.loads(get_nickname.text).get("nickname")
            if check_nickname is None:
                await call.answer("❗ На аккаунте отсутствует QIWI Никнейм")
            else:
                update_paymentx(qiwi_nickname=check_nickname)
                change_pass = True
        except json.decoder.JSONDecodeError:
            await call.answer("❗ QIWI кошелёк не работает.\n❗ Как можно быстрее установите его", True)
    else:
        change_pass = True
    if change_pass:
        update_paymentx(way_payment=way_pay)


###################################################################################
####################################### QIWI ######################################
# Изменение QIWI кошелька
@dp.message_handler(IsAdmin(), text="🤍 Изменить PayPal 🖍", state="*")
async def change_qiwi_login(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>🤍 Введите</b> <code>Client ID</code> <b>PayPal кошелька🖍 </b>")
    await StorageQiwi.here_input_qiwi_login.set()
@dp.message_handler(IsAdmin(), text="🔵 Изменить apirone 🖍", state="*")
async def change_qiwi_login(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>🔵 Введите</b> <code>Account ID</code> <b>APIRONE кошелька🖍 </b>")
    await StorageQiwi.here_input_apirone_login.set()
@dp.message_handler(IsAdmin(), text="🔵 Изменить банк трансфер 🖍", state="*")
async def change_qiwi_login(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>🔵 Введите <code>новый текст</code></b>")
    await StorageQiwi.here_input_karta_login.set()
# Принятие логина для киви
@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_qiwi_login)
async def change_key_api(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["here_input_qiwi_login"] = message.text
    await message.answer("<b>Введите</b> <code>Secret ID</code> <b>QIWI кошелька 🖍</b>\n",
                         disable_web_page_preview=True)
    await StorageQiwi.here_input_qiwi_token.set()
# APIRONEEDIT
@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_apirone_login)
async def change_key_api(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["here_input_apirone_login"] = message.text
    await message.answer("<b>Введите</b> <code>Transfer Key</code> <b>APIRONE кошелька 🖍</b>\n",
                         disable_web_page_preview=True)
    await StorageQiwi.here_input_apirone_token.set()

# Принятие токена для киви
@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_qiwi_token)
async def change_secret_api(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["here_input_qiwi_token"] = message.text
    await message.answer("<b>Введите</b> <code>Секретный ключ 🖍</code>\n",
                         disable_web_page_preview=True)
    await StorageQiwi.here_input_qiwi_secret.set()
@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_karta_login)
async def change_secret_api(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["here_input_karta_login"] = message.text
    await message.answer("✅ текст был добавлен\n",
                         disable_web_page_preview=True)
    update_paymentx(karta=message.text)
    await state.finish()
# Принятие токена для киви
@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_apirone_token)
async def change_secret_api(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        qiwi_login = data["here_input_apirone_login"]
        qiwi_token = message.text
    qiwi_private_key = message.text
    update_paymentx(apirone_key=qiwi_login, apirone_transfer=qiwi_token)
    await message.answer("<b>APIRONE токен был успешно изменён ✅</b>",
                            reply_markup=payment_default())
    await state.finish()
# Принятие приватного ключа для киви
@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_qiwi_secret)
async def change_secret_api(message: types.Message, state: FSMContext):
    secrey_key_error = False
    async with state.proxy() as data:
        qiwi_login = data["here_input_qiwi_login"]
        qiwi_token = data["here_input_qiwi_token"]
    qiwi_private_key = message.text
    update_paymentx(qiwi_login=qiwi_login, qiwi_token=qiwi_token,
                    qiwi_private_key=qiwi_private_key)
    await message.answer("<b>PayPal токен был успешно изменён ✅</b>",
                            reply_markup=payment_default())
    await state.finish()

@dp.message_handler(IsAdmin(), state=StorageQiwi.here_input_apirone_secret)
async def change_secret_api(message: types.Message, state: FSMContext):
    secrey_key_error = False
    async with state.proxy() as data:
        qiwi_login = data["here_input_apirone_login"]
        qiwi_token = data["here_input_apirone_token"]
    qiwi_private_key = message.text
    update_paymentx(apirone_key=qiwi_login, apirone_transfer=qiwi_token)
    await message.answer("<b>APIRONE токен был успешно изменён ✅</b>",
                            reply_markup=payment_default())
    await state.finish()
