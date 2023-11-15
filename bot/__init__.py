import logging
import os
import sys
from typing import Optional

import discord
from discord import app_commands
from discord import ui
from dotenv import load_dotenv

load_dotenv()
logging.getLogger().setLevel(level=logging.INFO)

def require_env(name: str) -> str:
    value = os.environ.get(name, None)
    if not value:
        logging.critical(f"missing env {name}. make sure you copy "
                         f".env.example to .env and fill it out")
        sys.exit(1)
    return value


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents,
        guild: discord.abc.Snowflake):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)
        self.main_guild = guild

    # In this basic example, we just synchronize the app commands to one
    # guild. Instead of specifying a guild to every command, we copy over our
    # global commands instead. By doing so, we don't have to wait up to an
    # hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=self.main_guild)
        await self.tree.sync(guild=self.main_guild)
        self.add_view(PersistentView())


intents = discord.Intents.default()
intents.members = True
guild = discord.Object(id=int(require_env("DISCORD_GUILD_ID")))
target_role = discord.Object(
    id=int(require_env("DISCORD_CHANGED_NAME_ROLE_ID")))
client = MyClient(intents=intents, guild=guild)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@discord.app_commands.default_permissions(manage_guild=True)
@client.tree.command(name="start")
async def setup(interaction: discord.Interaction, msg: Optional[str] = None):
    msg = msg or "Please Change your Nickname to continue:"
    await interaction.response.send_message(msg, view=PersistentView())


@discord.app_commands.default_permissions(manage_nicknames=True)
@client.tree.command(name="nickadmin",
                     description="Setup Nickname for other user")
async def nickname_other_command(interaction: discord.Interaction,
    target: Optional[discord.Member] = None, name: Optional[str] = None,
    university: Optional[str] = None):
    target = target or interaction.user

    if name and university:
        new_nickname = format_nickname(name, university)
        logging.info(
            f"{interaction.user.name=} set {target.name} nickname to {new_nickname}")
        try:
            await interaction.guild.get_member(target.id).edit(
                nick=new_nickname,
                reason=f"{interaction.user.name} set nickname using bot")
        except discord.errors.Forbidden as e:
            logging.warning(
                f"unable to {interaction.user.name=} set {target.name} nickname to {new_nickname}")
            await interaction.response.send_message(
                f"A Permission Error has occured while changing {target.global_name or target.name}'s Nickname. Ensure the bot has the MANAGE_NICKNAMES permission, the target is not the server owner, and the bot's role is above all others",
                ephemeral=True)
            return
        try:
            await target.add_roles(target_role,
                                   reason=f"{interaction.user.name} set nickname using bot")
        except discord.errors.Forbidden as e:
            logging.warning(f"unable to add role to {target.name}")
            await interaction.response.send_message(
                f"A Permission Error has occured while changing {target.global_name or target.name}'s Nickname. Ensure the bot has the MANAGE_NICKNAMES permission, the target is not the server owner, and the bot's role is above all others",
                ephemeral=True)
            return
        await interaction.response.send_message(
            f"You have set {target.global_name or target.name}'s Nickname to \"{new_nickname}\"",
            ephemeral=True)
        return
    await interaction.response.send_modal(
        NicknameEntry(target=target, default_name=name,
                      default_university=university))


@client.tree.command(name="nick", description="Setup Nickname")
async def nickname_command(interaction: discord.Interaction):
    await interaction.response.send_modal(
        NicknameEntry())


def format_nickname(name: str, university: str) -> str:
    name = name.strip()
    university = university.strip()
    name = name[slice(None, 32 - len(" | ") - len(university))]
    formatted = f"{name} | {university}"
    return formatted


class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Change Nickname',
                       style=discord.ButtonStyle.primary,
                       custom_id='persistent_view:start')
    async def change_nickname(self, interaction: discord.Interaction,
        button: discord.ui.Button):
        await interaction.response.send_modal(NicknameEntry())


class NicknameEntry(ui.Modal, title='Set Nickname'):
    name = ui.TextInput(label="tmp1", required=True,
                        default="tmp2", min_length=2, max_length=29)
    university = ui.TextInput(label="tmp3", required=True,
                              default="tmp4", max_length=15, min_length=3)

    def __init__(self, default_name: Optional[str] = None,
        default_university: Optional[str] = None,
        target: Optional[discord.Member] = None):
        self.target = target

        self.name.label = f"{target.global_name or target.name}'s First Name" if target else "First Name"
        self.university.label = f"{target.global_name or target.name}'s University" if target else "University"
        self.name.default = default_name
        self.university.default = default_university
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        new_nickname = format_nickname(self.name.value, self.university.value)
        if self.target:
            logging.info(
                f"{interaction.user.name=} set {self.target.name} nickname to {new_nickname}")
            try:
                await interaction.guild.get_member(self.target.id).edit(
                    nick=new_nickname,
                    reason=f"{interaction.user.name} set nickname using bot")
            except discord.errors.Forbidden as e:
                logging.warning(
                    f"unable to {interaction.user.name=} set {self.target.name} nickname to {new_nickname}")
                await interaction.response.send_message(
                    f"A Permission Error has occured while changing {self.target.global_name or self.target.name}'s Nickname. Ensure the bot has the MANAGE_NICKNAMES permission, the target is not the server owner, and the bot's role is above all others",
                    ephemeral=True)
                return
            try:
                await self.target.add_roles(target_role,
                                            reason=f"{interaction.user.name} set nickname using bot")
            except discord.errors.Forbidden as e:
                logging.warning(f"unable to add role to {self.target.name}")
                await interaction.response.send_message(
                    f"A Permission Error has occured while changing {self.target.global_name or self.target.name}'s Nickname. Ensure the bot has the MANAGE_NICKNAMES permission, the target is not the server owner, and the bot's role is above all others",
                    ephemeral=True)
                return
            await interaction.response.send_message(
                f"You have set {self.target.global_name or self.target.name}'s Nickname to \"{new_nickname}\"",
                ephemeral=True)
        else:
            logging.info(
                f"set {interaction.user.name} nickname to {new_nickname}")
            try:

                await interaction.user.edit(nick=new_nickname,
                                            reason="set own nickname using bot")
            except discord.errors.Forbidden:
                logging.warning(
                    f"unable to set {interaction.user.name} nickname to {new_nickname}")
                await interaction.response.send_message(
                    f"An Error has occured while changing your Nickname. if you are not the server owner, please report this.",
                    ephemeral=True)
                return

            try:
                await interaction.user.add_roles(target_role,
                                                 reason=f"set own nickname using bot")
            except discord.errors.Forbidden:
                logging.warning(
                    f"unable to add role to {interaction.user.name}")
                await interaction.response.send_message(
                    f"An Error has occured while updating your roles. if you are not the server owner, please report this.",
                    ephemeral=True)
                return
            await interaction.response.send_message(
                f'Thanks you for setting your nickname, {interaction.user.global_name or interaction.user.name} to \"{new_nickname}\"!',
                ephemeral=True)


if __name__ == "__main__":
    token = require_env("DISCORD_BOT_TOKEN")
    client.run(token, log_level=logging.INFO)
