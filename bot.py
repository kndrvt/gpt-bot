from telegram.ext import Application, MessageHandler
from telegram.ext.filters import ALL
from collections import defaultdict
import logging
import openai
import os

history = defaultdict(list)

async def generate_gpt_response(update, context):
    if not update.message:
        return

    user_input = update.message.text
    if not user_input:
        return

    global history
    h = history[update.effective_chat.id]

    logging.info("{} >: {}".format(update.effective_chat.id, user_input))

    h.append({"role": "user", "content": user_input})
    if len(h) > 15:
        h = h[-15:]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=list(h)
    )

    content = response.choices[0].message.content
    h.append({"role": response.choices[0].message.role, "content": content})
    if len(h) > 15:
        h = h[-15:]
    
    
    logging.info("{} <: {}".format(update.effective_chat.id, content))

    await context.bot.send_message(chat_id=update.effective_chat.id, text=content)

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
