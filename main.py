import discord
from discord.ext import commands, tasks
from discord import app_commands
import logging
from dotenv import load_dotenv
from keepalive import keep_alive
import os

keep_alive()
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
guild_id = 1381356363107794954
guild_obj = discord.Object(id=guild_id)

secret_role = 'Mayor'

@bot.event
async def on_ready():
    await bot.tree.sync(guild=guild_obj)
    print(f"Synced slash commands to {guild_id}.")
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}!")
    # Log to a channel if needed

@bot.event
async def on_member_remove(member):
    # Log to a channel if needed
    print(f"{member.name} has left the server.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - don't use that word!")

    await bot.process_commands(message)

@bot.tree.command(name="hello", description="Say hello!", guild=guild_obj)
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.mention}!")

@bot.tree.command(name="poll", description="Create a simple yes/no poll.", guild=guild_obj)
@app_commands.describe(question="The poll question")
async def poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="New Poll", description=question)
    poll_msg = await interaction.channel.send(embed=embed)
    await poll_msg.add_reaction("👍")
    await poll_msg.add_reaction("👎")
    await interaction.response.send_message("Poll created!", ephemeral=True)

    # Auto-delete poll after 2 minutes (optional)
    async def delete_later():
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(minutes=2))
        await poll_msg.delete()
    bot.loop.create_task(delete_later())

@bot.tree.command(name="assign", description="Assign yourself the secret role.", guild=guild_obj)
async def assign(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name=secret_role)
    if role:
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"{interaction.user.mention} is now assigned to {secret_role}.")
    else:
        await interaction.response.send_message("Role does not exist!")

@bot.tree.command(name="remove", description="Remove the secret role from yourself.", guild=guild_obj)
async def remove(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name=secret_role)
    if role:
        await interaction.user.remove_roles(role)
        await interaction.response.send_message(f"{interaction.user.mention} has had {secret_role} removed.")
    else:
        await interaction.response.send_message("Role does not exist!")

@bot.tree.command(name="dm", description="Send yourself a DM.", guild=guild_obj)
@app_commands.describe(msg="The message to send")
async def dm(interaction: discord.Interaction, msg: str):
    await interaction.user.send(f"You said: {msg}")
    await interaction.response.send_message("Message sent to your DMs!", ephemeral=True)

@bot.tree.command(name="reply", description="Replies to your command message.", guild=guild_obj)
async def reply(interaction: discord.Interaction):
    await interaction.response.send_message("This is a reply to your slash command!")

@bot.tree.command(name="secret", description="Access a secret only role holders can see.", guild=guild_obj)
async def secret(interaction: discord.Interaction):
    role = discord.utils.get(interaction.user.roles, name=secret_role)
    if role:
        await interaction.response.send_message("Welcome to the club!")
    else:
        await interaction.response.send_message("You do not have permission to do that.", ephemeral=True)

@bot.tree.command(name="list_members", description="List all members with a specific role.", guild=guild_obj)
@app_commands.describe(role_name="Name of the role")
async def list_members(interaction: discord.Interaction, role_name: str):
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role:
        members = [member.mention for member in role.members]
        if members:
            await interaction.response.send_message(f"Members with {role_name}:\n" + "\n".join(members))
        else:
            await interaction.response.send_message(f"No members have the role {role_name}.")
    else:
        await interaction.response.send_message("Role not found.")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
