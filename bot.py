import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests

# Включение логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен вашего бота
TOKEN = '7383751878:AAFZhigXGlocexMbe-VN8wHqkDkfJwpDBGs'
CHANNEL_USERNAME = '@markettwits'
TARGET_BOT_USERNAME = '@chatsgpts_bot'

# Словарь для хранения ID пользователей
users = {}

def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    users[user.id] = user
    update.message.reply_text('Привет! Я бот, который пересылает новости и отвечает на них.')

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Используйте /start для начала.')

def handle_channel_post(update: Update, context: CallbackContext) -> None:
    if update.channel_post:
        message = update.channel_post.text
        # Формируем сообщение для другого бота
        request_text = f'Объясни эту новость простым языком для обывателей, также предположи, как новость может отразиться на рынке, если эта новость не влияет на рынок, не делай предположений. Обоснуй предположения. Новость: {message}'
        
        # Отправляем сообщение другому боту
        response = requests.post(
            url=f'https://api.telegram.org/bot{TOKEN}/sendMessage',
            data={'chat_id': TARGET_BOT_USERNAME, 'text': request_text}
        )
        
        # Получаем ответ от другого бота
        response_data = response.json()
        if response_data.get("ok"):
            response_message = response_data['result']['text']
            # Рассылаем ответ всем пользователям
            for user_id in users:
                context.bot.send_message(chat_id=user_id, text=response_message)

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Обработчик сообщений из канала
    dispatcher.add_handler(MessageHandler(Filters.chat(username=CHANNEL_USERNAME) & Filters.text, handle_channel_post))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
