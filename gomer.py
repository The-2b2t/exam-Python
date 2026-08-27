from aiogram import Dispatcher , Bot , types , F
import asyncio
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from state import UpProductFrom , OrderFrom , SearchFrom
from table_page import (
create_table , add_user , kol_zakaz , 
 add_product , get_users , get_products ,
 update_product , delete_product , check_user_blocked ,
 set_user_block_status , check_product_code , add_cart ,
 get_user_cart , delete_cart_item , clear_cart)
from close import admin_id , admin2 , key

TOKEN = 'key'

bot = Bot(token=TOKEN)

dp = Dispatcher()

admkb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='➕ Добавить продукт'), KeyboardButton(text='👥 Посмотреть пользователей')],
        [KeyboardButton(text='📦 Просмотр заказов'), KeyboardButton(text='🛍 Просмотр продуктов')]
    ],
    resize_keyboard=True
)


uskb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🔎 Поиск товара по коду'),KeyboardButton(text='🛍 Просмотр товаров')],
        [KeyboardButton(text='🧺 Корзина'),KeyboardButton(text='📦 Оформление заказа')]
    ],
    resize_keyboard=True
)

@dp.message(Command('start'))
async def start(message:types.Message):
    user_id = (message.from_user.id)
    if user_id == admin_id:
        add_user(user_id, message.from_user.username, message.from_user.full_name)
        await message.answer('Helo', reply_markup=admkb)
        return

    if check_user_blocked(user_id) == True:
        await message.answer("Вы заблокированы и не можете пользоваться ботом")
        return

    if add_user(user_id, message.from_user.username, message.from_user.full_name):
        await message.answer('Регистрация прошла успешно', reply_markup=uskb)
    else:
        await message.answer('Вы уже зареганы', reply_markup=uskb)


@dp.message(F.text == '➕ Добавить продукт')
async def add_products(message:types.Message , state: FSMContext):
    user_id = (message.from_user.id)
    if user_id != admin_id:
        return
    else:
        await message.answer('Введите название товара')
        await state.set_state(OrderFrom.title)

@dp.message(OrderFrom.title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(OrderFrom.description)
    await message.answer('Введите описание товара')

@dp.message(OrderFrom.description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(OrderFrom.price)
    await message.answer('Введите цену товара')

@dp.message(OrderFrom.price)
async def process_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('введите корректное число')
        return
    await state.update_data(price=message.text)
    await state.set_state(OrderFrom.product_code)
    await message.answer('Введите код товара')

@dp.message(OrderFrom.product_code)
async def process_productcode(message: types.Message, state: FSMContext):
    await state.update_data(product_code=message.text)
    await state.set_state(OrderFrom.photo)
    await message.answer('скиньте фото товара')

@dp.message(OrderFrom.photo)
async def process_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer('отправьте фото товара картинкой(JPG,JPEG)')
        return
    await state.update_data(photo=message.photo[-1].file_id)
    data = await state.get_data()
    add_product(
        title=data['title'],
        description=data['description'],
        price=int(data['price']),
        product_code=data['product_code'],
        photo=data['photo']
    )

    await state.clear()
    await message.answer('Товар успешно добавлен в базу данных')

@dp.message(F.text == '👥 Посмотреть пользователей')
async def all_user(message: types.Message):
    user_id = (message.from_user.id)
    if user_id != admin_id:
        return
    users = get_users(admin_id)
    if not users:
        await message.answer(" не найдены.")
        return
    for tg_id, username, count in users:
        if not username:
            user_name = f"отсутствует" 
        else:
            user_name = f"@{username}" 
        text = (
            f"ID : {tg_id}\n"
            f"Username: {user_name}\n"
            f"Товаров в корзине: {count}\n\n"
        )
        admin_prosmotr = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='🚫 Заблокировать',callback_data=f'user_block {tg_id}')],
                             [InlineKeyboardButton(text='✅ разблокировать',callback_data=f'user_razblock {tg_id}')]])

        await message.answer(text,reply_markup=admin_prosmotr)

@dp.callback_query(F.data.startswith('user_block'))
async def process_user_block(callback: types.CallbackQuery):
    await callback.answer()
    person_id = int(callback.data.split(" ")[1])
    set_user_block_status(person_id, 'true')
    await callback.message.answer(f"🚫 Пользователь {person_id} заблокирован.")

@dp.callback_query(F.data.startswith('user_razblock'))
async def process_user_unblock(callback: types.CallbackQuery):
    await callback.answer()
    person_id = int(callback.data.split(" ")[1])
    set_user_block_status(person_id, 'false')
    await callback.message.answer(f"✅ Пользователь {person_id} разблокирован.")

@dp.message(F.text == '🛍 Просмотр продуктов')
async def prosmotr(message: types.Message):
    user_id = (message.from_user.id)
    if user_id != admin_id:
        return
    users = get_products()
    if not users:
        await message.answer("не найдены.")
        return
    for product_id, title, description, price, product_code, photo in users:
        caption_text = (
            f"название: {title}\n\n"
            f"Описание: {description or 'Отсутствует'}\n\n"
            f"Цена: {price} сомони\n\n"
            f"Код товара: {product_code}"
        )
        admin_upr = InlineKeyboardMarkup(
        inline_keyboard=[
        [InlineKeyboardButton(text='📝 Обновить',callback_data=f'admin_update {product_id}'),
         InlineKeyboardButton(text='❌ Удалить',callback_data=f'admin_delete {product_id}')]
    ]
)
        await message.answer_photo(
            photo=photo, caption=caption_text,reply_markup=admin_upr)

@dp.callback_query(F.data.startswith('admin_update'))
async def up(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    product_id = int(callback.data.split(" ")[1])
    await state.update_data(product_id=product_id)
    await callback.message.answer("Введите новое название товара")
    await state.set_state(UpProductFrom.title)

@dp.message(UpProductFrom.title)
async def process_new_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите новое описание товара")
    await state.set_state(UpProductFrom.description)

@dp.message(UpProductFrom.description)
async def process_new_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите новую цену товара")
    await state.set_state(UpProductFrom.price)

@dp.message(UpProductFrom.price)
async def process_new_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите цену числом (цифрами)")
        return
    await state.update_data(price=message.text)
    await message.answer("Введите новый код (артикуль) товара")
    await state.set_state(UpProductFrom.product_code)

@dp.message(UpProductFrom.product_code)
async def process_new_product_code(message: types.Message, state: FSMContext):
    await state.update_data(product_code=message.text)
    await message.answer("скиньте новое фото товара (или его старое фото)")
    await state.set_state(UpProductFrom.photo)

@dp.message(UpProductFrom.photo)
async def process_new_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer('отправьте фото товара картинкой(JPG,JPEG)')
        return
    await state.update_data(photo=message.photo[-1].file_id)
    data = await state.get_data()
    update_product(
        title = data['title'],
        description = data['description'],
        price = int(data['price']),
        product_code = data['product_code'],
        photo = data['photo'],
        product_id = data['product_id']
    )

    await state.clear()
    await message.answer('Товар успешно обновлен')


@dp.callback_query(F.data.startswith('admin_delete'))
async def delet(callback: types.CallbackQuery):
    await callback.answer()
    del_id = int(callback.data.split(" ")[1])
    delete_product(del_id)
    await callback.message.delete()
    await callback.message.answer("Товар успешно удален")


@dp.message(F.text == '🔎 Поиск товара по коду')
async def start_search_product(message: types.Message, state: FSMContext):
    user_id = (message.from_user.id)
    if check_user_blocked(user_id):
        await message.answer("Вы заблокированы и не можете пользоваться ботом")
        return
    await message.answer("Введите код (артикул) товара")
    await state.set_state(SearchFrom.product_code)

@dp.message(SearchFrom.product_code)
async def process_search_product(message: types.Message, state: FSMContext):
    code = message.text.strip()
    await state.clear()

    product = check_product_code(code)

    if not product:
        await message.answer("Товар с таким кодом не найден")
        return
    
    for product_id, title, description, price, product_code, photo in product:
        c_text = (
            f"название: {title}\n\n"
            f"Описание: {description or 'Отсутствует'}\n\n"
            f"Цена: {price} сомони\n\n"
            f"Код товара: {product_code}"
        )
        user_upr = InlineKeyboardMarkup(
            inline_keyboard=[
            [InlineKeyboardButton(text='🛒 Добавить в корзину',callback_data=f'user_korzina {product_id}')]
        ]
    )
        await message.answer_photo(
                photo=photo, caption=c_text,reply_markup=user_upr)

@dp.callback_query(F.data.startswith('user_korzina '))
async def process_user_block(callback: types.CallbackQuery):
    await callback.answer()
    user_id = (callback.from_user.id)
    product_id = int(callback.data.split(" ")[1])

    if add_cart(user_id, product_id):
        await callback.message.answer("✅ Товар добавлен в корзину!")
    else:
        await callback.message.answer("❌ Не удалось добавить товар.")
    
@dp.message(F.text == '🧺 Корзина')
async def korzinacha(message: types.Message):
    user_id = message.from_user.id
    if check_user_blocked(user_id):
        await message.answer("Вы заблокированы и не можете пользоваться ботом")
        return
    cart_items = get_user_cart(user_id)
    if not cart_items:
        await message.answer("🛒 Ваша корзина пуста.")
        return
    total_sum = 0

    for id_product , title, price, quantity in cart_items:
        obsh_sum = price * quantity
        total_sum += obsh_sum
        c_text = (
            f"название: {title}\n\n"
            f"Количество товара: {quantity}\n"
            f"общ. цена: {obsh_sum} сомони"
        )
        delete_kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="❌ Удалить товар", callback_data=f"del_cart {id_product}")
        ]]
    )

        await message.answer(c_text, reply_markup=delete_kb)

    action_kb = InlineKeyboardMarkup(
            inline_keyboard=[[
            InlineKeyboardButton(text="🧹 Очистить корзину", callback_data="clear_cart"),
            InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout_order")
        ]]
    )

    await message.answer(f"Итог к оплате: {total_sum} сомони", reply_markup=action_kb)




@dp.callback_query(F.data.startswith('del_cart '))
async def process_delete_item(callback: types.CallbackQuery):
    cart_id = int(callback.data.split(" ")[1])
    delete_cart_item(cart_id)

    await callback.answer("Товар удален из корзины")
    await callback.message.delete()

@dp.callback_query(F.data == 'clear_cart')
async def process_clear_cart(callback: types.CallbackQuery):
    clear_cart(callback.from_user.id)
    await callback.answer()
    await callback.message.answer("🧹 Ваша корзина успешно очищена.") 


@dp.message(F.text == '🛍 Просмотр товаров')
async def prosmotr(message: types.Message):
    user_id = (message.from_user.id)
    if check_user_blocked(user_id):
        await message.answer("Вы заблокированы и не можете пользоваться ботом")
        return
    users = get_products()
    if not users:
        await message.answer("не найдены.")
        return
    for product_id, title, description, price, product_code, photo in users:
        c_text = (
            f"название: {title}\n\n"
            f"Описание: {description or 'Отсутствует'}\n\n"
            f"Цена: {price} сомони\n\n"
            f"Код товара: {product_code}"
        )
        user_upr = InlineKeyboardMarkup(
            inline_keyboard=[
            [InlineKeyboardButton(text='🛒 Добавить в корзину',callback_data=f'user_korzina {product_id}')]
        ]
    )
        await message.answer_photo(
                photo=photo, caption=c_text,reply_markup=user_upr)



async def main():
    create_table()
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

    