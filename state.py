from aiogram.fsm.state import State, StatesGroup

class OrderFrom(StatesGroup):
    title = State()
    description = State()
    price = State()
    product_code = State()
    photo = State()

class UpProductFrom(StatesGroup):
    title = State()
    description = State()
    price = State()
    product_code = State()
    photo = State()

class SearchFrom(StatesGroup):
    product_code = State()