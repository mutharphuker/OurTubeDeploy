import yt_dlp
import telebot
from telebot import types
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

# download & send	
@bot.message_handler(content_types=['text'])
def send_message(message):
	link = message.text
	try:
		statuss = bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][2])
		ydl_opts = {
			'format': 'bestvideo+bestaudio',
			'outtmpl': '%(title)s.%(ext)s',
		}
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			info_dict = ydl.extract_info(link, download=True)
			video_title = info_dict.get('title', 'video')
			file_path = f"{video_title}.mp4"
			
		bot.edit_message_text(lng[f'{message.from_user.language_code}'][3], chat_id=message.chat.id, message_id=statuss.message_id)
		# Send the video file to the user
		with open(file_path, 'rb') as video:
			bot.send_video(message.chat.id, video, caption=lng[f'{message.from_user.language_code}'][8], parse_mode='html')

		os.remove(file_path)
		bot.delete_message(message.chat.id, statuss.message_id)
		# yt = YouTube(link, use_oauth=True, allow_oauth_cache=True)
		# ys = yt.streams.get_highest_resolution()
		# if ys.filesize >= 50000000:
		# 	bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][1])
		# else:
		# 	bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][2])
		# 	path = ys.download('videos/')
		# 	bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][3])
		# 	bot.send_video(message.chat.id, video=open(path, "rb"), supports_streaming=True)
		# 	os.remove(path)
	except exceptions.AgeRestrictedError: # type: ignore
		bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][4])
	except exceptions.RegexMatchError: # type: ignore
		bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][6])
	except Exception as e:
		bot.send_message(message.chat.id, lng[f'{message.from_user.language_code}'][5])
		print("ERROR should be below:")
		print(repr(e))
		
print("Bot is running...")
bot.polling(none_stop=True)
