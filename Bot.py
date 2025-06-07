from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import sqlite3

# Bot tokeningiz
TOKEN = "7869495986:AAExrwwdFOu8Dyqcdp6fvr7qD8eCClPAJG8"

# Hamkorlik kanallari
CHANNELS = ["@Khurbon_off", "https://t.me/nakrutkachi_2"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Ma'lumotlar bazasini yaratish
conn = sqlite3.connect("movies.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    movie_name TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE
)
""")
conn.commit()
conn.close()

# Obuna tekshirish
async def is_subscribed(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# Start buyrug‘i
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await message.answer("🎬 Salom! Kinolarni kod orqali topish mumkin!")

# Kinoni kod orqali topish
@dp.message_handler()
async def get_movie(message: types.Message):
    code = message.text.strip()
    
    if not await is_subscribed(message.from_user.id):
        await message.answer(f"❌ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:\n{CHANNELS}")
        return
    
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT movie_name FROM movies WHERE code=?", (code,))
    result = cursor.fetchone()
    conn.close()

    if result:
        await message.answer(f"🔎 Film topildi: {result[0]}")
    else:
        await message.answer("❌ Kodingizga mos film topilmadi!")

# Adminlarni qo‘shish
@dp.message_handler(commands=["add_admin"])
async def add_admin(message: types.Message):
    admin_id = message.from_user.id
    
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admins (user_id) VALUES (?)", (admin_id,))
    conn.commit()
    conn.close()
    
    await message.answer("✅ Siz admin sifatida qo‘shildingiz!")

# Adminlarni tekshirish
def is_admin(user_id):
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM admins WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return bool(result)

# Admin tomonidan kinolarni qo‘shish
@dp.message_handler(commands=["add"])
async def add_movie(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    _, code, movie_name = message.text.split(maxsplit=2)
    
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO movies (code, movie_name) VALUES (?, ?)", (code, movie_name))
    conn.commit()
    conn.close()
    
    await message.answer(f"✅ Film qo‘shildi: {movie_name}")

# Admin tomonidan kinolarni o‘chirish
@dp.message_handler(commands=["delete"])
async def delete_movie(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    _, code = message.text.split()
    
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE code=?", (code,))
    conn.commit()
    conn.close()
    
    await message.answer("❌ Kodga bog‘langan film o‘chirildi!")

# Botni ishga tushirish
if __name__ == "__main__":
    executor.start_polling(dp)
