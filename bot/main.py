import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from utils import add_hotel_to_db  # Предполагается, что эта функция асинхронная и возвращает объект отеля

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
    await message.answer("Hello!")


@dp.message(Command("create_hotel"))
async def create_hotel(message: types.Message):
    hotel_name = "Example Hotel"
    hotel_address = "Example Address"
    hotel_description = "Example Description"
    hotel_rating = "5 stars"
    hotel_sizes = "Small, Medium, Large"
    hotel_price = "100"
    # Вызываем функцию для добавления отеля в базу данных
    hotel = await add_hotel_to_db(hotel_name, hotel_address, hotel_description, hotel_rating, hotel_sizes, hotel_price)
    await message.answer(f"Отель '{hotel_name}' успешно добавлен!")


# Обработчик для команды смены роли, который переводит пользователя в состояние ожидания пароля
@dp.message(Command("change_my_role"))
async def change_role(message: types.Message, state: FSMContext):
    await message.answer("Введите пароль администратора:")
    await state.set_state(RoleStates.waiting_for_password)


# Обработчик для ввода пароля, когда пользователь находится в состоянии waiting_for_password
@dp.message(RoleStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await message.answer("Вы стали администратором!")
    else:
        await message.answer("Неправильный пароль!")
    # Сбрасываем состояние после обработки
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
