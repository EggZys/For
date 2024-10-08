import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='&', intents=intents)

user_pairs = {}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='start')
async def send_welcome(ctx):
    await ctx.send("Добро пожаловать в Анонимный чат! Отправьте сообщение /connect, чтобы найти собеседника для общения.")

@bot.command(name='connect')
async def connect_users(ctx):
    user_id = ctx.author.id

    if user_id in user_pairs:
        await ctx.send("Вы уже подключены. Отправь /disconnect, чтобы завершить текущий чат.")
        return

    for user in user_pairs:
        if user_pairs[user] is None:
            partner_id = user
            user_pairs[user_id] = partner_id
            user_pairs[partner_id] = user_id

            partner_member = bot.get_user(partner_id)
            if partner_member:
                await partner_member.send("Вы подключились! Поздоровайтесь. Отправь /disconnect чтоб отключиться.")
            await ctx.send("Вы подключились! Поздоровайтесь. Отправь /disconnect чтоб отключиться.")
            return

    user_pairs[user_id] = None
    await ctx.send("Ищем собеседника. Подождите...")
    await asyncio.sleep(1)

@bot.command(name='disconnect')
async def disconnect_users(ctx):
    user_id = ctx.author.id

    if user_id not in user_pairs or user_pairs[user_id] is None:
        await ctx.send("Вы ни к кому не подключены.")
        return

    partner_id = user_pairs[user_id]

    if partner_id is not None:
        partner_member = bot.get_user(partner_id)
        if partner_member:
            await partner_member.send("Ваш собеседник отключился :(\nОтправь /connect чтобы найти собеседника.")

    del user_pairs[user_id]
    if partner_id is not None:
        del user_pairs[partner_id]

    await ctx.send("Вы отключились. Отправь /connect чтобы найти собеседника.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith(bot.command_prefix):
        # Обработка команды
        await bot.process_commands(message)
        return

    user_id = message.author.id
    if user_id in user_pairs and user_pairs[user_id] is not None:
        partner_id = user_pairs[user_id]
        partner_member = bot.get_user(partner_id)
        if partner_member:
            await partner_member.send(message.content)
        else:
            await message.channel.send("Ваш собеседник вышел из Discord.")


bot.run('MTI1NDgxNjMzNDg4MjE0NDM1Nw.GpfW-l.f5v_YxLAtafIw9LjeKE6TYlrsx2pebr5zSUT9s')