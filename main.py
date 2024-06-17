import os
import json
from dotenv import load_dotenv
import telebot
from openai import OpenAI
import requests
import redis
import json

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


@bot.message_handler(func=lambda message: message.text & message.text[0] != "/")
def answer_chat(message):
    text = message.text

    try:
        info = database.get(message.from_user.id)
        if info:
            info = json.loads(info)
            info["conversation"].append({"role": "user", "content": text})
        else:
            info = {"conversation": [
                {"role": "system", "content": "You are helpful assistant"},
                {"role": "user", "content": text}],
                "context": True}

        if info["context"]:
            answer_openai = client.chat.completions.create(
                model=openaiModel,
                messages=info["conversation"])
        else:
            answer_openai = client.chat.completions.create(
                model=openaiModel,
                messages=[
                    {"role": "system", "content": "You are helpful assistant"},
                    {"role": "user", "content": text},
                ])

        info["conversation"].append({"role": "assistant", "content": answer_openai.choices[0].message.content})
        database.set(message.from_user.id, json.dumps(info))
        bot.send_message(chat_id=message.chat.id, text=f"OpenAI answer:\n{answer_openai.choices[0].message.content}")
    except Exception as exception:
        bot.send_message(chat_id=message.chat.id, text=f"OpenAI exception:\n{exception}")


@bot.message_handler(commands=['clear'])
def answer_chat(message):
    text = message.text
    if text == "/clear":
        database.set(message.from_user.id, json.dumps(default_db_info()))
    bot.send_message(chat_id=message.chat.id, text=f"Предыдущий диалог был удалён")


@bot.message_handler(commands=['disable_context'])
def answer_chat(message):
    info = database.get(message.from_user.id)
    if info:
        info = json.loads(info)
        info["context"] = False
        database.set(message.from_user.id, json.dumps(info))
    bot.send_message(chat_id=message.chat.id, text=f"Сейчас контекст: Не используется")


@bot.message_handler(commands=['enable_context'])
def answer_chat(message):
    info = database.get(message.from_user.id)
    if info:
        info = json.loads(info)
        info["context"] = True
        database.set(message.from_user.id, json.dumps(info))
    bot.send_message(chat_id=message.chat.id, text=f"Сейчас контекст: Используется")


@bot.message_handler(commands=['start'])
def start_chat(message):
    database.set(message.from_user.id, json.dumps(default_db_info()))
    bot.send_message(chat_id=message.chat.id,
                     text="Привет! Это бот для удобной работы с ChatGPT от команды nau.\n\n"
                          "Общаясь с этим ботом, вы соглашаетесь на то, что все ваши запросы могут быть использованы в аналитических целях и для обучения моделей.\n\n"
                          "Доступные команды:\n"
                          "/gpt - запрос в модель\n"
                          "/clear - очистить контекст диалога\n"
                          "/disable_context - отключить контекст\n"
                          "/enable_context - включить контекст\n\n"
                          "<b>ВНИМАНИЕ!</b> Пожалуйста, не отправляйте в запросах информацию, которая содержит NDA или другие приватные или персональные данные.",
                     parse_mode='HTML')


def default_db_info():
    return {"conversation": [
        {"role": "system", "content": "You are helpful assistant"}],
        "context": True}


if __name__ == "__main__":
    print("Bot is running")
    bot.polling()
