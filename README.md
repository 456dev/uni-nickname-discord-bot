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

## discord setup

need a bot account thats in the discord
it needs to be added with the bot permissions MANAGE_NICKNAMES and MANAGE_ROLES

as well as application.commands

get the client id from your discord dashboard, and add the bot using this url, replacing the dummy id
```
https://discord.com/api/oauth2/authorize?client_id=<clientid>&permissions=402653184&scope=bot%20applications.commands
```

reset the bot token, copy it, and put it in the config (.env or docker command)

in server setup

move the auto-created bot role to the very top, above the highest member role (other bot roles, that it doesnt need to set the nicknames of, are fine)

create a low role to give once the nickname has been changed
copy the role's id, and paste it into the confg
copy the guild id and put it into the config

create a channel to act as the first channel the user will see
this could be a rules channel, but if you want to have it autohide later, you probably want it seperate

in this target channel, in advanced permissions, set @everyone to allow view channel, deny sending messages
as well as the bot role.
additionally, allow your user (or a staff role that you have) to allow sending messages in that channel
optionally, to autohide the channel after they have changed their name to the correct format, deny the low role the ability to see it

next, start the bot. you may want to alter the permissions of the /slash commands, in integration settings

by default, /nick is usable by everyone to change their name withing the specified format,
/nickadmin is usable by people with manage_nicknames,
and /start is usable by people with manage server

go to your inital channel, and type /start, optionally providing a message to override the one sent by the bot by default
this will insert the button into the channel

next set @everyones global permissions in role settings to -view channels by default
and set your low role to allow viewing channels
(or an alternative like not being able to send messages / can)

ensure that @everyone doesnt have change nickname, so they can't bypass the format

