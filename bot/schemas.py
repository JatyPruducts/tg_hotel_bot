from pydantic import BaseModel


class User(BaseModel):
    username: str
    tg_chat_id: int


class Hotel(BaseModel):
    name: str
    address: str
    description: str
    rating: str
    sizes: str
    price: str
