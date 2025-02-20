import discord
from discord.ext import commands
import asyncio

# Bot prefix and permissions
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Event when bot is ready
@bot.event
async def on_ready():
    print(f'Bot {bot.user} is now online!')

# Warn command
@bot.command()
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.send(f'You have been warned! Reason: {reason}')
    await ctx.send(f'{member.mention} has been warned!')

# Ban command
@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned from the server!')

# Kick command
@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked from the server!')

# Clear messages command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'{amount} messages have been deleted!', delete_after=3)

# Mute command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: int):
    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f'{member.mention} has been muted for {duration} seconds!')
    await asyncio.sleep(duration)
    await member.remove_roles(role)
    await ctx.send(f'{member.mention} is now unmuted!')

# Unmute command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f'{member.mention} has been unmuted!')
    else:
        await ctx.send(f'{member.mention} is not muted!')

# Slowmode command
@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f'Slowmode has been set to {seconds} seconds!')

# Server info command
@bot.command()
async def server(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=guild.name, description='Server Info', color=discord.Color.blue())
    embed.add_field(name='Member Count', value=guild.member_count)
    embed.add_field(name='Total Channels', value=len(guild.channels))
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

# Add role command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f'{role.name} has been assigned to {member.mention}!')

# Remove role command
@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f'{role.name} has been removed from {member.mention}!')

# AFK System
afk_users = {}

@bot.command()
async def afk(ctx, *, reason="AFK"):
    afk_users[ctx.author.id] = reason
    await ctx.send(f'{ctx.author.mention} is now AFK: {reason}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check AFK users
    if message.author.id in afk_users:
        del afk_users[message.author.id]
        await message.channel.send(f'Welcome back {message.author.mention}, you are no longer AFK!')

    for mention in message.mentions:
        if mention.id in afk_users:
            await message.channel.send(f'{mention.mention} is AFK: {afk_users[mention.id]}')

    # Prevent excessive caps lock spam
    if message.content.isupper() and len(message.content) > 5:
        await message.delete()
        await message.channel.send(f'{message.author.mention}, please do not use excessive caps!')

    await bot.process_commands(message)

# Welcome & goodbye messages
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f'Welcome {member.mention} to {member.guild.name}!')

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name='general')
    if channel:
        await channel.send(f'{member.mention} has left the server. Goodbye!')

# Commands list
@bot.command()
async def commands_list(ctx):
    commands_text = """
    **Moderation Commands:**
    - `!warn @user [reason]` → Sends a warning message to the user.
    - `!ban @user [reason]` → Bans the user from the server.
    - `!kick @user [reason]` → Kicks the user from the server.
    - `!clear [number]` → Deletes the specified number of messages.
    - `!mute @user [duration]` → Mutes the user for a specified duration.
    - `!unmute @user` → Unmutes the specified user.
    - `!slowmode [seconds]` → Sets slowmode for the channel.
    - `!server` → Displays server information.
    - `!addrole @user [role]` → Assigns a role to a user.
    - `!removerole @user [role]` → Removes a role from a user.
    - `!afk [reason]` → Marks a user as AFK.
    """
    await ctx.send(commands_text)

# Run the bot (INSERT YOUR TOKEN HERE)
bot.run("Your_Discord_API_Token")
