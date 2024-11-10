
import requests
from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from states import RegistrationStates, LoginStates, TourStates, AddCardStates, ResetPasswordStates

API_URL = "http://127.0.0.1:8000/"

router = Router()

logging.basicConfig(level=logging.INFO)


async def is_authenticated(state: FSMContext):
    user_data = await state.get_data()
    return "access_token" in user_data


def handle_api_error(response):
    if response.status_code != 200:
        logging.error(f"API Error {response.status_code}: {response.text}")
        return False
    return True


def start_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✍️ Регистрация", callback_data="register")],
        [InlineKeyboardButton(text="🔑 Логин", callback_data="login")],
        [InlineKeyboardButton(text="Забыли пароль?", callback_data="forgot_password")]
    ])


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Добро пожаловать в наш туристический бот! Пожалуйста, выберите опцию ниже: \n\n"
        "1️⃣ Регистрация \n"
        "2️⃣ Логин",
        reply_markup=start_menu_keyboard()
    )


@router.callback_query(lambda c: c.data == "register")
async def registration_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Напишите свой ник для регистрации:")
    await state.set_state(RegistrationStates.waiting_for_username)
    await callback.answer()


@router.message(StateFilter(RegistrationStates.waiting_for_username))
async def process_username(message: types.Message, state: FSMContext):
    username = message.text
    await state.update_data(username=username)
    await message.answer("Теперь введи свой email.")
    await state.set_state(RegistrationStates.waiting_for_email)


@router.message(StateFilter(RegistrationStates.waiting_for_email))
async def process_email(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Теперь введи свой пароль.")
    await state.set_state(RegistrationStates.waiting_for_password)


@router.message(StateFilter(RegistrationStates.waiting_for_password))
async def process_password(message: types.Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    username = user_data["username"]
    email = user_data["email"]

    response = requests.post(f'{API_URL}avtorizate/users/register/', json={
        "username": username,
        "email": email,
        "password": password
    })

    if response.status_code == 201:
        await message.answer("✅ Регистрация прошла успешно! Проверочный код отправлен на ваш email.")
        await state.set_state(RegistrationStates.awaiting_code)
    else:
        error_message = "❌ Ошибка регистрации. Попробуйте еще раз."
        if response.status_code == 400:
            error_message = "⚠️ Неверные данные для регистрации. Проверьте введенные данные."
        await message.answer(error_message)
        await state.set_state(RegistrationStates.waiting_for_username)


"-----------------------------------------------------------------------------------------------------------------"



@router.callback_query(lambda c: c.data == "forgot_password")
async def forgot_password_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите свой email для сброса пароля:")
    await state.set_state(ResetPasswordStates.waiting_for_email)
    await callback.answer()

@router.message(StateFilter(ResetPasswordStates.waiting_for_email))
async def process_forgot_password_email(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)

    response = requests.post(f'{API_URL}avtorizate/reset-password-request/', json={"email": email})
    if response.status_code == 200:
        await message.answer("Код для сброса пароля отправлен на вашу почту. Введите код:")
        await state.set_state(ResetPasswordStates.waiting_for_code)
    else:
        await message.answer("❌ Ошибка: Пользователь с таким email не найден.")
        await state.clear()
@router.message(StateFilter(ResetPasswordStates.waiting_for_code))
async def process_forgot_password_code(message: types.Message, state: FSMContext):
    code = message.text
    await state.update_data(code=code)

    await message.answer("Введите новый пароль:")
    await state.set_state(ResetPasswordStates.waiting_for_new_password)
@router.message(StateFilter(ResetPasswordStates.waiting_for_new_password))
async def process_new_password(message: types.Message, state: FSMContext):
    new_password = message.text
    user_data = await state.get_data()

    response = requests.post(f'{API_URL}avtorizate/reset-password-confirm/', json={
        "email": user_data["email"],
        "code": user_data["code"],
        "new_password": new_password
    })

    if response.status_code == 200:
        await message.answer("✅ Пароль успешно обновлен! Теперь вы можете войти в систему.")
        await state.clear()
    else:
        await message.answer("❌ Ошибка: Неверный или просроченный код. Попробуйте еще раз.")
        await state.clear()

"------------------------------------------------------------------------------------------------------------"


@router.callback_query(lambda c: c.data == "login")
async def login_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("🔑 Напишите свой ник для логина:")
    await state.set_state(LoginStates.waiting_for_username)
    await callback.answer()


@router.message(StateFilter(LoginStates.waiting_for_username))
async def process_login_username(message: types.Message, state: FSMContext):
    username = message.text
    await state.update_data(username=username)
    await message.answer("🔑 Теперь введи свой пароль.")
    await state.set_state(LoginStates.waiting_for_password)


@router.message(StateFilter(LoginStates.waiting_for_password))
async def process_login_password(message: types.Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    username = user_data["username"]

    response = requests.post(f'{API_URL}avtorizate/users/login/', json={
        "username": username,
        "password": password
    })

    if handle_api_error(response):
        tokens = response.json()
        await state.update_data(access_token=tokens["access"], refresh_token=tokens["refresh"])
        await message.answer_sticker(sticker='CAACAgIAAxkBAAErxtBnLNOLeYgPGPam9T1EOoOvrJctBAAC4mAAAiQnaEmHEUXkVbbpGjYE')

        await message.answer(
            "✅ Логин успешен! Выберите один из вариантов ниже:",
            reply_markup=await user_main_menu(state)
        )
    else:
        await message.answer("❌ Ошибка логина. Попробуйте снова.")


@router.message(Command("menu"))
async def show_main_menu(message: types.Message, state: FSMContext):
    keyboard = await user_main_menu(state)
    await message.answer("Выберите действие из меню ниже:", reply_markup=keyboard)


async def get_user_card_data(user_data):
    tokens = user_data.get("access_token")
    if not tokens:
        return None

    headers = {
        "Authorization": f"Bearer {tokens}"
    }
    response = requests.get(f"{API_URL}cards/cards", headers=headers)

    if response.status_code == 200:
        return response.json()
    return None


async def user_main_menu(state: FSMContext):
    user_data = await state.get_data()
    user_card = await get_user_card_data(user_data)

    if user_card:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌍 Туры", callback_data="tours")],
            [InlineKeyboardButton(text="📝 Мои заказы", callback_data="my_bookings")],
            [InlineKeyboardButton(text="📜 История", callback_data="history")],
            [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")],
            [InlineKeyboardButton(text="💳 Посмотреть мою карту", callback_data="view_card")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌍 Туры", callback_data="tours")],
            [InlineKeyboardButton(text="📝 Мои заказы", callback_data="my_bookings")],
            [InlineKeyboardButton(text="📜 История", callback_data="history")],
            [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")],
            [InlineKeyboardButton(text="💳 Добавить карту", callback_data="add_card")]
        ])


@router.callback_query(lambda c: c.data == "add_card")
async def add_card_start(callback: types.CallbackQuery, state: FSMContext):
    if await is_authenticated(state):
        await callback.message.answer("Введите номер вашей карты:")
        await state.set_state(AddCardStates.waiting_for_card_number)
        await callback.answer()
    else:
        await callback.message.answer("❌ Вы не авторизованы. Пожалуйста, выполните логин.")


@router.message(StateFilter(AddCardStates.waiting_for_card_number))
async def process_card_number(message: types.Message, state: FSMContext):
    card_number = message.text
    await state.update_data(card_number=card_number)
    await message.answer("Введите дату окончания карты (в формате MM/YY):")
    await state.set_state(AddCardStates.waiting_for_card_expiry)


@router.message(StateFilter(AddCardStates.waiting_for_card_expiry))
async def process_card_expiry(message: types.Message, state: FSMContext):
    card_expiry = message.text
    await state.update_data(card_expiry=card_expiry)
    await message.answer("Введите имя владельца карты:")
    await state.set_state(AddCardStates.waiting_for_card_holder)


@router.message(StateFilter(AddCardStates.waiting_for_card_holder))
async def process_card_holder(message: types.Message, state: FSMContext):
    card_holder = message.text
    user_data = await state.get_data()

    data = {
        "card_num": user_data["card_number"],
        "mm_yy": user_data["card_expiry"],
        "card_holder": card_holder
    }

    tokens = user_data.get("access_token")
    if not tokens:
        await message.answer("❌ Вы не авторизованы. Пожалуйста, выполните логин.")
        return

    headers = {
        "Authorization": f"Bearer {tokens}"
    }

    response = requests.post(f"{API_URL}cards/cards/", json=data, headers=headers)

    if response.status_code == 201:
        card_info = response.json()
        await message.answer(f"✅ Ваша карта успешно добавлена!\n"
                             f"Номер карты: {card_info['card_num']}\n"
                             f"Срок действия: {card_info['mm_yy']}\n"
                             f"Баланс: {card_info['balance']}")

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        view_card_button = types.InlineKeyboardButton("Посмотреть мою карту", callback_data="view_card")
        keyboard.add(view_card_button)

        await message.answer("Меню обновлено. Вы можете теперь просматривать свою карту.", reply_markup=keyboard)

    else:
        await message.answer("❌ Ошибка при добавлении карты. Пожалуйста, попробуйте снова.")


@router.callback_query(lambda c: c.data == "view_card")
async def view_card(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    tokens = user_data.get("access_token")

    if not tokens:
        await callback.message.answer("❌ Вы не авторизованы. Пожалуйста, выполните логин.")
        await callback.answer()
        return

    headers = {
        "Authorization": f"Bearer {tokens}"
    }

    response = requests.get(f"{API_URL}cards/cards/", headers=headers)

    if response.status_code == 200:
        user_card = response.json()

        if isinstance(user_card, list) and len(user_card) > 0:
            user_card = user_card[0]

        if user_card:
            card_num = user_card.get("card_num", "Неизвестно")
            mm_yy = user_card.get("mm_yy", "Неизвестно")
            balance = user_card.get("balance", "Неизвестно")

            await callback.message.answer(
                f"💳 Ваши данные карты:\n"
                f"Номер карты: {card_num}\n"
                f"Срок действия: {mm_yy}\n"
                f"Баланс: {balance} $"

            )
        else:
            await callback.message.answer("❌ У вас нет добавленной карты. Пожалуйста, добавьте карту.")
    else:
        await callback.message.answer("❌ Ошибка при получении данных карты. Пожалуйста, попробуйте снова.")

    await callback.answer()


@router.callback_query(lambda c: c.data == "tours")
async def get_tours(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if "access_token" not in user_data:
        await callback.message.answer("❌ Вы не авторизованы. Пожалуйста, войдите в систему.")
        await state.set_state(LoginStates.waiting_for_username)
        return
    response = requests.get(f"{API_URL}tours/tours/", headers={"Authorization": f"Bearer {user_data['access_token']}"})

    if handle_api_error(response):
        tours = response.json()
        buttons = [
            InlineKeyboardButton(text=f"{tour['name']} - {tour['hotel']}", callback_data=f"tour_{tour['id']}")
            for tour in tours
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
        await callback.message.answer("📚 Выберите тур:", reply_markup=keyboard)
    else:
        await callback.message.answer("❌ Ошибка при получении списка туров.")


@router.callback_query(lambda c: c.data.startswith("tour_"))
async def show_tour_info(callback: types.CallbackQuery, state: FSMContext):
    tour_id = int(callback.data.split("_")[1])
    response = requests.get(f"{API_URL}tours/tours/{tour_id}/")

    if handle_api_error(response):

        tour = response.json()
        details = f"🗺️ Тур: {tour['name']}\n🏨 Отель: {tour['hotel']}"
        booking_button = InlineKeyboardButton(text="📅 Забронировать", callback_data=f"book_{tour_id}")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[booking_button]])
        photo_url = tour.get('photo_url')
        if photo_url:
            await callback.message.answer_photo(photo_url)
        else:
            await callback.message.answer('Тут должна была быть фотка')
        await callback.message.answer(details, reply_markup=keyboard)
    else:
        await callback.message.answer("❌ Ошибка при получении информации о туре.")




@router.callback_query(lambda c: c.data.startswith("book_"))
async def handle_booking(callback: types.CallbackQuery, state: FSMContext):
    tour_id = int(callback.data.split("_")[1])
    await state.update_data(selected_tour=tour_id)
    await callback.message.answer("👶 Введите количество детей:")
    await state.set_state(TourStates.waiting_for_child_count)
    await callback.answer()



@router.message(TourStates.waiting_for_child_count)
async def enter_child_count(message: types.Message, state: FSMContext):
    if message.text.isdigit() or message.text == "":
        await state.update_data(child_count=message.text)
        await message.answer("👨‍👩‍👧 Введите количество взрослых:")
        await state.set_state(TourStates.waiting_for_adult_count)
    else:
        await message.answer("⚠️ Пожалуйста, введите число:")


@router.message(TourStates.waiting_for_adult_count)
async def enter_adult_count(message: types.Message, state: FSMContext):
    if message.text.isdigit() or message.text == "":
        await state.update_data(adult_count=message.text)
        await message.answer("👴 Введите количество пожилых людей:")
        await state.set_state(TourStates.waiting_for_senior_count)
    else:
        await message.answer("⚠️ Пожалуйста, введите число")


@router.message(TourStates.waiting_for_senior_count)
async def enter_senior_count(message: types.Message, state: FSMContext):
    if message.text.isdigit() or message.text == "":
        await state.update_data(senior_count=message.text)
        user_data = await state.get_data()
        booking_people = []

        if int(user_data["child_count"]) > 0:
            booking_people.append({"person": "child", "count": int(user_data["child_count"])})
        if int(user_data["adult_count"]) > 0:
            booking_people.append({"person": "adult", "count": int(user_data["adult_count"])})
        if int(user_data["senior_count"]) > 0:
            booking_people.append({"person": "senior", "count": int(user_data["senior_count"])})

        data = {
            "tour": user_data["selected_tour"],
            "booking_people": booking_people
        }

        tokens = user_data.get("access_token")
        if not tokens:
            await message.answer("❌ Вы не авторизованы. Пожалуйста, выполните логин.")
            return

        headers = {
            "Authorization": f"Bearer {tokens}"
        }

        response = requests.post(f"{API_URL}tours/booking/", json=data, headers=headers)

        logging.info(f"Booking response: {response.status_code} - {response.text}")

        if response.status_code == 201:
            booking_info = response.json()
            booking_details = (
                f"✅ Бронирование успешно оформлено!\n\n"
                f"ID бронирования: {booking_info['id']}\n"
                f"Пользователь: {booking_info['user']}\n"
                f"Тур: {booking_info['tour']}\n"
                f"Общая стоимость: {booking_info['total_price']}\n\n"
                f"Детали бронирования:\n"
            )
            for person in booking_info['booking_people']:
                booking_details += f"{person['person'].capitalize()}: {person['count']}\n"

            await message.answer(booking_details)
        else:
            error_message = "❌ Произошла ошибка при оформлении бронирования. Пожалуйста, попробуйте снова."
            if response.status_code == 400:
                error_message = "⚠️ Неверные данные для бронирования. Проверьте введенные данные."
            elif response.status_code == 401:
                error_message = "❌ Неавторизованный доступ. Пожалуйста, выполните логин."
            logging.error(f"Booking error: {response.status_code} - {response.text}")
            await message.answer(error_message)
    else:
        await message.answer("⚠️ Пожалуйста, введите число или оставьте поле пустым.")


@router.callback_query(lambda c: c.data.startswith("book_"))
async def handle_booking(callback: types.CallbackQuery, state: FSMContext):
    tour_id = int(callback.data.split("_")[1])
    await state.update_data(selected_tour=tour_id)
    await callback.message.answer("👶 Введите количество детей:")
    await state.set_state(TourStates.waiting_for_child_count)
    await callback.answer()


@router.callback_query(lambda c: c.data == "my_bookings")
async def my_bookings(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    access_token = user_data.get("access_token")

    if not access_token:
        await callback.message.answer("❌ Вы не авторизованы. Пожалуйста, выполните логин.")
        return

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{API_URL}tours/tours/booking/list", headers=headers)

    if response.status_code == 200:
        bookings = response.json()
        if bookings:
            for booking in bookings:
                booking_id = booking['id']
                tour_name = booking['tour']
                total_price = booking['total_price']
                booking_people = booking["booking_people"]
                is_paid = booking.get('is_paid', False)

                people_details = "\n".join(
                    [f"{person['person'].capitalize()}: {person['count']}" for person in booking_people]
                )

                booking_details = (
                    f"🗓️ Заказ ID: {booking_id}\n"
                    f"🏖️ Тур: {tour_name}\n"
                    f"👥 Кол-во людей:\n{people_details}\n"
                    f"💰 Общая стоимость: {total_price} $\n"
                    f"✅ Оплачено: {'Да' if is_paid else 'Нет'}\n"
                )
                if not is_paid:
                    pay_button = InlineKeyboardButton(text="💳 Оплатить", callback_data=f"pay_{booking_id}")
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[[pay_button]])
                    await callback.message.answer(booking_details, reply_markup=keyboard)
                else:
                    await callback.message.answer(booking_details)
        else:
            await callback.message.answer("❌ У вас нет активных бронирований.")
    else:
        await callback.message.answer("❌ Ошибка при получении списка бронирований. Попробуйте позже.")

    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("pay_"))
async def handle_payment(callback: types.CallbackQuery, state: FSMContext):
    booking_id = int(callback.data.split("_")[1])
    user_data = await state.get_data()
    tokens = user_data.get("access_token")

    if not tokens:
        await callback.message.answer("❌ Вы не авторизованы. Пожалуйста, выполните логин.")
        return

    headers = {
        "Authorization": f"Bearer {tokens}"
    }

    response = requests.get(f"{API_URL}tours/tours/booking/{booking_id}/", headers=headers)
    if response.status_code != 200:
        await callback.message.answer("❌ Ошибка при получении информации о бронировании.")
        return

    booking_info = response.json()

    if booking_info.get("is_paid"):
        await callback.message.answer("❌ Этот заказ уже оплачен. Повторная оплата невозможна.")
        await callback.answer()
        return

    response = requests.get(f"{API_URL}cards/cards/", headers=headers)
    if response.status_code != 200:
        await callback.message.answer("❌ Ошибка при получении информации о картах. Пожалуйста, попробуйте позже.")
        return

    cards = response.json()
    if not cards:
        await callback.message.answer("❌ У вас нет привязанных карт. Пожалуйста, добавьте карту для оплаты.")
        return

    card_id = cards[0]['id']
    payment_data = {
        "booking_id": booking_id,
        "card_id": card_id
    }

    response = requests.post(f"{API_URL}avtorizate/pay/", json=payment_data, headers=headers)

    if response.status_code == 200:
        await callback.message.answer(f"✅ Заказ ID: {booking_id} успешно оплачен!")
        await my_bookings(callback, state)
    elif response.status_code == 400:
        error_message = response.json().get("error", "Ошибка при оплате")
        if "оплата уже была произведена" in error_message.lower():
            error_message = "❌ Оплата уже была произведена для этого заказа."
        await callback.message.answer(error_message)
    elif response.status_code == 401:
        await callback.message.answer("❌ Неавторизованный доступ. Пожалуйста, выполните логин.")
    elif response.status_code == 404:
        await callback.message.answer("❌ Бронирование не найдено. Проверьте ID.")
    else:
        await callback.message.answer("❌ Ошибка при оплате заказа. Попробуйте снова.")

    await callback.answer()






async def get_user_profile(access_token: str):
    try:
        url = f"{API_URL}avtorizate/users/me/"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Ошибка получения профиля: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Ошибка при запросе к API: {e}")
        return None

@router.callback_query(lambda c: c.data == "my_profile")
async def my_profile(callback: types.CallbackQuery, state: FSMContext):
    if await is_authenticated(state):
        user_data = await state.get_data()
        access_token = user_data.get("access_token")
        response = requests.get(f"{API_URL}avtorizate/users/me/", headers={"Authorization": f"Bearer {access_token}"})

        if response.status_code == 200:
            user_info = response.json()
            profile_info = (
                f"👤 Имя пользователя: {user_info.get('username')}\n"
                f"📧 Email: {user_info.get('email')}\n"
            )
            await callback.message.answer(profile_info)
        else:
            await callback.message.answer("❌ Не удалось получить информацию о профиле.")
    else:
        await callback.message.answer("❌ Вы не авторизованы. Пожалуйста, выполните логин.")

    await callback.answer()








@router.callback_query(lambda c: c.data == "history")
async def view_transaction_history(callback: types.CallbackQuery, state: FSMContext):
    if await is_authenticated(state):
        user_data = await state.get_data()
        access_token = user_data.get("access_token")

        if not access_token:
            await callback.message.answer("❌ Ошибка: не найден токен авторизации. Пожалуйста, войдите в систему.")
            return

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{API_URL}cards/transactions/", headers=headers)

        if response.status_code == 200:
            transactions = response.json()
            if transactions:
                history_details = "📜 История последних транзакций:\n"
                for transaction in transactions:
                    transaction_date = transaction.get("datetime", "?").split("T")[0]
                    transaction_amount = transaction.get("value", "?")
                    history_details += (
                        f"💳 Номер карты: {transaction.get('from_card', '?')}\n"
                        f"🗓 Дата: {transaction_date}\n"
                        f"💰 Сумма: {transaction_amount}₽\n"
                        f"------------------------\n"
                    )
                await callback.message.answer(history_details)
            else:
                await callback.message.answer("❌ У вас нет транзакций.")
        else:
            await callback.message.answer("❌ Ошибка при получении истории транзакций. Пожалуйста, попробуйте снова.")
    else:
        await callback.message.answer("❌ Вы не авторизованы. Пожалуйста, выполните логин.")
