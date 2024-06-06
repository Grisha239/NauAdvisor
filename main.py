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
database = redis.Redis(host=redis_host, port=redis_port, db=0)


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
    except Exception as exception:
        bot.send_message(chat_id=message.chat.id, text=f"OpenAI exception:\n{exception}")

    try:
        database.set(name=str(message.from_user.id), value=str(text))
        bot.send_message(chat_id=message.chat.id, text=f"Conversation:\n{text}")
    except Exception as exception:
        bot.send_message(chat_id=message.chat.id, text=f"Redis exception:\n{exception}")


if __name__ == "__main__":
    print("Bot is running")
    bot.polling()
