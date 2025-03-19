from sqlalchemy.future import select
from models import *
from database import get_session


async def add_hotel_to_db(name: str, address: str, description: str, rating: str, sizes: str, price: str) -> bool:
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
        return True


async def add_user_to_db(username: str, chat_id: int) -> bool:
    async for db in get_session():
        user = await db.execute(select(User).where(User.chat_id == chat_id))
        user = user.scalars().first()
        if user:
            return True
        new_user = User(
            username=username,
            chat_id=chat_id
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return True


async def check_user(chat_id: int) -> bool:
    async for db in get_session():
        user = await db.execute(select(User).where(User.chat_id == chat_id))
        user = user.scalars().first()
        if user:
            return True
        return False


async def change_user_role(chat_id: int) -> str | None:
    async for db in get_session():
        user = await db.execute(select(User).where(User.chat_id == chat_id))
        user = user.scalars().first()
        if user:
            if user.role == "user":
                user.role = "admin"
            elif user.role == "admin":
                user.role = "user"
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            return "UserError"


async def add_user_log(chat_id: int, action: str) -> str | None:
    async for db in get_session():
        user = await db.execute(select(User).where(User.chat_id == chat_id))
        user = user.scalars().first()
        if user:
            new_log = UserLogs(
                chat_id=chat_id,
                action=action
            )
            db.add(new_log)
            await db.commit()
            await db.refresh(new_log)
        else:
            return "UserError"


async def get_user_role(chat_id: int) -> str | None:
    async for db in get_session():
        user = await db.execute(select(User).where(User.chat_id == chat_id))
        user = user.scalars().first()
        return user.role
