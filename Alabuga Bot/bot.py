import os
import sys
import discord
from discord.ext import commands, tasks
import asyncio
import json
from datetime import date, datetime
import emoji
import atexit
import random
import huggingface_hub
from gradio_client import Client
from openai import OpenAI
import logging
import requests
import math
from bs4 import BeautifulSoup
from Cipher_for_bot import cipher, uncipher


DATA_FILE = 'Files/level_data.json'
WORDS_FILE = 'Files/words.txt'
GUILD_ID = '1268823879871103006'

# Список доступных плагинов и их команды
PLUGINS = {
    "server": {
        "title": "**Команды сервера**",
        "description": "Список доступных команд:",
        "color": discord.Color.blue(),
        "commands": [
            {"type": "command", "name": "`.search_github`", "description": "Найти Статью на ГитХабе по запросу", "args": "<Запрос>"},
            {"type": "command", "name": "`.off`", "description": "Выключить бота(ТОЛЬКО ДЛЯ АДМИНИСТРАЦИИ)"},
            {"type": "command", "name": "`.restart`", "description": "Перезагрузить бота(ТОЛЬКО ДЛЯ АДМИНИСТРАЦИИ)"},
            {"type": "command", "name": "`.stat`", "description": "Посмотреть статистику пользователя", "args": "<Пользователь>(необязательно)"},
            {"type": "command", "name": "`.top`", "description": "Топ пользователей"},
            {"type": "command", "name": "`.reset_data`", "description": "Очисить статистику пользователя", "args": "<Пользователь>"}
        ]
    },
    "ai": {
        "title": "**ИИ**",
        "description": "Список команд ИИ",
        "color": discord.Color.green(),
        "commands": [
            {"type": "command", "name": "`.? <Запрос>`", "description": "Отправить запрос ИИ(Улучшенная версия)"},
            {"type": "command", "name": "`.ai <Запрос>`", "description": "Пробная версия ИИ(Намного хуче чем улучшенная версия)"},
            {"type": "command", "name": "`.img <Промпт>`", "description": "Сгенерировать изображение(Промпт вводить на английском языке)"},
            {"type": "command", "name": "`.add_key <Ключ AI/ML API>`", "description": "Получить доступ к Улучшенной версии ИИ(В ЛС с ботом)", "args": "<Ключ AI/ML Api>"},
            {"type": "text", "text": "`\nНе используйте много запросов к улучшенной верси ИИ, на одного человека рассчитано +- 5 запросов в день(если длинных), коротких больше.`"}
        ]
    }
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
            print('Данные Загружены!')
    else:
        return {}

def save_level_data():
    with open(DATA_FILE, "w") as f:
        json.dump(level_data, f, indent=4)

def load_banned_words():
    if os.path.exists(WORDS_FILE):
        with open(WORDS_FILE, 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip()]
            print('Плохие слова загружены!')
    else:
        return []

def save_data_on_exit():
    save_level_data()

atexit.register(save_data_on_exit)
level_data = load_data()
forbidden_words = load_banned_words()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)
bot.remove_command('help')
logging.basicConfig(level=logging.INFO)
huggingface_hub.login(token='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')
gh = Client("Jadssss/AIbot")
imagine = Client("mukaist/Midjourney")

user_pairs = {}

previous_requests = []
key = None

def load_keys():
    try:
        if os.path.exists('Files/keys.txt'):
            with open('Files/keys.txt', 'r') as f:
                return [line.strip() for line in f]
        else:
            return []
    except Exception as e:
        print(f"Ошибка при загрузке ключей: {e}")
        return []

keys_list = load_keys()

def save_user_history(user_id, history):
    """Сохранение истории запросов пользователя"""
    file_path = f"Player Data/{user_id}.json"
    with open(file_path, "w") as file:
        json.dump(history, file)

@bot.event
async def on_ready():
    print(f'Бот подключился к Дискорду как {bot.user} - {bot.user.id}')
    with open(f"Logs {date.today().isoformat()}.txt", "a", encoding="utf-8") as f:
        f.write(f"<===######   БОТ ЗАПУСТИЛСЯ   ######===>\n<===######   {datetime.now()}   ######===>\n")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=".help"))

ROLE_NAME = "GPT"

@bot.event
async def on_member_join(member):
    # Отправляем личное сообщение пользователю
    try:
        embed = discord.Embed(title='Добро пожаловать!', description='Это описание', color=discord.Color.green())
        embed.add_field(name='Привествуем тебя на нашем сервере!', value='Спасибо, что решил к нам присоедениться', inline=False)
        embed.add_field(name='Пожалуйста, прочитай правила данного сервера', value='Чтобы не случалось плохих инцидентов', inline=True)
        embed.add_field(name='Также просим:', value='Измени свой никнейм на твое реальное имя, чтобы с тобой Было удобно взаимодействовать!', inline=False)
        embed.add_field(name='Спасибо большое', value='И приятного времени припровождения!', inline=False)
        await member.send(embed=embed)
    except discord.Forbidden:
        print(f'Не удалось отправить сообщение пользователю {member.mention}')
    with open(f"Logs_{datetime.date.today().isoformat()}.txt", "a", encoding="utf-8") as f:
        f.write(f"Пользователь  {member.mention} присоединился к серверу.\n")


@bot.command(name='?') 
async def ask(ctx, *, request):

    global keys_list
    max_tries = 14
    retry_delay = 5 

    for i in range(max_tries): # Цикл для перебора ключей 
        if not keys_list: 
            await ctx.reply(embed=discord.Embed(title='Ошибка', description='Извините, ключи для использования закончились, возвращайтесь завтра.', color=discord.Color.red()))
            return 

        key = keys_list.pop(0) # Берем ключ 
        try:
            client = OpenAI(api_key=key, base_url="https://api.aimlapi.com/")

            previous_requests.append(request)

            messages = [
                {
                    "role": "system",
                    "content": "You are an AI assistant who knows everything and speaks Russian.",
                },
            ] + [{ "role": "user", "content": req } for req in previous_requests]

            response = client.chat.completions.create(model="gpt-4o", messages=messages)
            await ctx.defer(ephemeral=True)
            message = response.choices[0].message.content
            # Добавляем URL только если ответ получен успешно
            await ctx.reply(embed=discord.Embed(title="Assistaint", description=message, color=discord.Color.blue()))

            keys_list.append(key)  # Возвращаем ключ в список, если запрос успешен
            break 

        except Exception as e:
            print(f"Ошибка с ключом {key}: {e}")  # Логируем ошибку
            await ctx.reply(embed=discord.Embed(title='Ошибка', description='Ключ закончился.\nЗапрос повторится после замены ключа.\nИдет замена ключа...', color=discord.Color.yellow()))
            if i < max_tries - 1:
                await asyncio.sleep(retry_delay)

@bot.command(name='img', help='Generate an image using Midjourney API')
async def generate(ctx, *, prompt):
    # Отправляем начальное сообщение с одной точкой
    thinking_message = await ctx.send(f'{bot.user.name} Думает...')

    try:
        # Основная генерация изображения
        result = imagine.predict(
            prompt=prompt,
            negative_prompt="(deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime:1.4), text, close up, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, blurry, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck",
            use_negative_prompt=True,
            style="2560 x 1440",
            seed=0,
            width=1024,
            height=1024,
            guidance_scale=6,
            randomize_seed=True,
            api_name="/run"
        )

        # Получаем путь к изображению из результата
        image_path = result[0][0]['image']
        filename = os.path.basename(f"Images/{image_path}")

        # Сохраняем изображение в текущей директории"
        with open(filename, 'wb') as f:
            with open(image_path, 'rb') as img_f:
                f.write(img_f.read())

        # Редактируем сообщение, заменяя его на изображение
        await thinking_message.edit(content=None, attachments=[discord.File(filename)])

        # Удаляем изображение после отправки
        os.remove(filename)

    except asyncio.CancelledError:
        # Игнорируем отмену,
        pass

@bot.command(name='add_key')
async def add_key(ctx, key: str):
    if len(key) != 32:
        await ctx.reply(embed=discord.Embed(title='Не правильный формат ключа!', description='Используйте **__ПРАВИЛЬНЫЙ__** ключ!', color=discord.Color.red()))
        return
    
    with open('Files/keys.txt', 'a') as f:
        f.write(key + '\n')
    
    # Получаем сервер и роль
    guild_id = 1250073805095698462  # ID сервера
    role_id = 1269935425724616797  # ID роли
    guild = bot.get_guild(guild_id)
    role = guild.get_role(role_id)
    
    # Получаем пользователя на сервере
    member = guild.get_member(ctx.author.id)
    
    # Добавляем роль пользователю
    if member:
        await member.add_roles(role)
        level_data[str(member.id)]["role"] = [role.name for role in member.roles]
    
    await ctx.reply(embed=discord.Embed(title=f'Ключ добавлен успешно!', description=f'API: `{key}`\nРоль на сервере Выдана!', color=discord.Color.green()))
    await ctx.message.delete()


@bot.command(name='ai')
async def ai(ctx, *, request):
    try:
        result = gh.predict(
            message=request,
            system_message="Ты персональный ИИ помощник который знает ВСЁ! и Разговаривает на русском языке.",
            max_tokens=512,
            temperature=0.5,
            top_p=0.95
        )
        await ctx.reply(embed=discord.Embed(
            title="Assistaint",
            description=f'{result}',
            color=discord.Color.blue()
        ))

    except Exception as error:
        print(f"ошибка: {error}")

@bot.command()
async def search_github(ctx, *, query: str):
    url = f"https://api.github.com/search/repositories?q={query}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('items', [])
        
        if results:
            reply = "Найденные репозитории:\n"
            for repo in results[:5]:  # Ограничим вывод до 5 результатов
                repo_name = repo['name']
                repo_url = repo['html_url']
                reply += f"{repo_name}: {repo_url}\n"
        else:
            reply = "К сожалению, по вашему запросу ничего не найдено."
    else:
        reply = "Произошла ошибка при поиске. Попробуйте позже."

    await ctx.reply(embed=discord.Embed(title=reply, description='5 Первых репозиториев', color=discord.Color.dark_gray()))

@bot.command()
async def off(ctx):
    ctx.reply('Бот выключается...')
    exit()

@bot.command(name='restart')
@commands.has_guild_permissions(administrator=True)
async def restart(ctx):
    await ctx.reply(embed=discord.Embed(title="Перезапуск", description="Бот перезапускается...", color=0xffa500))
    os.execv(sys.executable, ['python'] + sys.argv)

# Логирование сообщений
@bot.event
async def on_message(message):
    if message.guild is None and message.author != bot.user:
        if message.author.id in user_pairs and user_pairs[message.author.id] is not None:
            if message.content.startswith(bot.command_prefix):
                # Обработка команды
                await bot.process_commands(message)
                return
            crypted_message=cipher(message)
            partner_id = user_pairs[message.author.id]
            partner_member = bot.get_user(partner_id)
            if partner_member:
                uncipher_message=message
                await partner_member.send(embed=discord.Embed(title=message.author.name, description=uncipher_message, color=discord.Color.green()))
        else:
            await message.author.send("Вы не подключены к собеседнику. Отправьте /connect, чтобы найти собеседника.")
    else:
        member = message.guild.get_member(message.author.id)
        # Update the role data
        if str(member.id) in level_data:
            level_data[str(member.id)]["role"] = [role.name for role in member.roles]

        # Проверка и обновление данных пользователя
        if str(message.author.id) not in level_data:
            level_data[str(message.author.id)] = {
                "role": [role.name for role in message.author.roles],
                "joined_at": str(message.author.joined_at),
                "last_message_at": str(datetime.now()),
                "messages": 0,
                "characters": 0,
                "forwarded": 0,
                "emojis": 0,
                "swear_messages": 0,
                "level": 0
            }

        level_data[str(message.author.id)]["messages"] += 1
        level_data[str(message.author.id)]["characters"] += len(message.content)
        level_data[str(message.author.id)]["emojis"] += emoji.emoji_count(message.content)
        level_data[str(message.author.id)]["last_message_at"] = str(datetime.now())

        if any(word in message.content.lower() for word in forbidden_words):
            level_data[str(message.author.id)]["swear_messages"] += 1
            print(f"[{datetime.now()}] ({message.channel}) [МАТ] {message.author} > {message.content}")
        else:
            print(f"[{datetime.now()}] ({message.channel}) [CHAT] {message.author} > {message.content}")

        # Save message log to file
        with open(f"Logs {date.today().isoformat()}.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] ({message.channel}) {message.author} > {message.content}\n")

        # Проверка и повышение уровня
        if level_data[str(message.author.id)]["messages"] % 100 == 0:
            level_data[str(message.author.id)]["level"] += 1
            await message.channel.send(embed=discord.Embed(
                title="Новый уровень!",
                description=f"{message.author.mention}, теперь у тебя уровень: {level_data[str(message.author.id)]['level']}!",
                color=0x00ff00
            ))

        save_level_data()
        await bot.process_commands(message)

@bot.command(name='stat')
async def stat(ctx, member: discord.Member = None):
    member = member or ctx.author
    if str(member.id) in level_data:
        level_info = level_data[str(member.id)]
        char_count = level_info['characters']
        char_display = f"{char_count / 1000:.1f}K" if char_count >= 1000 else str(char_count)

        await ctx.reply(embed=discord.Embed(
            title=f"Статистика {member}",
            description=(
                f"Роль: {', '.join(level_info['role'])}\n"
                f"В чате с: {level_info['joined_at']}\n"
                f"Последнее сообщение: {level_info['last_message_at']}\n"
                f"Сообщений: {level_info['messages']}\n"
                f"Символов: {char_display}\n"
                f"Пересланных: {level_info['forwarded']}\n"
                f"Смайлов: {level_info['emojis']}\n"
                f"Сообщений с матом: {level_info['swear_messages']}\n"
                f"Уровень: {level_info['level']}"
            ),
            color=0x0000ff
        ))
    else:
        await ctx.reply(embed=discord.Embed(title="Ошибка", description="Нет данных о пользователе.", color=0xff0000))

@bot.command(name='top')
async def top(ctx, page: int = 1):
    # Фильтрация записей без необходимых ключей и сортировка
    sorted_data = sorted(
        [(user_id, data) for user_id, data in level_data.items() if 'level' in data and 'messages' in data],
        key=lambda x: (x[1]['level'], x[1]['messages']),
        reverse=True
    )

    # Определение количества страниц
    pages = math.ceil(len(sorted_data) / 10)

    # Проверка страницы
    if page < 1 or page > pages:
        await ctx.reply(embed=discord.Embed(title="Ошибка", description="Неправильная страница", color=0xff0000))
        return

    # Формирование списка для отображения
    leaderboard = ""
    for rank, (user_id, data) in enumerate(sorted_data[(page - 1) * 10:page * 10], (page - 1) * 10 + 1):
        user = await bot.fetch_user(int(user_id))
        if user is not None:
            leaderboard += f"{rank}. @{user.name} - Уровень: {data['level']}, Сообщений: {data['messages']}\n"
        else:
            leaderboard += f"{rank}. Неизвестный пользователь (ID: {user_id}) - Уровень: {data['level']}, Сообщений: {data['messages']}\n"

    # Отправка сообщения с рейтингом
    embed = discord.Embed(
        title=f"Топ пользователей (Страница {page}/{pages})",
        description=leaderboard,
        color=0x00ff00
    )
    await ctx.reply(embed=embed)

@bot.command(name='reset_data')
async def reset_data(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    if str(member.id) in level_data:
        level_data[str(member.id)] = {
            "role": [role.name for role in member.roles],
            "joined_at": str(member.joined_at),
            "last_message_at": str(datetime.now()),
            "warnings": 0,
            "messages": 0,
            "characters": 0,
            "forwarded": 0,
            "photos": 0,
            "commands": 0,
            "emojis": 0,
            "swear_messages": 0,
            "level": 0
        }
        save_level_data()
        await ctx.reply(embed=discord.Embed(title="Данные сброшены", description=f"Данные о пользователе {member.mention} были сброшены.", color=0x00ff00))
    else:
        await ctx.reply(embed=discord.Embed(title="Ошибка", description=f"Нет данных о пользователе {member.mention}.", color=0xff0000))

# Команда для вывода help
@bot.command(name='help')
async def help(ctx, vibor: str = ''):
    if vibor in PLUGINS:
        plugin = PLUGINS[vibor]
        help_embed = discord.Embed(
            title=plugin["title"],
            description=plugin["description"],
            color=plugin["color"]
        )
        for command in plugin["commands"]:
            if command["type"] == "command":
                help_embed.add_field(name=command["name"], value=command["description"], inline=False)
            elif command["type"] == "text":
                help_embed.description += f"{command['text']}\n\n"
        await ctx.reply(embed=help_embed)

    elif vibor == '':
        net_vibora = discord.Embed(title="**Выберите категорию:**", color=discord.Color.blue())
        for plugin_name in PLUGINS:
            net_vibora.add_field(
                name=f"`{plugin_name}`",
                value=f"Использование: `.help {plugin_name}`\nОтправляет команды для {plugin_name}",
                inline=False
            )
        await ctx.reply(embed=net_vibora)

    else:
        no_kat = discord.Embed(title="**Неизвестная категория!**", description='Используйте `.help` для просмотра всех категорий', color=discord.Color.red())
        await ctx.reply(embed=no_kat)


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
                await partner_member.send("Вы подключились! Поздоровайтесь.\nОтправь /disconnect чтоб отключиться.")
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

# Запуск бота
bot.run('MTI1NDgxNjMzNDg4MjE0NDM1Nw.GpfW-l.f5v_YxLAtafIw9LjeKE6TYlrsx2pebr5zSUT9s')