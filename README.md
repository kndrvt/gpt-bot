# gpt-bot
This project is a simple Telegram bot for communication with ChatGPT.

### Requirements

- Docker
- Docker Swarm (optionally)

### Run
   
1) Create a gpt-bot Docker image from Dockerfile using following commands:
~~~bash
# if you have image named 'gpt-bot'
docker rmi gpt-bot

docker build -t gpt-bot .
~~~

2) Set environment variables according to your OpenAI key and Telegram token:
~~~bash
export OPENAI_API_KEY="<your key>"
export TELEGRAM_API_TOKEN="<your token>"
~~~

3) Launch a Docker container with your gpt-bot using following command:
~~~bash
docker run \
  --env OPENAI_API_KEY=$OPENAI_API_KEY \
  --env TELEGRAM_API_TOKEN=$TELEGRAM_API_TOKEN \
  --volume "$(pwd)"/bot.log:/bot.log \
  --name gpt-bot \
  --net host \
  --rm \
  gpt-bot
~~~

4) Optionally, you also can launch Docker Swarm service instead of single container:
~~~bash
docker swarm init

docker service create \
  --name gpt-bot-service \
  --replicas 1 \
  --env OPENAI_API_KEY=$OPENAI_API_KEY \
  --env TELEGRAM_API_TOKEN=$TELEGRAM_API_TOKEN \
  --mount type=bind,source="$(pwd)"/bot.log,destination=/bot.log \
  gpt-bot
~~~