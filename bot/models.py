from database import Base, engine
from sqlalchemy import Column, Integer, String, func, BigInteger


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=False, nullable=False)
    chat_id = Column(Integer, unique=True, nullable=False)
    role = Column(String, nullable=False, default="user")
    created_at = Column(BigInteger, default=func.extract('epoch', func.now()))


class Hotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False, nullable=False)
    address = Column(String, unique=False, nullable=False)
    description = Column(String, unique=False, nullable=False)
    rating = Column(String, unique=False, nullable=False)
    sizes = Column(String, unique=False, nullable=False)
    price = Column(String, unique=False, nullable=False)


class UserLogs(Base):
    __tablename__ = "user_logs"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, unique=False, nullable=False)
    action = Column(String, unique=False, nullable=False)
    created_at = Column(BigInteger, default=func.extract('epoch', func.now()))


