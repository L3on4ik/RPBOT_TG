import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import init_db, save_profile, get_profile

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

init_db()

# -------- FSM --------
class ProfileStates(StatesGroup):
    name = State()
    description = State()
    fursona = State()
    photo = State()


# -------- Команды --------
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.answer(
        "👋 Привет!\n\n"
        "/create — создать анкету\n"
        "/profile — посмотреть анкету"
    )


# -------- Создание анкеты --------
@dp.message_handler(commands=['create'])
async def create(msg: types.Message):
    await msg.answer("Введите имя персонажа:")
    await ProfileStates.name.set()


@dp.message_handler(state=ProfileStates.name)
async def set_name(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Введите описание:")
    await ProfileStates.next()


@dp.message_handler(state=ProfileStates.description)
async def set_description(msg: types.Message, state: FSMContext):
    await state.update_data(description=msg.text)
    await msg.answer("Введите фурсону:")
    await ProfileStates.next()


@dp.message_handler(state=ProfileStates.fursona)
async def set_fursona(msg: types.Message, state: FSMContext):
    await state.update_data(fursona=msg.text)
    await msg.answer("Отправьте фото персонажа:")
    await ProfileStates.next()


@dp.message_handler(content_types=['photo'], state=ProfileStates.photo)
async def set_photo(msg: types.Message, state: FSMContext):
    photo_id = msg.photo[-1].file_id

    data = await state.get_data()

    save_profile(
        msg.from_user.id,
        data['name'],
        data['description'],
        data['fursona'],
        photo_id
    )

    await msg.answer("✅ Анкета сохранена!")
    await state.finish()


# -------- Просмотр анкеты --------
@dp.message_handler(commands=['profile'])
async def profile(msg: types.Message):
    data = get_profile(msg.from_user.id)

    if not data:
        await msg.answer("❌ У тебя нет анкеты. Напиши /create")
        return

    user_id, name, description, fursona, photo = data

    text = (
        f"🧾 {name}\n\n"
        f"{description}\n\n"
        f"🐾 Фурсона: {fursona}"
    )

    await bot.send_photo(
        chat_id=msg.chat.id,
        photo=photo,
        caption=text
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)