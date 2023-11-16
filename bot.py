"""The simple Telegram bot to communicate with ChatGPT 3.5"""

# pylint: disable=missing-function-docstring
# pylint: disable=broad-exception-caught
# pylint: disable=global-variable-not-assigned

import logging
import os
import time
from collections import defaultdict

import openai
from telegram.ext import Application, MessageHandler
from telegram.ext.filters import ALL

history = defaultdict(list)
MAX_HISTORY_SIZE = 16
MAX_TG_MSG_SIZE = 4096
EXPIRATION_PERIOD = 30 * 60 # 30 munutes

def append_history_entry(h, role, content):
    h.append((time.time(), {"role": role, "content": content}))
    if len(h) > MAX_HISTORY_SIZE:
        del h[:-MAX_HISTORY_SIZE]

    now = time.time()
    for i, e in enumerate(h):
        if e[0] + EXPIRATION_PERIOD > now:
            del h[:i]
            break

async def generate_gpt_response(update, context):
    if not update.message:
        return

    user_input = update.message.text
    if not user_input:
        return

    global history
    h = history[update.effective_chat.id]

    logging.info("%d >: %s", update.effective_chat.id, user_input)

    append_history_entry(h, "user", user_input)
    content = ""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[e[1] for e in h]
        )

        content = response.choices[0].message.content
        append_history_entry(h, response.choices[0].message.role, content)
    except Exception as exc:
        exc = str(exc)
        delta = 25
        content = f"```ChatGPT API error: \
            {exc if len(exc) < MAX_TG_MSG_SIZE - delta else exc[:MAX_TG_MSG_SIZE - delta]}```"
        h.clear()

    logging.info("%d <: %s", update.effective_chat.id, content)
    logging.info("history size: %s", len(h))

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=content,
                                   parse_mode="MarkdownV2")

def main(k, t):
    logging.basicConfig(filename='bot.log',
                        format='%(asctime)s %(levelname)-5s %(message)s',
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    openai.api_key = k
    application = Application.builder().token(t).build()
    application.add_handler(MessageHandler(filters=ALL, callback=generate_gpt_response))

    try:
        application.run_polling()
    except Exception as ex:
        logging.error("%s", ex)

if __name__ == "__main__":
    key = os.getenv("OPENAI_API_KEY")
    token = os.getenv("TELEGRAM_API_TOKEN")
    if not key or not token:
        raise ValueError("Cannot start without initialization \
                        of OPENAI_API_KEY and TELEGRAM_API_TOKEN variables")
    main(key, token)
