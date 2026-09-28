import os
import asyncio

from flask import Flask, request
from telegram import Update, ReplyParameters
from telegram.ext import Application, MessageHandler, filters


# =========================
# BOT TOKEN
# =========================

BOT_TOKEN = os.environ["BOT_TOKEN"]


# =========================
# MAIN / SOURCE CHANNEL
# =========================

SOURCE_CHANNEL = "@XauusdGoldMaster05"


# =========================
# DESTINATION CHANNELS
# =========================

DESTINATION_CHANNELS = [
    "@xauuusdgoldsignals292",
    "@bluepipsGold_Btc",
    "@TradeNovaLaba",
    "@bluepipsgoldbtc",
    "@tradewithfundamentalandtecnicala",
    "@narketnewssupclas",

    "@GoldMarketSignals1k",
    "@blueEdgeTradin",
    "@DiamondTradeFx2",
    "@dolarmanroyalteam",
    "@forextradingsignals181",
    "@agagsgzvsvsjsksns",
]


# =========================
# FLASK
# =========================

app = Flask(__name__)


# =========================
# TELEGRAM APPLICATION
# =========================

telegram_app = (
    Application.builder()
    .token(BOT_TOKEN)
    .updater(None)
    .build()
)


# ==========================================================
# MESSAGE MAPPING
#
# Main channel message ID
#        ↓
# Destination channel message ID
#
# Example:
# Main message 500
#        ↓
# Blue Edge message 1200
# ==========================================================

message_map = {}


# ==========================================================
# COPY CHANNEL POST
# ==========================================================

async def copy_channel_post(update, context):

    message = update.channel_post

    if not message:
        return

    # ------------------------------------------
    # Make sure this is our MAIN channel
    # ------------------------------------------

    if not message.chat.username:
        return

    source_username = "@" + message.chat.username

    if source_username.lower() != SOURCE_CHANNEL.lower():
        return

    source_message_id = message.message_id

    print(
        f"New message from {SOURCE_CHANNEL}: "
        f"{source_message_id}"
    )


    # ------------------------------------------
    # Check whether this message is a REPLY
    # to another message in the main channel
    # ------------------------------------------

    reply_parameters = None

    if message.reply_to_message:

        original_reply_id = message.reply_to_message.message_id

        print(
            f"Message {source_message_id} is a reply to "
            f"message {original_reply_id}"
        )

        # --------------------------------------
        # Find the copied parent message
        # for every destination channel
        # --------------------------------------

    # Save destination message IDs here
    destination_mapping = {}


    # ======================================================
    # SEND TO ALL DESTINATION CHANNELS
    # ======================================================

    for destination in DESTINATION_CHANNELS:

        try:

            # ------------------------------------------
            # If this message is a reply, find the
            # corresponding copied parent message
            # ------------------------------------------

            reply_parameters = None

            if message.reply_to_message:

                original_reply_id = (
                    message.reply_to_message.message_id
                )

                destination_messages = message_map.get(
                    original_reply_id,
                    {}
                )

                copied_parent_id = destination_messages.get(
                    destination
                )

                if copied_parent_id:

                    reply_parameters = ReplyParameters(
                        message_id=copied_parent_id
                    )

                    print(
                        f"Reply link created: "
                        f"{source_message_id} -> "
                        f"{copied_parent_id} "
                        f"in {destination}"
                    )

                else:

                    print(
                        f"WARNING: Parent message "
                        f"{original_reply_id} not found "
                        f"for {destination}"
                    )


            # ------------------------------------------
            # COPY THE MESSAGE
            # ------------------------------------------

            copied_message = await context.bot.copy_message(
                chat_id=destination,
                from_chat_id=message.chat.id,
                message_id=source_message_id,
                reply_parameters=reply_parameters
            )


            # ------------------------------------------
            # SAVE THE COPIED MESSAGE ID
            # ------------------------------------------

            destination_mapping[destination] = (
                copied_message.message_id
            )

            print(
                f"Copied {source_message_id} -> "
                f"{copied_message.message_id} "
                f"to {destination}"
            )


        except Exception as e:

            print(
                f"ERROR copying message "
                f"{source_message_id} "
                f"to {destination}: {e}"
            )


    # ======================================================
    # SAVE MAPPING
    # ======================================================

    message_map[source_message_id] = destination_mapping

    print(
        f"Mapping saved for message "
        f"{source_message_id}"
    )


# ==========================================================
# HANDLER
# ==========================================================

telegram_app.add_handler(
    MessageHandler(
        filters.ALL,
        copy_channel_post
    )
)


# ==========================================================
# HOME PAGE
# ==========================================================

@app.route("/")
def home():

    return "Telegram Copy Bot is running!"


# ==========================================================
# WEBHOOK
# ==========================================================

@app.route("/webhook", methods=["POST"])
async def webhook():

    try:

        data = request.get_json(force=True)

        update = Update.de_json(
            data,
            telegram_app.bot
        )

        await telegram_app.process_update(update)

        return "OK"

    except Exception as e:

        print(f"Webhook error: {e}")

        return "ERROR", 500


# ==========================================================
# SET WEBHOOK
# ==========================================================

async def setup_telegram():

    await telegram_app.initialize()

    render_url = os.environ.get(
        "RENDER_EXTERNAL_URL"
    )

    if not render_url:

        raise RuntimeError(
            "RENDER_EXTERNAL_URL is not set"
        )

    webhook_url = (
        render_url.rstrip("/")
        + "/webhook"
    )

    await telegram_app.bot.set_webhook(
        url=webhook_url,
        allowed_updates=[
            "channel_post"
        ]
    )

    print(
        f"Webhook set to: {webhook_url}"
    )


# ==========================================================
# START
# ==========================================================

if __name__ == "__main__":

    asyncio.run(
        setup_telegram()
    )

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
