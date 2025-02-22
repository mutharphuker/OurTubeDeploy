import yt_dlp
import telebot
from telebot import types
import threading
import requests
import json
import sys
import os
import re

bot = telebot.TeleBot('6203380442:AAHM9BZtZFsSlomzxhLQ0E3DTaMQ1KDDhy0')

# language
with open("lang.json", "r", encoding="utf-8") as file:
	lng = json.load(file)

# commands
@bot.message_handler(commands=['start'])
def welcome(message):
	msg = bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][0])

@bot.message_handler(commands=['help'])
def helpme(message):
	msg = bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][7], parse_mode='html', disable_web_page_preview=True)

# link validation
def is_valid_url(url):
    extractors = yt_dlp.extractor.gen_extractors()
    for extractor in extractors:
        if extractor.suitable(url) and extractor.IE_NAME != 'generic':
            return True
    return False
# download & send	
@bot.message_handler(content_types=['text'])
def send_message(message):
	link = message.text
	try:
		if is_valid_url(link):
			statuss = bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][2])
			ydl_opts = {
				'format': 'best',
				'outtmpl': '%(title)s.%(ext)s',
				'cookiefile': 'cookies.txt',
			}
			with yt_dlp.YoutubeDL(ydl_opts) as ydl:
				info = ydl.extract_info(link, download=False)
				filesize = info.get('filesize_approx') or info.get('filesize')
				if filesize and filesize > 50 * 1024 * 1024:
					bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][1])
				else:
					info_dict = ydl.extract_info(link, download=True)
					video_title = info_dict.get('title', 'video')
					file_path = f"{video_title}.mp4"
				
			bot.edit_message_text(lng[f'{message.from_user.language_code}'][3], chat_id=message.chat.id, message_id=statuss.message_id)
			def send_video(path):
				bot.send_document(message.chat.id, open(path, 'rb'), caption=lng[f'{message.from_user.language_code}'][8], parse_mode='html')
			thread2 = threading.Thread(target=send_video(file_path))
			thread2.start()

			os.remove(file_path)
			bot.delete_message(message.chat.id, statuss.message_id)
		else:
			bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][6])
	except Exception as e:
		print("ERROR: " + repr(str(e)))
		bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][5])
		
print("Bot is running...")
bot.polling(none_stop=True)