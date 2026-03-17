import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = '8627185091:AAHFVD3-FMMS6UAknOV9za4D_-WQudK9t1w'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ---------- БАЗА ----------
conn = sqlite3.connect("profiles.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER,
    name TEXT,
    description TEXT,
    photo TEXT
)
""")
conn.commit()


def save_profile(user_id, name, description, photo):
    cursor.execute(
        "INSERT INTO profiles VALUES (?, ?, ?, ?)",
        (user_id, name, description, photo)
    )
    conn.commit()


def get_all_names():
    cursor.execute("SELECT name FROM profiles")
    return cursor.fetchall()


def get_profile_by_name(name):
    cursor.execute("SELECT * FROM profiles WHERE name = ?", (name,))
    return cursor.fetchone()


# ---------- FSM ----------
class CreateProfile(StatesGroup):
    name = State()
    description = State()
    photo = State()


# ---------- КОМАНДЫ ----------
@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.reply(
        "👋 Привет! Я бот для РП-анкет.\n\n"
        "/create — создать анкету\n"
        "/list — список персонажей\n"
        "/who — инфа о персонаже"
    )


# ---------- CREATE ----------
@dp.message_handler(commands=['create'])
async def create(msg: types.Message):
    await msg.reply("Введите имя персонажа:")
    await CreateProfile.name.set()


@dp.message_handler(state=CreateProfile.name, content_types=types.ContentTypes.TEXT)
async def set_name(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.reply("Введите описание:")
    await CreateProfile.next()


@dp.message_handler(state=CreateProfile.description, content_types=types.ContentTypes.TEXT)
async def set_description(msg: types.Message, state: FSMContext):
    await state.update_data(description=msg.text)
    await msg.reply("Отправь фото:")
    await CreateProfile.next()


@dp.message_handler(state=CreateProfile.photo, content_types=types.ContentTypes.PHOTO)
async def set_photo(msg: types.Message, state: FSMContext):
    photo_id = msg.photo[-1].file_id
    data = await state.get_data()

    save_profile(
        msg.from_user.id,
        data['name'],
        data['description'],
        photo_id
    )

    await msg.reply("✅ Анкета создана!")
    await state.finish()


# ---------- LIST ----------
@dp.message_handler(commands=['list'])
async def list_profiles(msg: types.Message):
    names = get_all_names()
    if not names:
        await msg.reply("❌ Анкет нет")
        return

    text = "📜 Персонажи:\n\n"
    for n in names:
        text += f"• {n[0]}\n"

    await msg.reply(text)


# ---------- WHO ----------
@dp.message_handler(commands=['who'])
async def who(msg: types.Message):
    await msg.reply("Введите имя персонажа:")


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_name(msg: types.Message):
    # Игнорируем команды
    if msg.text.startswith("/"):
        return

    profile = get_profile_by_name(msg.text)
    if not profile:
        await msg.reply("❌ Персонаж не найден")
        return

    user_id, name, description, photo = profile
    text = f"🧾 {name}\n\n{description}"

    await bot.send_photo(
        chat_id=msg.chat.id,
        photo=photo,
        caption=text
    )


# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
