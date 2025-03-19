import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from utils import *  # Предполагается, что эта функция асинхронная и возвращает объект отеля

load_dotenv()
API_TOKEN = os.getenv("TOKEN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
logging.basicConfig(level=logging.INFO)

# Создаем объект бота и диспетчера с использованием памяти для хранения состояний
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Определяем группу состояний для смены роли
class RoleStates(StatesGroup):
    waiting_for_password = State()


@dp.message(Command("start"))
async def start(message: types.Message):
    # Проверяем, есть ли пользователь в базе, если нет — добавляем
    if not await check_user(message.chat.id):
        await add_user_to_db(message.from_user.username, message.chat.id)

    # Логируем запуск бота (если функция возвращает ошибку — выводим Error)
    if await add_user_log(message.chat.id, "start_bot"):
        await message.answer("Error")

    # Получаем роль пользователя. Предполагается, что функция get_user_role возвращает "admin" или "user"
    user_role = await get_user_role(message.chat.id)

    # Формируем клавиатуру в зависимости от роли пользователя
    if user_role == "admin":
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Фильтры"), types.KeyboardButton(text="Просмотр отелей")],
                [types.KeyboardButton(text="Поиск по названию")],
                [types.KeyboardButton(text="Добавить отель")]
            ],
            resize_keyboard=True
        )
    else:
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Фильтры"), types.KeyboardButton(text="Просмотр отелей")],
                [types.KeyboardButton(text="Поиск по названию")],
            ],
            resize_keyboard=True
        )

    # Отправляем приветственное сообщение с клавиатурой
    await message.answer("Добро пожаловать!", reply_markup=keyboard)


# --- Обработчик для добавления отеля через FSM --- #

# Определяем состояния для добавления отеля
class AddHotelStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_address = State()
    waiting_for_description = State()
    waiting_for_rating = State()
    waiting_for_sizes = State()
    waiting_for_price = State()


@dp.message(lambda message: message.text == "Добавить отель")
async def start_add_hotel(message: types.Message, state: FSMContext):
    # Дополнительно можно проверить, что роль пользователя "admin"
    user_role = await get_user_role(message.chat.id)
    if user_role != "admin":
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Фильтры"), types.KeyboardButton(text="Просмотр отелей")],
                [types.KeyboardButton(text="Поиск по названию")],
            ],
            resize_keyboard=True
        )
        await message.answer("У вас недостаточно прав для этой операции.", reply_markup=keyboard)
        return
    await add_user_log(message.chat.id, "start_create_hotel")
    await message.answer("Введите название отеля:")
    await state.set_state(AddHotelStates.waiting_for_name)


@dp.message(AddHotelStates.waiting_for_name)
async def process_hotel_name(message: types.Message, state: FSMContext):
    await state.update_data(hotel_name=message.text)
    await message.answer("Введите адрес отеля:")
    await state.set_state(AddHotelStates.waiting_for_address)


@dp.message(AddHotelStates.waiting_for_address)
async def process_hotel_address(message: types.Message, state: FSMContext):
    await state.update_data(hotel_address=message.text)
    await message.answer("Введите описание отеля:")
    await state.set_state(AddHotelStates.waiting_for_description)


@dp.message(AddHotelStates.waiting_for_description)
async def process_hotel_description(message: types.Message, state: FSMContext):
    await state.update_data(hotel_description=message.text)
    await message.answer("Введите рейтинг отеля (например, 5 stars):")
    await state.set_state(AddHotelStates.waiting_for_rating)


@dp.message(AddHotelStates.waiting_for_rating)
async def process_hotel_rating(message: types.Message, state: FSMContext):
    await state.update_data(hotel_rating=message.text)
    await message.answer("Введите размеры отеля (например, Small, Medium, Large):")
    await state.set_state(AddHotelStates.waiting_for_sizes)


@dp.message(AddHotelStates.waiting_for_sizes)
async def process_hotel_sizes(message: types.Message, state: FSMContext):
    await state.update_data(hotel_sizes=message.text)
    await message.answer("Введите цену отеля:")
    await state.set_state(AddHotelStates.waiting_for_price)


@dp.message(AddHotelStates.waiting_for_price)
async def process_hotel_price(message: types.Message, state: FSMContext):
    await state.update_data(hotel_price=message.text)
    data = await state.get_data()
    # Вызываем функцию для добавления отеля в базу данных
    hotel = await add_hotel_to_db(
        data.get("hotel_name"),
        data.get("hotel_address"),
        data.get("hotel_description"),
        data.get("hotel_rating"),
        data.get("hotel_sizes"),
        data.get("hotel_price")
    )
    await message.answer(f"Отель '{data.get('hotel_name')}' успешно добавлен!")
    await add_user_log(message.chat.id, "end_create_hotel")
    await state.clear()


@dp.message(lambda message: message.text in ["Фильтры", "Поиск отелей"])
async def answer_handler(message: types.Message):
    if message.text == "Фильтры":
        await message.answer("Вы выбрали фильтры. Здесь можно настроить параметры поиска.")
    elif message.text == "Поиск отелей":
        await message.answer("Введите критерии для поиска отелей:")


# Обработчик для команды смены роли, который переводит пользователя в состояние ожидания пароля
@dp.message(Command("change_my_role"))
async def change_role(message: types.Message, state: FSMContext):
    await message.answer("Введите пароль администратора:")
    await state.set_state(RoleStates.waiting_for_password)


# Обработчик для ввода пароля, когда пользователь находится в состоянии waiting_for_password
@dp.message(RoleStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        res = await change_user_role(message.chat.id)
        if res == "UserError":
            await message.answer("Пользователь не найден!")
            return
        await message.answer("Вы успешно сменили роль!")
    else:
        await message.answer("Неправильный пароль!")
    # Сбрасываем состояние после обработки
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
