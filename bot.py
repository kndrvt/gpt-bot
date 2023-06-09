from telegram.ext import Application, MessageHandler
from telegram.ext.filters import ALL
from collections import defaultdict
import logging
import openai
import os
import time

history = defaultdict(list)
max_history_size = 25
expiration_period = 30 * 60 # 30 munutes

def append_history_entry(h, role, content):
    h.append((time.time(), {"role": role, "content": content}))
    if len(h) > max_history_size:
        h = h[-max_history_size:]

    now = time.time()
    for i, e in enumerate(h):
        if e[0] + expiration_period > now:
           h = h[i:]
           break

async def generate_gpt_response(update, context):
    if not update.message:
        return

    user_input = update.message.text
    if not user_input:
        return

    global history
    h = history[update.effective_chat.id]

    logging.info("{} >: {}".format(update.effective_chat.id, user_input))

    append_history_entry(h, "user", user_input)

    content = ""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[e[1] for e in h]
        )
        content = response.choices[0].message.content
    except Exception as exc:
        content = "`ChatGPT API error: {}`".format(exc)

    append_history_entry(h, "assistant", content)

    logging.info("{} <: {}".format(update.effective_chat.id, content))

    await context.bot.send_message(chat_id=update.effective_chat.id, text=content, parse_mode="Markdown")

def main(key, token):
    logging.basicConfig(filename='bot.log', 
                        format='%(asctime)s %(levelname)-5s %(message)s', 
                        level=logging.INFO, 
                        datefmt='%Y-%m-%d %H:%M:%S')
    openai.api_key = key
    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(filters=ALL, callback=generate_gpt_response))

    try:
        application.run_polling()
    except Exception as ex:
        logging.error("{}", ex)

if __name__ == "__main__":
    key = os.getenv("OPENAI_API_KEY")
    token = os.getenv("TELEGRAM_API_TOKEN")
    if not key or not token:
        raise Exception("Cannot start without initialization of OPENAI_API_KEY and TELEGRAM_API_TOKEN variables")
    main(key, token)
