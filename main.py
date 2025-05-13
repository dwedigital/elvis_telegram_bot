"""Elvis Bot"""

import logging
import os

import requests
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# load .env file
load_dotenv()

N8N_TEST_URL = "https://pinpoint.app.n8n.cloud/webhook-test/"
N8N_PROD_URL = "https://pinpoint.app.n8n.cloud/webhook/"

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

client = OpenAI()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=update.message.text
    )


async def story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a story when the command /story is issued."""
    logging.info("Story command received")

    prompt = "" if len(context.args) == 0 else " ".join(context.args)

    logging.info("Prompt: %s", prompt)

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions="you are a frinedly and fun story writer that is creative and changes their style based on the context of the story",
        max_output_tokens=50,
        input=(
            "Give me a one line story about a dachshund named elvis"
            if len(prompt) == 0
            else "Give me a one line story about a dachshund named elvis with the following context: "
            + prompt
        ),
    )
    logging.info("Response: %s", response)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=response.output_text
    )

    requests.post(
        N8N_PROD_URL + "elvis_photo",
        json={
            "prompt": (
                "Give me a photo of a black and tan dachshund named elvis"
                if len(prompt) == 0
                else "Give me a photo of a black and tan dachshund wearing the following outfit: "
                + prompt
            )
        },
        timeout=10,
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    story_handler = CommandHandler("story", story)
    application.add_handler(story_handler)

    application.run_polling()
