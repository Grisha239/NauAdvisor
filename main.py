import os
import json
from dotenv import load_dotenv
import telebot
from openai import OpenAI
import requests
import redis

load_dotenv()

# OpenAI GPT
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openaiModel = 'gpt-3.5-turbo-0125'
client = OpenAI(api_key=OPENAI_API_KEY)

# Telegram bot
BotToken = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BotToken)

# Redis database
redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
database = redis.Redis(host=redis_host, port='6379', db=0)

try:
    database.set("Hello", "World")
except Exception as exception:
    bot.send_message(chat_id=-4048345106, text=f"Redis Test exception:\n{exception}")


@bot.message_handler(commands=['gpt'])
def answer_chat(message):
    text = message.text.replace('/gpt', '')

    try:
        answer_openai = client.chat.completions.create(
            model=openaiModel,
            messages=[
                {'role': 'user', 'content': text}
            ]
        )
        bot.send_message(chat_id=message.chat.id, text=f"OpenAI answer:\n{answer_openai.choices[0].message.content}")
    except Exception as exception2:
        bot.send_message(chat_id=message.chat.id, text=f"OpenAI exception:\n{exception2}")

    try:
        database.set("Hello", "World")
    except Exception as exception2:
        bot.send_message(chat_id=message.chat.id, text=f"Redis exception:\n{exception2}")


if __name__ == "__main__":
    print("Bot is running")
    bot.polling()
