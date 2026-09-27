import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]

SOURCE_CHANNEL = "@XauusdGoldMaster05"

DESTINATION_CHANNELS = [
    "@xauuusdgoldsignals292",
    "@bluepipsGold_Btc",
    "@TradeNovaLaba",
    "@bluepipsgoldbtc",
    "@tradewithfundamentalandtecnicala",
    "@narketnewssupclas",
]

app = Flask(__name__)

telegram_app = Application.builder().token(BOT_TOKEN).build()


async def copy_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.channel_post:
        return

    message = update.channel_post

    # صرف Main Channel کی posts copy ہوں گی
    if message.chat.username:
        source = "@" + message.chat.username
    else:
        source = str(message.chat.id)

    if source.lower() != SOURCE_CHANNEL.lower():
        return

    for destination in DESTINATION_CHANNELS:
        try:
            await context.bot.copy_message(
                chat_id=destination,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
        except Exception as e:
            print(f"Error copying to {destination}: {e}")


telegram_app.add_handler(
    MessageHandler(filters.ALL, copy_channel_post)
)


@app.route("/", methods=["GET"])
def home():
    return "Telegram Copy Bot is running!"


@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"


if __name__ == "__main__":
    telegram_app.run_polling()
