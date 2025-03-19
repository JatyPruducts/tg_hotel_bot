from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import *
from database import get_session


async def add_hotel_to_db(name: str, address: str, description: str, rating: str, sizes: str,
                          price: str):
    async for db in get_session():
        new_hotel = Hotel(
            name=name,
            address=address,
            description=description,
            rating=rating,
            sizes=sizes,
            price=price
        )
        db.add(new_hotel)
        await db.commit()  # Сохраняем изменения
        await db.refresh(new_hotel)  # Получаем обновленный объект с id
        return new_hotel


async def add_user_to_db(username: str, tg_chat_id: int):
    async for db in get_session():
        try:
            user = await db.execute(select(User).where(User.tg_chat_id == tg_chat_id))
            user = user.scalars().first()
            if user:
                return user
            new_user = User(
                username=username,
                tg_chat_id=tg_chat_id
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            await db.rollback()  # Если ошибка, откатываем транзакцию
            print(f"Ошибка при добавлении пользователя: {e}")
            return None


async def check_role(tg_chat_id: int):
    async for db in get_session():
        user = await db.execute(select(User).where(User.tg_chat_id == tg_chat_id))
        user = user.scalars().first()
        if user.role == "user":
            return False
        return True


async def change_user_role(db: AsyncSession, tg_chat_id: int):
    async for db in get_session():
        user = await db.execute(select(User).where(User.tg_chat_id == tg_chat_id))
        user = user.scalars().first()
        if user:
            if user.role == "user":
                user.role = "admin"
                return "admin"
            elif user.role == "admin":
                user.role = "user"
                return "user"
            else:
                return "RoleError"
            await db.commit()
            await db.refresh(user)
        else:
            return "UserError"