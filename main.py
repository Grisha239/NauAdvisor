import os
import json
from dotenv import load_dotenv
import telebot
from openai import OpenAI
import requests

load_dotenv()

# Yandex GPT
Yandex_Token = os.getenv("YANDEX_TOKEN")
Yandex_Folder = os.getenv("YANDEX_FOLDER")

# OpenAI GPT
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openaiModel = 'gpt-3.5-turbo-0125'
client = OpenAI(api_key=OPENAI_API_KEY)

# Telegram bot
BotToken = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BotToken)


@bot.message_handler(commands=['gpt'])
def answer_chat(message):
    text = message.text.replace('/gpt', '')

    yandex_prompt = {
        "modelUri": f'gpt://{Yandex_Folder}/yandexgpt-lite',
        'completionOptions': {
            'stream': False,
            'temperature': 0.6,
            'maxTokens': '2000'
        },
        'messages': [
            {'role': 'user', 'text': text}
        ]
    }
    yandex_url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Api-Key {Yandex_Token}'
    }
    response = requests.post(url=yandex_url, headers=headers, json=yandex_prompt)
    response_json = json.loads(response.text.replace("\'", '\"'))
    bot.send_message(chat_id=message.chat.id, text=f"Yandex answer:\n"
                                                   f"{response_json['result']['alternatives'][0]['message']['text']}")
    try:
        answer_openai = client.chat.completions.create(
            model=openaiModel,
            messages=[
                {'role': 'user', 'content': text}
            ]
        )
        bot.send_message(chat_id=message.chat.id, text=f"OpenAI answer:\n{answer_openai.choices[0].message}")
    except Exception as exception:
        bot.send_message(chat_id=message.chat.id, text=f"OpenAI answer:\n{exception}")


if __name__ == "__main__":
    print("Bot is running")
    bot.polling()
