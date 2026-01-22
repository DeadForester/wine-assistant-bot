import telebot
from src.config import TELEGRAM_TOKEN
from src.agent.wine_agent import Agent

def run_telegram_bot(agent: Agent):
    bot = telebot.TeleBot(TELEGRAM_TOKEN)

    @bot.message_handler(commands=["start"])
    def start(message):
        ans = agent(message.text, session_id=message.chat.id)
        bot.send_message(message.chat.id, ans.output_text)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        ans = agent(message.text, session_id=message.chat.id)
        bot.send_message(message.chat.id, ans.output_text)

    print("✅ Бот запущен и готов принимать сообщения в Telegram!")
    bot.polling(none_stop=True)