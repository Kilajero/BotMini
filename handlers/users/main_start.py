# - *- coding: utf- 8 - *-
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
import json
from filters import IsWork, IsUser
from filters.all_filters import IsBuy
from keyboards.default import check_user_out_func
from loader import dp, bot
from states import StorageUsers
from utils.db_api.sqlite import *
from utils.other_func import clear_firstname, get_dates
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
prohibit_buy = ["xbuy_item", "not_buy_items", "buy_this_item", "buy_open_position", "back_buy_item_position",
                "buy_position_prevp", "buy_position_nextp", "buy_category_prevp", "buy_category_nextp",
                "back_buy_item_to_category", "buy_open_category"]

class captcha(StatesGroup):
    captcha_text = State()
# Проверка на нахождение бота на технических работах
@dp.message_handler(IsWork(), state="*")
@dp.callback_query_handler(IsWork(), state="*")
async def send_work_message(message: types.Message, state: FSMContext):
    if "id" in message:
        await message.answer("🔴 Бот находится на технических работах.")
    else:
        await message.answer("<b>🔴 Бот находится на технических работах.</b>")




keyboard = InlineKeyboardMarkup()
button = InlineKeyboardButton("🤖Я не робот🤖", callback_data="www_capcha")
keyboard.add(button)

@dp.message_handler(CommandStart(), state="*")
async def bot_startЕ(message: types.Message, state: FSMContext):
    with open('db.json', 'r', encoding='utf-8') as file:
        db_data=json.load(file)
    if db_data['CAPCHA_STATUS'] == 'ON':
        return await message.answer(db_data['CAPCHA_TEXT'], reply_markup=keyboard)
    await state.finish()
    first_name = clear_firstname(message.from_user.first_name)
    get_user_id = get_userx(user_id=message.from_user.id)
    if get_user_id is None:
        if message.from_user.username is not None:
            get_user_login = get_userx(user_login=message.from_user.username)
            if get_user_login is None:
                add_userx(message.from_user.id, message.from_user.username.lower(), first_name, 0, 0, get_dates())
            else:
                delete_userx(user_login=message.from_user.username)
                add_userx(message.from_user.id, message.from_user.username.lower(), first_name, 0, 0, get_dates())
        else:
            add_userx(message.from_user.id, message.from_user.username, first_name, 0, 0, get_dates())
    else:
        if first_name != get_user_id[3]:
            update_userx(get_user_id[1], user_name=first_name)
        if message.from_user.username is not None:
            if message.from_user.username.lower() != get_user_id[2]:
                update_userx(get_user_id[1], user_login=message.from_user.username.lower())

    await message.answer("<b>🔸 Бот готов к использованию.</b>\n"
                         "🔸 Если не появились вспомогательные кнопки\n"
                         "▶ Введите /start",
                         reply_markup=check_user_out_func(message.from_user.id))
@dp.callback_query_handler(lambda callback_query: callback_query.data == "www_capcha", state="*")
async def handle_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete() 
    await state.finish()
    first_name = clear_firstname(callback_query.from_user.first_name)
    get_user_id = get_userx(user_id=callback_query.from_user.id)
    if get_user_id is None:
        if callback_query.from_user.username is not None:
            get_user_login = get_userx(user_login=callback_query.from_user.username)
            if get_user_login is None:
                add_userx(callback_query.from_user.id, callback_query.from_user.username.lower(), first_name, 0, 0, get_dates())
            else:
                delete_userx(user_login=callback_query.from_user.username)
                add_userx(callback_query.from_user.id, callback_query.from_user.username.lower(), first_name, 0, 0, get_dates())
        else:
            add_userx(callback_query.from_user.id, callback_query.from_user.username, first_name, 0, 0, get_dates())
    else:
        if first_name != get_user_id[3]:
            update_userx(get_user_id[1], user_name=first_name)
        if callback_query.from_user.username is not None:
            if callback_query.from_user.username.lower() != get_user_id[2]:
                update_userx(get_user_id[1], user_login=callback_query.from_user.username.lower())

    await callback_query.message.answer("<b>🔸 Бот готов к использованию.</b>\n"
                         "🔸 Если не появились вспомогательные кнопки\n"
                         "▶ Введите /start",
                         reply_markup=check_user_out_func(callback_query.from_user.id))

keyboard2 = InlineKeyboardMarkup(row_width=2)
button2 = InlineKeyboardButton("Включить", callback_data="www_capcha_on")
keyboard2.add(button2)
button2 = InlineKeyboardButton("Выключить", callback_data="www_capcha_off")
keyboard2.add(button2)
button2 = InlineKeyboardButton("Изменить текст", callback_data="www_capcha_edit_text")
keyboard2.add(button2)
@dp.message_handler(text="🤖CAPTCHA🤖")
async def bot_captcha_settings(message: types.Message, state: FSMContext):
    await message.answer('⚙️Настройки капчи:', reply_markup=keyboard2)

@dp.callback_query_handler(lambda callback_query: callback_query.data == "www_capcha_on")
async def handle_callback_captcha_on(callback_query: types.CallbackQuery, state: FSMContext):
    with open('db.json', 'r', encoding='utf-8') as file:
        db_data=json.load(file)
    db_data['CAPCHA_STATUS'] = 'ON'
    with open('db.json', 'w') as file:
        json.dump(db_data,file)
    await callback_query.message.answer('✅CAPTCHA включена✅')

@dp.callback_query_handler(lambda callback_query: callback_query.data == "www_capcha_off")
async def handle_callback_captcha_off(callback_query: types.CallbackQuery, state: FSMContext):
    with open('db.json', 'r', encoding='utf-8') as file:
        db_data=json.load(file)
    db_data['CAPCHA_STATUS'] = 'OFF'
    with open('db.json', 'w') as file:
        json.dump(db_data,file)
    await callback_query.message.answer('✅CAPTCHA выключена✅')

@dp.callback_query_handler(lambda callback_query: callback_query.data == "www_capcha_edit_text")
async def handle_callback_capcha_edit_text(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete() 
    await callback_query.message.answer('👇Введите текст капчи👇')
    await captcha.captcha_text.set()

@dp.message_handler(state=captcha.captcha_text)
async def process_name(message: types.Message, state: FSMContext):
    text = message.text
    with open('db.json', 'r', encoding='utf-8') as file:
        db_data=json.load(file)
    db_data['CAPCHA_TEXT'] = text
    with open('db.json', 'w') as file:
        json.dump(db_data,file)
    await state.finish()
    await message.answer('✅CAPTCHA текст изменен✅')
# Обработка кнопки "На главную" и команды "/start"
@dp.message_handler(text="⬅ На главную", state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    first_name = clear_firstname(message.from_user.first_name)
    get_user_id = get_userx(user_id=message.from_user.id)
    if get_user_id is None:
        if message.from_user.username is not None:
            get_user_login = get_userx(user_login=message.from_user.username)
            if get_user_login is None:
                add_userx(message.from_user.id, message.from_user.username.lower(), first_name, 0, 0, get_dates())
            else:
                delete_userx(user_login=message.from_user.username)
                add_userx(message.from_user.id, message.from_user.username.lower(), first_name, 0, 0, get_dates())
        else:
            add_userx(message.from_user.id, message.from_user.username, first_name, 0, 0, get_dates())
    else:
        if first_name != get_user_id[3]:
            update_userx(get_user_id[1], user_name=first_name)
        if message.from_user.username is not None:
            if message.from_user.username.lower() != get_user_id[2]:
                update_userx(get_user_id[1], user_login=message.from_user.username.lower())

    await message.answer("<b>🔸 Бот готов к использованию.</b>\n"
                         "🔸 Если не появились вспомогательные кнопки\n"
                         "▶ Введите /start",
                         reply_markup=check_user_out_func(message.from_user.id))


@dp.message_handler(IsUser(), state="*")
@dp.callback_query_handler(IsUser(), state="*")
async def send_user_message(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id,
                           "<b>❗ Ваш профиль не был найден.</b>\n"
                           "▶ Введите /start")


# Проверка на доступность покупок
@dp.message_handler(IsBuy(), text="🎁 Купить", state="*")
@dp.message_handler(IsBuy(), state=StorageUsers.here_input_count_buy_item)
@dp.callback_query_handler(IsBuy(), text_startswith=prohibit_buy, state="*")
async def send_user_message(message, state: FSMContext):
    if "id" in message:
        await message.answer("🔴 Покупки в боте временно отключены", True)
    else:
        await message.answer("<b>🔴 Покупки в боте временно отключены</b>")
