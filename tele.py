import telebot
import urllib.parse
import requests
import json

bot=telebot.TeleBot("")

@bot.message_handler(commands=["start"])
def start(message):
    # bot.reply_to(message,"你好")
    bot.reply_to(message,"你好,我是你的算命机器人")

@bot.message_handler(func=lambda message:True)
def echo_all(message):
    try:
        # encoded_message = urllib.parse.quote(message.text)
        encoded_message=message.text
        # 将chat_id作为参数传递给服务器
        chat_id = str(message.chat.id)
        print(chat_id)
        response = requests.post(
            'http://localhost:8000/chat',
            params={
                'query': encoded_message,
                'chat_id': chat_id
            },
            timeout=100
        )
        if response.status_code == 200:
            ai_response = json.loads(response.text)
            print(ai_response)
            if "output" in ai_response:
                bot.reply_to(message, ai_response["output"])
            else:
                bot.reply_to(message, "对不起，我不知道怎么回答你")
    except Exception as e:
        bot.send_message(message.chat.id, "发生了错误")

bot.infinity_polling()