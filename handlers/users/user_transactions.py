# - *- coding: utf- 8 - *-
import json
import random
import time

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from pyqiwip2p import QiwiP2P

from keyboards.default import all_back_to_main_default, check_user_out_func
from keyboards.inline import *
from loader import dp, bot
from states.state_payment import StorageQiwi
from utils import send_all_admin, clear_firstname, get_dates
from utils.db_api.sqlite import update_userx, get_refillx, add_refillx
import paypalrestsdk
from data import config

client_id="Client ID"
secret="Secret"
KARTA_PAYMENT = "4444444444444444444"
class Payment:
	def __init__(self, client_id: str, secret: str, mode: str = "sandbox"):
		paypalrestsdk.configure({
			"mode": mode,
			"client_id": client_id,
			"client_secret": secret
		})

	def createPayment(self, count: str = "10.00", currency: str = "USD", 
					  redirect_urls: dict = None, description: str = "desc"):
		
		if redirect_urls is None:
			redirect_urls = {
				"return_url": "https://example.com/payment/execute",
				"cancel_url": "https://example.com/payment/cancel"
			}

		# Создание платежа
		payment = paypalrestsdk.Payment({
			"intent": "sale",
			"payer": {
				"payment_method": "paypal"
			},
			"redirect_urls": {
				"return_url": redirect_urls.get("return_url"),  # URL для успешного завершения
				"cancel_url": redirect_urls.get("cancel_url")   # URL для отмены
			},
			"transactions": [{
				"amount": {
					"total": count,
					"currency": currency
				},
				"description": description
			}]
		})

		# Попытка создать платеж
		if payment.create():
			# Получаем PayId
			pay_id = payment.id
			print(f"PayId: {pay_id}")

			# Получаем ссылку для оплаты
			for link in payment.links:
				if link.rel == "approval_url":
					print("Ссылка для оплаты: {}".format(link.href))
					return (pay_id, link.href)
		else:
			print("Ошибка при создании платежа:")
			print(payment.error)

	def get_payment_status(self, payment_id):
		try:
			# Поиск платежа по его ID
			payment = paypalrestsdk.Payment.find(payment_id)
			
			if payment:
				# Вывод информации о платеже в формате dict
				payment_dict = payment.to_dict()

				# Получаем статус платежа
				status = payment_dict.get("state", "unknown")
				
				return {
					"status": status,
					"payment_data": payment_dict
				}
			else:
				print("Платеж не найден!")
				return None
		except paypalrestsdk.ResourceNotFound as error:
			print(f"Ошибка: Платеж с ID {payment_id} не найден!")
			return None
# Создание платежей APIRONE
import requests, segno
def apirone_create_invoice(summ, account_id):
    s = requests.post(f"https://apirone.com/api/v2/accounts/{account_id}/invoices",json={
        "amount": int(str(f'{summ}000000')),
        "currency": "usdt@trx",
        "lifetime": 3600000000,
        "callback_url": "http://t.me",
        "user-data": {
            "title": "Пополнение бота шоп",
            "merchant": "SHop Bot Popolnenie",
            "url": "http://telegram.org",
            "price": "$0",
            "items": [
                {"name": "Пополнение бота", "cost": "$0", "qty": 1, "total": "$0"},
            ],
            "extras": []
        },
        "linkback": "http://t.me"
    })
    print(s.json())
    address, amount = s.json()['address'], s.json()['amount']
    qr = segno.make(f'litecoin:{address}?amount={amount/1000000}').save('qr.png', scale=7)

    return s.json()['invoice'], s.json()['invoice-url'], address, amount
def apirone_create_invoice_ltc(summ, account_id):
    cof = requests.get('https://apirone.com/api/v2/ticker?currency=ltc&fiat=usd').json()['usd']
    print(cof)
    dollar = summ
    summ = (summ / cof)*100000000
    print(summ)
    s = requests.post(f"https://apirone.com/api/v2/accounts/{account_id}/invoices",json={
        "amount": int(summ),
        "currency": "ltc",
        "lifetime": 3600000000,
        "callback_url": "http://t.me",
        "user-data": {
            "title": "Пополнение бота шоп",
            "merchant": "SHop Bot Popolnenie",
            "url": "http://telegram.org",
            "price": "$0",
            "items": [
                {"name": "Пополнение бота", "cost": "$0", "qty": 1, "total": "$0"},
            ],
            "extras": []
        },
        "linkback": "http://t.me"
    })
    print(s.json())
    address, amount = s.json()['address'], s.json()['amount']
    qr = segno.make(f'litecoin:{address}?amount={amount/1000000}').save('qr.png', scale=7)

    return s.json()['invoice'], s.json()['invoice-url'], address, amount
def apirone_status(account, transfer_key, invoice):
    s = requests.get(f"https://apirone.com/api/v2/invoices/{invoice}")
    return s.json()['invoice'], s.json()['invoice-url']
@dp.callback_query_handler(text="user_input")
async def input_amount(call: CallbackQuery, state: FSMContext):
    print('s')
    get_payment = get_paymentx()
    await call.message.edit_text(f"Введите пожалуйста сумму пополнения: ($)")
    await StorageQiwi.here_input_qiwi_amount.set()
@dp.message_handler(state=StorageQiwi.here_input_qiwi_amount)
async def input_amount(message: types.Message, state: FSMContext):
    UserID = message.from_user.id
    summ = int(message.text.lower())
    get_payment = get_paymentx()
    data = []
    if summ > 1:
        pass
    else:
        return await message.answer(f"Сумма не может быть меньше 2 USD\nПопробуйте еще раз!")
    if get_payment[5] == 'True':
        data.append([InlineKeyboardButton(text=f"🤍 PayPal", callback_data=f"paypal{summ}")])
    if get_payment[6] == 'True':
        data.append([InlineKeyboardButton(text=f"🔵 USDT", callback_data=f"apirone{summ}")])
    if get_payment[6] == 'True':
        data.append([InlineKeyboardButton(text=f"🔵 LTC", callback_data=f"ltc_apirone{summ}")])
    if get_payment[8] == 'True':
        data.append([InlineKeyboardButton(text=f"🟡 Банк трансфер", callback_data=f"karta{summ}")])
    if len(data) == 0:
        await state.finish()
        await message.answer(f"🔵🤍🟡 К сожелению, платежные системы сейчас недоступны!")
        return
    await message.answer(f"Выберите способ оплаты",
    reply_markup=InlineKeyboardMarkup(inline_keyboard=data))
    await state.finish()
@dp.callback_query_handler(text_startswith="paypal")
async def input_amount(call: CallbackQuery):
    UserID = call.from_user.id
    summ = int(call.data.replace('paypal', ''))
    get_payment = get_paymentx()
    if get_payment[5] == 'True':
        pass
    else:
        return await call.answer(f"PayPal временно недоступен!")
    if 1:
        payment = Payment(client_id=get_payment[0], secret=get_payment[1])
        check = payment.createPayment(count=summ, currency="USD", description=f"{UserID}")
    if 2+2==2:
        check = (1, 'error.com')
    await call.message.edit_text(f"Счет для оплаты {summ} USD", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
         [InlineKeyboardButton(text=f"Оплатить", url=str(check[1])),
         InlineKeyboardButton(text=f"Проверить", callback_data="1check" + str(check[0]))]
    ]))
# Выдача счета APIRONE USDT
@dp.callback_query_handler(text_startswith="apirone")
async def input_amount(call: CallbackQuery):
    UserID = call.from_user.id
    summ = int(call.data.replace('apirone', ''))
    get_payment = get_paymentx()
    if get_payment[6] == 'True':
        pass
    else:
        return await call.answer(f"apirone временно недоступен!")
    invoice, link, address, amount = apirone_create_invoice(summ, account_id=get_payment[7])
    await bot.send_photo(UserID, open('qr.png', 'rb'), f'Ваш счет создан!\n\nID: <code>{invoice}</code>\nСумма: {amount/1000000} USDT\nАдрес: <code>{address}</code>', reply_markup=InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [       
            # InlineKeyboardButton(text=f"Оплата", url=link),
            InlineKeyboardButton(text=f"Проверить оплату", callback_data=f'check_apirone{invoice}+{summ}')
        ]
    ]))
    await call.message.delete()
# Выдача счета APIRONE LTC
@dp.callback_query_handler(text_startswith="ltc_apirone")
async def input_amount(call: CallbackQuery):
    UserID = call.from_user.id
    summ = int(call.data.replace('ltc_apirone', ''))
    get_payment = get_paymentx()
    if get_payment[6] == 'True':
        pass
    else:
        return await call.answer(f"apirone временно недоступен!")
    invoice, link, address, amount = apirone_create_invoice_ltc(summ, account_id=get_payment[7])
    await bot.send_photo(UserID, open('qr.png', 'rb'), f'Ваш счет создан!\n\nID: <code>{invoice}</code>\nСумма: {amount/100000000} LTC\nАдрес: <code>{address}</code>', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [       
            # InlineKeyboardButton(text=f"Оплата", url=link),
            InlineKeyboardButton(text=f"Проверить оплату", callback_data=f'check_apirone{invoice}+{summ}')
        ]
    ]))
    await call.message.delete()
@dp.callback_query_handler(text_startswith="karta")
async def input_amount(call: CallbackQuery):
    UserID = call.from_user.id
    summ = int(call.data.replace('karta', ''))
    get_payment = get_paymentx()
    if get_payment[8] == 'True':
        pass
    else:
        return await call.answer(f"банк трансфер временно недоступен!")
    await call.message.edit_text(f"""
{get_payment[9]}
""", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [       
            InlineKeyboardButton(text=f"💳 Проверить оплату", callback_data=f'check_karta{summ}')
        ]
    ]))
@dp.callback_query_handler(text_startswith = "check_karta")
async def input_amount(call: CallbackQuery, state: FSMContext):
    check = call.data.replace('check_karta', '')
    await send_all_admin(f"""
💸 Пополнение (вручное)

У него должен быть комментарий:
Комменатрий: <code>{call.from_user.id} my username {call.from_user.username}</code>
Сумма: {check} USD

""", markup=InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=f"💸 Да, он оплатил", callback_data=f"addbalance+{call.from_user.id}+{check}")]
]))
@dp.callback_query_handler(text_startswith = "addbalance")
async def input_amount(call: CallbackQuery, state: FSMContext):
    UserID = call.data.split('+')[1]
    summ = call.data.split('+')[2]
    get_user_info = get_userx(user_id=UserID)
    update_userx(UserID, balance=int(get_user_info[4]) + int(summ), all_refill=int(get_user_info[5]) + int(summ))
    await call.message.edit_text(f"Успешно выдали ему {summ} USD")
@dp.callback_query_handler(text_startswith = "check_apirone")
async def input_amount(call: CallbackQuery, state: FSMContext):
    check = call.data.split('+')[0].replace('check_apirone', '')
    summ = call.data.split('+')[1]
    get_payment = get_paymentx()
    print(check)
    print(summ)
    status, li = apirone_status(get_payment[7], get_payment[10], check)
    get_user_info = get_userx(user_id=call.from_user.id)
    if status == 'paid':
        update_userx(call.from_user.id, balance=int(get_user_info[4]) + int(summ), all_refill=int(get_user_info[5]) + int(summ))
        get_payment = get_paymentx()
        s = requests.post(f"https://apirone.com/api/v2/accounts/{get_payment[7]}/transfer",json={
        "transfer-key": get_payment[10],
        "currency": "ltc",
        "destinations": {
             {
                  "adress": config.withdraw_ltc
             }
        }
        })
        print(s)
        s = requests.post(f"https://apirone.com/api/v2/accounts/{get_payment[7]}/transfer",json={
        "transfer-key": get_payment[10],
        "currency": "usdt",
        "destinations": {
             {
                  "adress": config.withdraw_usdt
             }
        }
        })
        print(s)
        await call.message.delete()
        await call.message.answer("Успешно!")
    else:
        return await call.answer(f"Счет не оплачен!")
@dp.callback_query_handler(text_startswith = "1check")
async def input_amount(call: CallbackQuery, state: FSMContext):
    check = call.data.replace('1check', '')
    payment = Payment(client_id=client_id, secret=secret)
    test = payment.get_payment_status(check)
    from pprint import pprint
    get_user_info = get_userx(user_id=call.from_user.id)
    transaction = test['payment_data']['transactions'][0]  # Полуаем первую транзачкцию
    print(test['status'] + transaction['amount']['total'])
    if test['status'] == 'completed':
        update_userx(call.from_user.id, balance=int(get_user_info[4]) + int(float(transaction['amount']['total'])), all_refill=int(get_user_info[5]) + int(float(transaction['amount']['total'])))
        await call.message.edit_text(f"✅ <i>Платеж прошел!, баланс был пополнен на +{transaction['amount']['total']} USD</i>")
    else:
        await call.answer(f"📵 Платеж не оплачен")
###################################################################################
############################## ВВОД СУММЫ ПОПОЛНЕНИЯ ##############################
# Выбор способа пополнения
@dp.callback_query_handler(text="1user_input", state="*")
async def input_amount(call: CallbackQuery, state: FSMContext):
    check_pass = False
    get_payment = get_paymentx()
    if get_payment[5] == "True":
        if get_payment[0] != "None" and get_payment[1] != "None" and get_payment[2] != "None":
            try:
                request = requests.Session()
                request.headers["authorization"] = "Bearer " + get_payment[1]
                response_qiwi = request.get(
                    f"https://edge.qiwi.com/payment-history/v2/persons/{get_payment[0]}/payments",
                    params={"rows": 1, "operation": "IN"})
                if response_qiwi.status_code == 200:
                    await StorageQiwi.here_input_qiwi_amount.set()
                    await bot.delete_message(call.from_user.id, call.message.message_id)
                    await call.message.answer("<b>💵 Введите сумму для пополнения средств 🥝</b>",
                                              reply_markup=all_back_to_main_default)
                else:
                    check_pass = True
            except json.decoder.JSONDecodeError:
                check_pass = True

            if check_pass:
                await bot.answer_callback_query(call.id, "❗ Пополнение временно недоступно")
                await send_all_admin(
                    f"👤 Пользователь <a href='tg://user?id={call.from_user.id}'>{clear_firstname(call.from_user.first_name)}</a> "
                    f"пытался пополнить баланс.\n"
                    f"<b>❌ QIWI кошелёк не работает. Срочно замените его.</b>")
        else:
            await bot.answer_callback_query(call.id, "❗ Пополнение временно недоступно")
            await send_all_admin(
                f"👤 Пользователь <a href='tg://user?id={call.from_user.id}'>{clear_firstname(call.from_user.first_name)}</a> "
                f"пытался пополнить баланс.\n"
                f"<b>❌ QIWI кошелёк недоступен. Срочно замените его.</b>")
    else:
        await bot.answer_callback_query(call.id, "❗ Пополнения в боте временно отключены")


###################################################################################
####################################### QIWI ######################################
# Принятие суммы для пополнения средств через QIWI
#@dp.message_handler(state=StorageQiwi.here_input_qiwi_amount)
async def create_qiwi_pay(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        pay_amount = int(message.text)
        del_msg = await bot.send_message(message.from_user.id, "<b>♻ Подождите, платёж генерируется...</b>")
        min_input_qiwi = 1  # Минимальная сумма пополнения в  USDлях

        get_payments = get_paymentx()
        if get_payments[0] != "None" or get_payments[1] != "None" or get_payments[2] != "None":
            try:
                request = requests.Session()
                request.headers["authorization"] = "Bearer " + get_payments[1]
                response_qiwi = request.get(
                    f"https://edge.qiwi.com/payment-history/v2/persons/{get_payments[0]}/payments",
                    params={"rows": 1, "operation": "IN"})
                if pay_amount >= min_input_qiwi:
                    passwd = list("1234567890ABCDEFGHIGKLMNOPQRSTUVYXWZ")
                    random.shuffle(passwd)
                    random_chars = "".join([random.choice(passwd) for x in range(10)])
                    generate_number_check = str(random.randint(100000000000, 999999999999))
                    if get_payments[4] == "form":
                        qiwi = QiwiP2P(get_payments[2])
                        bill = qiwi.bill(bill_id=generate_number_check, amount=pay_amount,
                                         comment=generate_number_check)
                        way_pay = "Form"
                        send_requests = bill.pay_url
                        send_message = f"<b>🆙 Пополнение баланса</b>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"❗ У вас имеется 30 минут на оплату счета.\n" \
                                       f"🥝 Для пополнения баланса, нажмите на кнопку  <code>Перейти к оплате</code>\n" \
                                       f"💵 Сумма пополнения: <code>{pay_amount} USD</code>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"
                    elif get_payments[4] == "number":
                        way_pay = "Number"
                        send_requests = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={get_payments[0]}&amountInteger=" \
                                        f"{pay_amount}&amountFraction=0&extra%5B%27comment%27%5D={generate_number_check}&currency=" \
                                        f"643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"
                        send_message = f"<b>🆙 Пополнение баланса</b>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🥝 Для пополнения баланса, переведите нужную сумму на указанный кошелёк или " \
                                       f"нажмите на кнопку  <code>Перейти к оплате</code>\n" \
                                       f"❗ Обязательно введите комментарий, который указан ниже\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🏷 Комментарий: <code>{generate_number_check}</code>\n" \
                                       f"📞 QIWI кошелёк: <code>{get_payments[0]}</code>\n" \
                                       f"💵 Сумма пополнения: <code>{pay_amount} USD</code>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"
                    elif get_payments[4] == "nickname":
                        way_pay = "Nickname"
                        send_requests = f"https://qiwi.com/payment/form/99999?amountInteger={pay_amount}&amountFraction=0&currency=643" \
                                        f"&extra%5B%27comment%27%5D=405550&extra%5B%27account%27%5D={get_payments[3]}&blocked%5B0%5D=" \
                                        f"comment&blocked%5B1%5D=account&blocked%5B2%5D=sum&0%5Bextra%5B%27accountType%27%5D%5D=nickname"
                        # send_requests = short_link.get(f"https://clck.ru/--?url={send_requests}").text
                        send_message = f"<b>🆙 Пополнение баланса</b>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🥝 Для пополнения баланса, переведите нужную сумму на указанный кошелёк или " \
                                       f"нажмите на кнопку  <code>Перейти к оплате</code> и укажите комментарий\n" \
                                       f"❗ Обязательно введите комментарий, который указан ниже\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🏷 Комментарий: <code>{generate_number_check}</code>\n" \
                                       f"Ⓜ QIWI Никнейм: <code>{get_payments[3]}</code>\n" \
                                       f"💵 Сумма пополнения: <code>{pay_amount} USD</code>\n" \
                                       f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
                                       f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"
                    await bot.delete_message(message.chat.id, del_msg.message_id)
                    delete_msg = await message.answer("🥝 <b>Платёж был создан.</b>",
                                                      reply_markup=check_user_out_func(message.from_user.id))
                    await message.answer(send_message,
                                         reply_markup=create_pay_qiwi_func(send_requests,
                                                                           generate_number_check,
                                                                           delete_msg.message_id,
                                                                           way_pay))
                    await state.finish()
                else:
                    await StorageQiwi.here_input_qiwi_amount.set()
                    await bot.delete_message(message.chat.id, del_msg.message_id)
                    await message.answer(f"❌ <b>Неверная сумма пополнения</b>\n"
                                         f"▶ Мин. сумма пополнения: <code>{min_input_qiwi} USD</code>\n"
                                         f"💵 Введите сумму для пополнения средств 🥝")
            except json.decoder.JSONDecodeError or UnicodeEncodeError:
                await state.finish()
                await bot.delete_message(message.chat.id, del_msg.message_id)
                await message.answer("❕ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                                     "⌛ Попробуйте чуть позже.",
                                     reply_markup=check_user_out_func(message.from_user.id))
                await send_all_admin("<b>🥝 QIWI кошелёк отсутствует</b> ❌\n"
                                     f"❕ <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>"
                                     " пытался пополнить баланс\n"
                                     "❗ Как можно быстрее замените QIWI кошелёк")
        else:
            await state.finish()
            await bot.delete_message(message.chat.id, del_msg.message_id)
            await message.answer("❕ Извиняемся за доставленные неудобства, пополнение временно недоступно.\n"
                                 "⌛ Попробуйте чуть позже.",
                                 reply_markup=check_user_out_func(message.from_user.id))
            await send_all_admin("<b>🥝 QIWI кошелёк отсутствует</b> ❌\n"
                                 f"❕ <a href='tg://user?id={message.from_user.id}'>{clear_firstname(message.from_user.first_name)}</a>"
                                 " пытался пополнить баланс\n"
                                 "❗ Как можно быстрее замените QIWI кошелёк")
    else:
        await StorageQiwi.here_input_qiwi_amount.set()
        await message.answer("<b>❌ Данные были введены неверно.</b>\n"
                             "💵 Введите сумму для пополнения средств 🥝")


# Обработка колбэка "Проверить оплату" QIWI через Форму
@dp.callback_query_handler(text_startswith="Pay:Form:")
async def check_qiwi_pay(call: CallbackQuery):
    receipt = call.data[9:].split(":")[0]
    message_id = call.data[9:].split(":")[1]
    get_payments = get_paymentx()
    get_user_info = get_userx(user_id=call.from_user.id)
    if get_payments[0] != "None" or get_payments[1] != "None" or get_payments[2] != "None":
        qiwi = QiwiP2P(get_payments[2])
        pay_comment = qiwi.check(bill_id=receipt).comment  # Получение комментария платежа
        pay_status = qiwi.check(bill_id=receipt).status  # Получение статуса платежа
        pay_amount = float(qiwi.check(bill_id=receipt).amount)  # Получение суммы платежа в  USDлях
        pay_amount = int(pay_amount)
        if pay_status == "PAID":
            get_purchase = get_refillx("*", receipt=receipt)
            if get_purchase is None:

                add_refillx(call.from_user.id, call.from_user.username, call.from_user.first_name, pay_comment,
                            pay_amount, receipt, "Form", get_dates(),
                            int(time.time()))

                # Обновление баланса у пользователя
                update_userx(call.from_user.id,
                             balance=int(get_user_info[4]) + pay_amount,
                             all_refill=int(get_user_info[5]) + pay_amount)

                await bot.delete_message(call.message.chat.id, message_id)
                await call.message.delete()
                await call.message.answer(f"<b>✅ Вы успешно пополнили баланс на сумму {pay_amount} USD. Удачи ❤</b>\n"
                                          f"<b>📃 Чек:</b> <code>+{receipt}</code>",
                                          reply_markup=check_user_out_func(call.from_user.id))
                await send_all_admin(f"<b>💰 Пользователь</b> "
                                     f"(@{call.from_user.username}|<a href='tg://user?id={call.from_user.id}'>{call.from_user.first_name}</a>"
                                     f"|<code>{call.from_user.id}</code>) "
                                     f"<b>пополнил баланс на сумму</b> <code>{pay_amount} USD</code> 🥝\n"
                                     f"📃 <b>Чек:</b> <code>+{receipt}</code>")
            else:
                await bot.answer_callback_query(call.id, "❗ Ваше пополнение уже зачислено.", True)
        elif pay_status == "EXPIRED":
            await bot.edit_message_text("<b>❌ Время оплаты вышло. Платёж был удалён.</b>",
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=check_user_out_func(call.from_user.id))
        elif pay_status == "WAITING":
            await bot.answer_callback_query(call.id, "❗ Оплата не была произведена.", True)
        elif pay_status == "REJECTED":
            await bot.edit_message_text("<b>❌ Счёт был отклонён.</b>",
                                        call.message.chat.id,
                                        call.message.message_id,
                                        reply_markup=check_user_out_func(call.from_user.id))
    else:
        await send_all_admin("<b>❗ Кто-то пытался проверить платёж, но QIWI не работает\n"
                             "❗ Срочно замените QIWI данные</b>")
        await bot.answer_callback_query(call.id, "❗ Извиняемся за доставленные неудобства,\n"
                                                 "проверка платежа временно недоступна.\n"
                                                 "⏳ Попробуйте чуть позже.")


# Обработка колбэка "Проверить оплату" QIWI через Номер и Никнейм
@dp.callback_query_handler(text_startswith=["Pay:Number", "Pay:Nickname"])
async def check_qiwi_pay(call: CallbackQuery):
    way_pay = call.data[4:].split(":")[0]
    receipt = call.data[4:].split(":")[1]
    message_id = call.data[4:].split(":")[2]
    get_payments = get_paymentx()
    get_user_info = get_userx(user_id=call.from_user.id)
    pay_status = False
    if get_payments[0] != "None" or get_payments[1] != "None" or get_payments[2] != "None":
        try:
            request = requests.Session()
            request.headers["authorization"] = "Bearer " + get_payments[1]
            get_history = request.get(
                f"https://edge.qiwi.com/payment-history/v2/persons/{get_payments[0]}/payments",
                params={"rows": 20, "operation": "IN"}).json()["data"]
            for check_pay in get_history:
                if str(receipt) == str(check_pay["comment"]):
                    if "643" == str(check_pay["sum"]["currency"]):
                        pay_status = True  # Получение статуса платежа
                        pay_amount = float(check_pay["sum"]["amount"])  # Получение суммы платежа в  USDлях
                        pay_amount = int(pay_amount)
                    else:
                        await bot.answer_callback_query(call.id, "❗ Оплата была произведена не в  USDлях.", True)
            if pay_status:
                get_purchase = get_refillx("*", receipt=receipt)
                if get_purchase is None:
                    add_refillx(call.from_user.id, call.from_user.username, call.from_user.first_name, receipt,
                                pay_amount, receipt, way_pay, get_dates(), int(time.time()))

                    # Обновление баланса у пользователя
                    update_userx(call.from_user.id,
                                 balance=int(get_user_info[4]) + pay_amount,
                                 all_refill=int(get_user_info[5]) + pay_amount)

                    await bot.delete_message(call.message.chat.id, message_id)
                    await call.message.delete()
                    await call.message.answer(
                        f"<b>✅ Вы успешно пополнили баланс на сумму {pay_amount} USD. Удачи ❤</b>\n"
                        f"<b>📃 Чек:</b> <code>+{receipt}</code>",
                        reply_markup=check_user_out_func(call.from_user.id))
                    await send_all_admin(f"<b>💰 Пользователь</b> "
                                         f"(@{call.from_user.username}|<a href='tg://user?id={call.from_user.id}'>{call.from_user.first_name}</a>"
                                         f"|<code>{call.from_user.id}</code>) "
                                         f"<b>пополнил баланс на сумму</b> <code>{pay_amount} USD</code> 🥝\n"
                                         f"📃 <b>Чек:</b> <code>+{receipt}</code>")
                else:
                    await bot.answer_callback_query(call.id, "❗ Ваше пополнение уже зачислено.", True)
            else:
                await bot.answer_callback_query(call.id, "❗ Платёж не был найден.\n⌛ Попробуйте чуть позже.", True)
        except json.decoder.JSONDecodeError:
            await bot.answer_callback_query(call.id,
                                            "❕ Извиняемся за доставленные неудобства, проверка временно недоступна.\n"
                                            "⌛ Попробуйте чуть позже.", True)
            await send_all_admin("<b>🥝 QIWI кошелёк отсутствует</b> ❌\n"
                                 f"❕ <a href='tg://user?id={call.from_user.id}'>{call.from_user.first_name}</a>"
                                 " пытался проверить платёж\n"
                                 "❗ Как можно быстрее замените QIWI кошелёк")
    else:
        await send_all_admin("<b>❗ Кто-то пытался проверить платёж, но QIWI не работает\n"
                             "❗ Срочно замените QIWI данные</b>")
        await bot.answer_callback_query(call.id, "❗ Извиняемся за доставленные неудобства,\n"
                                                 "проверка платежа временно недоступна.\n"
                                                 "⏳ Попробуйте чуть позже.")
