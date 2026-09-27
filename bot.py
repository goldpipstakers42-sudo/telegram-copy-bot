import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

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

telegram_app = (
    Application.builder()
    .token(BOT_TOKEN)
    .updater(None)
    .build()
)


async def copy_channel_post(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.channel_post:
        return

    message = update.channel_post

    if message.chat.username:
        source = "@" + message.chat.username
    else:
        source = ""

    if source.lower() != SOURCE_CHANNEL.lower():
        return

    for destination in DESTINATION_CHANNELS:
        try:
            await context.bot.copy_message(
                chat_id=destination,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
            print(f"Copied message to {destination}")

        except Exception as e:
            print(f"Failed to copy to {destination}: {e}")


telegram_app.add_handler(
    MessageHandler(filters.ALL, copy_channel_post)
)


@app.route("/", methods=["GET"])
def home():
    return "Telegram Copy Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(
        request.get_json(force=True),
        telegram_app.bot,
    )

    asyncio.run(
        telegram_app.process_update(update)
    )

    return "OK"


async def setup_telegram():
    await telegram_app.initialize()

    webhook_base = os.environ.get("RENDER_EXTERNAL_URL")

    if not webhook_base:
        raise RuntimeError("RENDER_EXTERNAL_URL not found")

    webhook_url = webhook_base.rstrip("/") + "/webhook"

    await telegram_app.bot.set_webhook(
        url=webhook_url,
        allowed_updates=["channel_post", "edited_channel_post"],
    )

    print(f"Webhook set to: {webhook_url}")


if __name__ == "__main__":
    asyncio.run(setup_telegram())

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port,
    )
