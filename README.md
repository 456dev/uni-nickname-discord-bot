# uni nickname enforcer discord bot thing

written in discord.py
will load config from environment variables


## requirements
- poetry installed
- python 3.11 (not 3.12, apparently once of the libs doesnt like it)


## running from cloned repo
```bash
# install depends with poetry
poetry install

# copy the example env file
cp .env.example .env

# edit the file: currently every field is required
$EDITOR .env

# ensure the discord bot represented by the token has already joined the server given in the config

# run the bot

poetry run python bot/__init__.py
```

## running from cloned repo
```bash
# build the docker image
docker build . --tag=uninicknameenforcer

# run the bot
docker run -e DISCORD_BOT_TOKEN=xxx -e DISCORD_GUILD_ID=yyy -e DISCORD_CHANGED_NAME_ROLE_ID=zzz uninicknameenforcer
```