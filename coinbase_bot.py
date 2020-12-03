from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackContext
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, ParseMode
from telegram.utils.helpers import escape_markdown
import logging
import json
import httpx
import os
from coinbase_sql import check_api, delete_token

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def info(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi!')

def unknown(update, context) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def token_event(context) -> None:

    urls = [
        {'name':'coinbase', 'url':'https://api.pro.coinbase.com/currencies', 'table':'coinbase_pro', 
        'api_elements': {'name':'name', 'id':'id'}},
        {'name':'acdx', 'url':'https://api.acdx.io/v1/tokens', 'json_element': 'tokens', 'table':'acdx', 
        'api_elements': {'name':'token_code', 'id':'token_code'}},
        {'name':'binance', 'url':'https://api.binance.com/api/v3/exchangeInfo', 'json_element': 'symbols', 'table':'binance', 
        'api_elements': {'name':'symbol', 'id':'baseAsset'}}
    ]

    for url in urls:
        if url.get('json_element'):
            req = httpx.get(url['url']).json()[url['json_element']]
        else:
            req = httpx.get(url['url']).json()

        token = check_api(req, url['table'], url['api_elements'])
        if token:
            context.bot.send_message(chat_id=os.environ.get("TELEGRAM_CHAT_ID"), text=f'''*New {url["name"].title()} listing:*

Name: {token[0]}
Symbol: {token[1]}''', 
parse_mode=ParseMode.MARKDOWN)

        deleted_token = delete_token(req, url['table'])
        if deleted_token:
            context.bot.send_message(chat_id=os.environ.get("TELEGRAM_CHAT_ID"), text=f'New {url["name"].title()} delisting: {deleted_token}')

def main():
    updater = Updater(token=os.environ.get("TELEGRAM_API"), use_context=True)
    j = updater.job_queue
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    job = j.run_repeating(token_event, interval=30, first=0)
    updater.start_polling()


if __name__ == '__main__':
    main()