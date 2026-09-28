import os
import asyncio

from flask import Flask, request
from telegram import Update, ReplyParameters
from telegram.ext import Application, MessageHandler, ContextTypes, filters


# =========================================================
# SETTINGS
# =========================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")

SOURCE_CHANNEL = "@XauusdGoldMaster05"

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


# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)


# =========================================================
# TELEGRAM APPLICATION
# =========================================================

telegram_app = (
    Application.builder()
    .token(BOT_TOKEN)
    .updater(None)
    .build()
)


# =========================================================
# MESSAGE MAPPING
#
# source message ID
#       ↓
# destination channel
#       ↓
# destination message ID
#
# Example:
# {
#   123: {
#       "@channel1": 456,
#       "@channel2": 789
#   }
# }
# =========================================================

message_map = {}


# =========================================================
# COPY CHANNEL MESSAGE
# =========================================================

async def copy_channel_post(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.channel_post

    if not message:
        return

    # Only copy from our main/source channel
    if not message.chat.username:
        return

    source_username = "@" + message.chat.username

    if source_username.lower() != SOURCE_CHANNEL.lower():
        return

    print(
        f"Received message from source: "
        f"{source_username} | "
        f"Message ID: {message.message_id}"
    )


    # =====================================================
    # CHECK IF THIS MESSAGE IS A REPLY
    # =====================================================

    is_reply = message.reply_to_message is not None

    parent_map = {}

    if is_reply:

        parent_source_id = message.reply_to_message.message_id

        print(
            f"This is a reply to source message: "
            f"{parent_source_id}"
        )

        parent_map = message_map.get(
            parent_source_id,
            {}
        )

        # If we don't know the original copied message,
        # don't send the update as a standalone message.
        if not parent_map:

            print(
                "Parent message mapping not found. "
                "Reply skipped."
            )

            return


    # =====================================================
    # STORE DESTINATION MESSAGE IDs
    # =====================================================

    current_message_map = {}


    # =====================================================
    # COPY TO ALL DESTINATION CHANNELS
    # =====================================================

    for destination in DESTINATION_CHANNELS:

        try:

            copy_arguments = {
                "chat_id": destination,
                "from_chat_id": message.chat.id,
                "message_id": message.message_id,
            }


            # =================================================
            # IF SOURCE MESSAGE IS A REPLY
            # MAKE DESTINATION MESSAGE A REPLY TOO
            # =================================================

            if is_reply:

                destination_parent_id = parent_map.get(
                    destination
                )

                if not destination_parent_id:

                    print(
                        f"No parent mapping for "
                        f"{destination}. Skipping."
                    )

                    continue


                copy_arguments["reply_parameters"] = (
                    ReplyParameters(
                        message_id=destination_parent_id
                    )
                )


            # =================================================
            # COPY MESSAGE
            # =================================================

            copied_message = await context.bot.copy_message(
                **copy_arguments
            )


            # Save destination message ID
            current_message_map[destination] = (
                copied_message.message_id
            )


            print(
                f"Copied to {destination} "
                f"-> message ID "
                f"{copied_message.message_id}"
            )


        except Exception as e:

            print(
                f"ERROR copying to "
                f"{destination}: {e}"
            )


    # =====================================================
    # SAVE THIS SOURCE MESSAGE'S DESTINATION MAPPINGS
    # =====================================================

    if current_message_map:

        message_map[message.message_id] = (
            current_message_map
        )

        print(
            f"Saved mapping for source message "
            f"{message.message_id}"
        )


# =========================================================
# TELEGRAM HANDLER
# =========================================================

telegram_app.add_handler(
    MessageHandler(
        filters.ALL,
        copy_channel_post
    )
)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return "Telegram Copy Bot is running."


# =========================================================
# WEBHOOK
# =========================================================

@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        data = request.get_json(force=True)

        update = Update.de_json(
            data,
            telegram_app.bot
        )

        # IMPORTANT:
        # This is a synchronous Flask route.
        # It avoids Flask async-view problems.
        asyncio.run(
            telegram_app.process_update(update)
        )

        return "OK", 200


    except Exception as e:

        print(
            f"WEBHOOK ERROR: {e}"
        )

        return "ERROR", 500


# =========================================================
# SET TELEGRAM WEBHOOK
# =========================================================

async def setup_telegram():

    await telegram_app.initialize()

    render_url = os.environ.get(
        "RENDER_EXTERNAL_URL"
    )

    if not render_url:

        raise RuntimeError(
            "RENDER_EXTERNAL_URL is not set."
        )


    webhook_url = (
        render_url.rstrip("/")
        + "/webhook"
    )


    await telegram_app.bot.set_webhook(
        url=webhook_url,
        allowed_updates=[
            "channel_post",
            "edited_channel_post",
        ],
    )


    print(
        "Webhook set to:",
        webhook_url
    )


# =========================================================
# START SERVER
# =========================================================

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
