FROM python:3.8

COPY . .

RUN pip install python-telegram-bot==20.02
RUN pip install openai==0.27.2

CMD ["python", "bot.py"]