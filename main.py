import yt_dlp
import asyncio
import aiofiles
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

API_TOKEN = '6203380442:AAHMZtZFsSlomzxhLQ0E3DTaMQ1KDDhy0'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Load language file
with open("lang.json", "r", encoding="utf-8") as file:
    lng = json.load(file)

# Link validation
def is_valid_url(url):
    extractors = yt_dlp.extractor.gen_extractors()
    for extractor in extractors:
        if extractor.suitable(url) and extractor.IE_NAME != 'generic':
            return True
    return False

# Start command
@dp.message_handler(commands=['start'])
async def welcome(message: Message):
    await message.answer(lng.get(f'{message.from_user.language_code}', ["Welcome"])[0])

# Help command
@dp.message_handler(commands=['help'])
async def helpme(message: Message):
    await message.answer(lng.get(f'{message.from_user.language_code}', ["Help"])[7], parse_mode='html', disable_web_page_preview=True)

# Download & send
@dp.message_handler(content_types=['text'])
async def send_message(message: Message):
    link = message.text
    if not is_valid_url(link):
        await message.answer(lng.get(f'{message.from_user.language_code}', ["Invalid URL"])[6])
        return
    
    statuss = await message.answer(lng.get(f'{message.from_user.language_code}', ["Downloading..."])[2])
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(title)s.%(ext)s',
        'cookiefile': 'cookies.txt'
    }
    
    try:
        async with asyncio.Lock():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                filesize = info.get('filesize_approx') or info.get('filesize')
                if filesize and filesize > 50 * 1024 * 1024:
                    await message.answer(lng.get(f'{message.from_user.language_code}', ["File too large"])[1])
                    return
                
                info_dict = ydl.extract_info(link, download=True)
                video_title = info_dict.get('title', 'video')
                file_path = f"{video_title}.mp4"
                
                await bot.edit_message_text(lng.get(f'{message.from_user.language_code}', ["Uploading..."])[3], chat_id=message.chat.id, message_id=statuss.message_id)
                
                async with aiofiles.open(file_path, 'rb') as file:
                    await bot.send_document(message.chat.id, file, caption=lng.get(f'{message.from_user.language_code}', ["Here is your video"])[8], parse_mode='html')
                
                os.remove(file_path)
                await bot.delete_message(message.chat.id, statuss.message_id)
    except Exception as e:
        print("ERROR:", e)
        await message.answer(lng.get(f'{message.from_user.language_code}', ["Error occurred"])[5])

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())