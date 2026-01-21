import telebot
from config import TELEGRAM_TOKEN

def run_telegram_bot(agent):
    bot = telebot.TeleBot(TELEGRAM_TOKEN)

    @bot.message_handler(commands=["start"])
    def start(message):
        ans = agent(message.text, session_id=str(message.chat.id))
        text = ans.output_text.strip() if ans.output_text else "Извините, я не смогла сформулировать ответ. Попробуйте переформулировать вопрос."
        bot.send_message(message.chat.id, text)

    @bot.message_handler(func=lambda _: True)
    def handle_message(message):
        ans = agent(message.text, session_id=str(message.chat.id))
        text = ans.output_text.strip() if ans.output_text else "Извините, я не поняла ваш запрос. Могу ли я чем-то помочь?"
        bot.send_message(message.chat.id, text)

    print("✅ Бот запущен и готов принимать сообщения в Telegram!")
    bot.polling(none_stop=True)