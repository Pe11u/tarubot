import discord # type: ignore
from discord.ext import commands, tasks # type: ignore
from discord.ui import Button, Select, View # type: ignore
from discord import FFmpegPCMAudio # type: ignore
from datetime import timedelta
import re
import os
import moviepy.editor as mp # type: ignore
from moviepy.editor import VideoFileClip, ImageClip # type: ignore
import random
import time
from datetime import timedelta
import requests # type: ignore
from urllib.parse import quote
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='t?', intents=intents)

converting_tasks = []

polls = {}

bot.remove_command('help')

async def update_ping():
    while True:
        latency = bot.latency * 1000
        count = len(bot.guilds)
        activity = discord.Game(name=f"{count} Servers｜Ping: {int(latency)}ms")
        await bot.change_presence(activity=activity)
        await asyncio.sleep(15)

@bot.event
async def on_ready():
    bot.loop.create_task(update_ping())

class HelpSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="管理", description="管理に関連するコマンド", emoji="⚙️"),
            discord.SelectOption(label="情報", description="情報に関連するコマンド", emoji="ℹ️"),
            discord.SelectOption(label="技術", description="技術的なコマンド", emoji="🛠"),
            discord.SelectOption(label="その他", description="その他のコマンド", emoji="📝")
        ]
        super().__init__(placeholder="カテゴリを選択", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embed = discord.Embed(title=f"{category} コマンド", color=discord.Color.blue())

        if category == "管理":
            embed.add_field(name="t?kick [メンション]", value="メンバーをキックします。", inline=False)
            embed.add_field(name="t?ban [メンション]", value="メンバーをBANします。", inline=False)
            embed.add_field(name="t?unban [ユーザー名]", value="ユーザーのBANを解除します。", inline=False)
            embed.add_field(name="t?timeout [メンション] [時間]", value="メンバーを指定時間タイムアウトします。", inline=False)
            embed.add_field(name="t?untimeout [メンション]", value="メンバーのタイムアウトを解除します。", inline=False)
            embed.add_field(name="t?clear [数] [メンション(任意)]", value="指定されたユーザーのメッセージを削除します。", inline=False)
        elif category == "情報":
            embed.add_field(name="t?info [メンション(任意)]", value="指定されたユーザーの情報を表示します。", inline=False)
            embed.add_field(name="t?ping", value="BotのPing値を表示します。", inline=False)
            embed.add_field(name="t?banlist", value="現在BANされているユーザーのリストを表示します。", inline=False)
        elif category == "技術":
            embed.add_field(name="t?gif [FPS(任意)]", value="返信元のメディアをGIFに変換します。", inline=False)
            embed.add_field(name="t?say ['メッセージ']", value="メッセージをそのままボットとして送信します。", inline=False)
            embed.add_field(name="t?intent ['タイトル'] ['メッセージ'] [色(任意)]", value="メッセージをそのままボットとして送信します。", inline=False)
            embed.add_field(name="t?iplocate [IPアドレス]", value="指定されたIPv4/v6アドレスの情報を表示します。", inline=False)
        elif category == "その他":
            embed.add_field(name="t?help", value="コマンドの使い方を表示します。", inline=False)
            embed.add_field(name="t?dice [(回す回数)d(乱数範囲)] [int/float(任意)]", value="サイコロを回します。", inline=False)

        await interaction.response.edit_message(embed=embed)

class HelpView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpSelect())

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(title="エラー", description="コマンドを実行できませんでした。\n権限があるかどうかを確認してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="エラー", description=f"'{ctx.invoked_with}' というコマンドはありません。\n**t?help**コマンドで確認してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="エラー", description=f"コマンドに必要な引数が足りません。\n**t?help**コマンドで確認してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="エラー", description="引数の形式が不正です。\n**t?help**コマンドで確認してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(title="エラー", description="このボットに必要な権限がありません。\n権限を確認してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, discord.Forbidden):
        embed = discord.Embed(title="エラー", description="ボット参加時に必要な権限が許可されていません。\nもう一度入れなおしてください。", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingAnyRole):
        embed = discord.Embed(title="エラー", description="このコマンドを実行するには最高権限が必要です。", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title="エラー", description=f"{ctx.command}コマンドを実行しようとしたため、失敗しました。\nボットの権限より高い権限を持つユーザーには実行できません。", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        if '隼佑' not in {str(error)} and 'MTMyNzQ5MjM3ODQyMDA1MjAxOA' not in {str(error)}:
            embed = discord.Embed(title="エラー", description=f"コマンドの実行中にエラーが発生しました。\nエラー詳細: {str(error)}", color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="エラー", description=f"コマンドの実行中にエラーが発生しました。", color=discord.Color.red())
            await ctx.send(embed=embed)

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        embed = discord.Embed(title="エラー", description="自分自身をキックすることはできません。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(title="成功", description=f'{member.mention} をキックしました。理由: {reason}', color=discord.Color.green())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="エラー", description=f"キック中にエラーが発生しました。\nエラー詳細: {str(e)}", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        embed = discord.Embed(title="エラー", description="自分自身をBANすることはできません。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(title="成功", description=f'{member.mention} をBANしました。理由: {reason}', color=discord.Color.green())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="エラー", description=f"BAN中にエラーが発生しました。\nエラー詳細: {str(e)}", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name):
    try:
        async for ban_entry in ctx.guild.bans():
            user = ban_entry.user
            if user.name == member_name:
                await ctx.guild.unban(user)
                embed = discord.Embed(title="成功", description=f'{user.name} のBANを解除しました。', color=discord.Color.green())
                await ctx.send(embed=embed)
                return
        
        embed = discord.Embed(title="エラー", description=f'{member_name} はBANされていません。', color=discord.Color.red())
        await ctx.send(embed=embed)
    
    except Exception as e:
        embed = discord.Embed(title="エラー", description=f"BAN解除中にエラーが発生しました。\nエラー詳細: {str(e)}", color=discord.Color.red())
        await ctx.send(embed=embed)


@bot.command(name='timeout')
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration: str, *, reason=None):
    if member == ctx.author:
        embed = discord.Embed(title="エラー", description="自分自身をタイムアウトすることはできません。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    try:
        time_regex = re.compile(r'((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?')
        match = time_regex.fullmatch(duration)
        if not match:
            embed = discord.Embed(title="エラー", description="時間形式が無効です。例: 1d3h", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        time_params = {k: int(v) for k, v in match.groupdict(default=0).items()}
        delta = timedelta(**time_params)
        await member.timeout_for(delta)
        embed = discord.Embed(title="成功", description=f'{member.mention} を {duration} の間、タイムアウトしました。理由: {reason}', color=discord.Color.green())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="エラー", description=f"タイムアウト中にエラーが発生しました。\nエラー詳細: {str(e)}", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='untimeout')
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    if member == ctx.author:
        embed = discord.Embed(title="エラー", description="自分自身のタイムアウトは解除できません。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    try:
        await member.timeout(None)
        embed = discord.Embed(title="成功", description=f'{member.mention} のタイムアウトを解除しました。', color=discord.Color.green())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="エラー", description=f"タイムアウト解除中にエラーが発生しました。\nエラー詳細: {str(e)}", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='info')
async def info(ctx, *, user: discord.Member = None):
    if user is None:
        user = ctx.author

    if user.banner:
        banner_color = discord.Color(int(user.banner_url.split("/")[-1].split("_")[-1], 16))

    embed = discord.Embed(title=f"{user.name} の情報", color=discord.Color.green())
    
    embed.set_thumbnail(url=user.avatar.url)

    embed.add_field(name="名前", value=user.name, inline=True)
    embed.add_field(name="種類", value="ボット" if user.bot else "ユーザー", inline=True)
    embed.add_field(name="Discord参加日", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="サーバー参加日", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S") if user.joined_at else "**不明**", inline=True)
    embed.add_field(name="ユーザーID", value=user.id, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    try:
        ping_value = round(bot.latency * 1000)
        embed = discord.Embed(title="Pong!", description=f"{ping_value}ms", color=discord.Color.green())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(title="エラー", description=f"Ping中にエラーが発生しました。\nエラー詳細: {str(e)}", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, number: int, *, user: discord.Member = None):
    if number < 1 or number > 9999:
        embed = discord.Embed(title="エラー", description="削除するメッセージの数は1から9999の範囲で指定してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    if user:
        deleted = 0
        async for message in ctx.channel.history(limit=9999):
            if message.author == user:
                await message.delete()
                deleted += 1
                if deleted >= number:
                    break

        embed = discord.Embed(title="成功", description=f'{user.mention} の {deleted} 件のメッセージを削除しました。', color=discord.Color.green())
        await ctx.send(embed=embed, delete_after=5)

    else:
        deleted = await ctx.channel.purge(limit=number)
        embed = discord.Embed(title="成功", description=f'{len(deleted)} 件のメッセージを削除しました。', color=discord.Color.green())
        await ctx.send(embed=embed, delete_after=5)

@bot.command(name='gif')
async def gif(ctx, fps: int = 10):
    global converting_tasks
    if len(converting_tasks) >= 5:
        await ctx.send(embed=discord.Embed(title="エラー", description="現在、5つの変換が進行中です。後ほどお試しください。", color=discord.Color.red()))
        return

    if not ctx.message.reference:
        await ctx.send(embed=discord.Embed(title="エラー", description="返信先のメディアを指定してください。", color=discord.Color.red()))
        return

    replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    if not replied_message.attachments:
        await ctx.send(embed=discord.Embed(title="エラー", description="メディアが見つかりません。", color=discord.Color.red()))
        return

    attachment = replied_message.attachments[0]
    ext = attachment.filename.split(".")[-1].lower()

    if ext not in ["mp4", "mov", "avi", "png", "jpg", "jpeg"]:
        await ctx.send(embed=discord.Embed(title="エラー", description="対応していないファイル形式です。", color=discord.Color.red()))
        return

    if fps < 1 or fps > 33:
        await ctx.send(embed=discord.Embed(title="エラー", description="FPSは1から33の範囲で指定してください。", color=discord.Color.red()))
        return

    converting_message = await ctx.send(embed=discord.Embed(title="変換中", description="GIFへの変換を行っています。しばらくお待ちください...", color=discord.Color.blue()))
    converting_tasks.append(ctx.author.id)

    try:
        file_path = f"temp_{int(time.time())}.{ext}"
        await attachment.save(file_path)
        gif_path = file_path.rsplit('.', 1)[0] + ".gif"

        if ext in ["mp4", "mov", "avi"]:
            clip = VideoFileClip(file_path)
            if clip.duration > 60:
                raise ValueError("動画の長さが60秒を超えています。")
            clip.write_gif(gif_path, fps=fps)
        else:
            clip = ImageClip(file_path)
            clip.set_duration(2).write_gif(gif_path, fps=24)

        await converting_message.edit(embed=discord.Embed(title="完了", description="GIF変換が完了しました！", color=discord.Color.green()))
        await ctx.send(file=discord.File(gif_path))
    except ValueError as e:
        await converting_message.edit(embed=discord.Embed(title="エラー", description=str(e), color=discord.Color.red()))
    except Exception as e:
        await converting_message.edit(embed=discord.Embed(title="エラー", description=f"エラーが発生しました: {str(e)}", color=discord.Color.red()))
    finally:
        os.remove(file_path)
        if os.path.exists(gif_path):
            os.remove(gif_path)
        converting_tasks.remove(ctx.author.id)

@bot.command()
async def dice(ctx, dice: str, value_type: str = 'int'):
    try:
        parts = dice.lower().split("d")
        if len(parts) != 2:
            raise ValueError("無効な入力です。構文は [回数]d[範囲] です。")
        
        rolls = int(parts[0])
        sides = int(parts[1])
        
        if rolls > 100:
            raise ValueError("回数は最大100回までです。")
        if sides > 99999:
            raise ValueError("範囲は最大99999までです。")
        
        results = []
        total = 0
        for _ in range(rolls):
            if value_type == 'int':
                roll_result = random.randint(0, sides)
            elif value_type == 'float':
                roll_result = random.uniform(0, sides)
                roll_result = round(roll_result, 5)

            results.append(roll_result)
            total += roll_result
        
        if rolls == 1:
            result_display = str(results[0])
        else:
            results_str = " + ".join(map(str, results))
            if value_type == 'int':
                result_display = f"{results_str} = {total}"
            else:
                result_display = f"{results_str} = {total:.5f}"

        embed = discord.Embed(title="サイコロの結果", description=result_display, color=discord.Color.green())
        await ctx.send(embed=embed)

    except ValueError as e:
        embed = discord.Embed(title="エラー", description=str(e), color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='say')
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)

@bot.command(name='intent')
@commands.has_permissions(manage_messages=True)
async def intent(ctx, title: str, content: str, color: str = "green"):
    await ctx.message.delete()
    
    embed_color = discord.Color.green()

    try:
        if color.startswith('#'):
            color_code = int(color.lstrip('#'), 16)
            embed_color = discord.Color(color_code)
        else:
            embed_color = getattr(discord.Color, color.lower())()
    except (ValueError, AttributeError):
        embed = discord.Embed(title="エラー", description="無効な色の指定です。色は16進数（#ff5733）か、'blue' や 'red' などの名前を使用してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title=title, description=content, color=embed_color)
    await ctx.send(embed=embed)

def parse_color(color_str: str):
    try:
        if color_str.startswith("#"):  # 16進数の場合
            return discord.Color(int(color_str[1:], 16))
        else:  # 色名の場合
            return getattr(discord.Color, color_str.lower())()
    except AttributeError:
        return discord.Color.green()

@bot.command(name='poll')
async def poll(ctx, action: str, *args):
    if action == "create":
        if len(args) < 2:
            embed = discord.Embed(title="エラー", description="タイトルと色、選択肢を指定してください。", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        title = args[0]
        
        if len(args) > 2 and (args[1].startswith("#") or args[1].lower() in ["red", "green", "blue", "yellow", "purple", "pink"]):
            color = parse_color(args[1])
            options = list(args[2:])
        else:
            color = discord.Color.green()
            options = list(args[1:])
        
        if len(options) < 1:
            embed = discord.Embed(title="エラー", description="少なくとも1つの選択肢を指定してください。", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        if len(options) > 15:
            embed = discord.Embed(title="エラー", description="選択肢は最大15までです。", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(title=title, color=color)
        embed.add_field(name="選択肢", value="\n".join([f"{i + 1}. {option}" for i, option in enumerate(options)]))

        poll_message = await ctx.send(embed=embed)
        
        polls[title] = {
            "message": poll_message,
            "options": options,
            "votes": {option: 0 for option in options},
            "voted_users": set()
        }
        
        for i in range(len(options)):
            await poll_message.add_reaction(chr(127462 + i))

        await ctx.message.delete()

    elif action == "done":
        title = args[0]
        if title not in polls:
            embed = discord.Embed(title="エラー", description="そのタイトルの投票は存在しません。", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        poll = polls[title]
        embed = discord.Embed(title=f"{title} の投票結果", color=poll["message"].embeds[0].color)
        result = "\n".join([f"{option}: {poll['votes'][option]}票" for option in poll["options"]])
        embed.add_field(name="結果", value=result)

        await ctx.send(embed=embed)

        poll["message"].disable_mention()
        poll["message"].clear_reactions()
        await poll["message"].edit(embed=embed)

        await ctx.message.delete()

    elif action == "remove":
        if len(args) < 2:
            embed = discord.Embed(title="エラー", description="タイトルと削除する選択肢を指定してください。", color=discord.Color.red())
            await ctx.send(embed=embed)
            return
        
        title = args[0]
        option_to_remove = args[1]

        if title not in polls:
            embed = discord.Embed(title="エラー", description="そのタイトルの投票は存在しません。", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        poll = polls[title]
        if option_to_remove not in poll["options"]:
            embed = discord.Embed(title="エラー", description=f"選択肢「{option_to_remove}」は存在しません。", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        poll["options"].remove(option_to_remove)
        poll["votes"].pop(option_to_remove, None)

        embed = discord.Embed(title=title, color=poll["message"].embeds[0].color)
        embed.add_field(name="選択肢", value="\n".join([f"{i + 1}. {option}" for i, option in enumerate(poll["options"])]))
        await poll["message"].edit(embed=embed)

        await poll["message"].clear_reactions()

        for i in range(len(poll["options"])):
            await poll["message"].add_reaction(chr(127462 + i))  # A, B, C, ...

        await ctx.message.delete()

    else:
        embed = discord.Embed(title="エラー", description="無効なアクションです。`create`, `add`, `done`, `remove` のいずれかを指定してください。", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    for title, poll in polls.items():
        if reaction.message.id == poll["message"].id and user not in poll["voted_users"]:
            option_index = ord(reaction.emoji) - 127462
            if 0 <= option_index < len(poll["options"]):
                option = poll["options"][option_index]
                poll["votes"][option] += 1
                poll["voted_users"].add(user)

                embed = discord.Embed(title=title, color=poll["message"].embeds[0].color)
                embed.add_field(name="選択肢", value="\n".join([f"{i + 1}. {option}: {poll['votes'][option]}票" for i, option in enumerate(poll["options"])]))
                await reaction.message.edit(embed=embed)

@bot.command(name='banlist')
async def banlist(ctx):
    banned_users = []
    
    async for ban_entry in ctx.guild.bans():
        banned_users.append(ban_entry.user)
    
    if not banned_users:
        embed = discord.Embed(title="現在BANされているユーザーは居ません。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title="BANされたユーザー一覧", color=discord.Color.black())

    for user in banned_users:
        embed.add_field(name=user.name, value=f"ID: {user.id}", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def iplocate(ctx, ip: str):
    def is_ipv4(ip):
        return bool(re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", ip))

    def is_ipv6(ip):
        return bool(re.match(r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$", ip))

    def get_ip_info(ip):
        try:
            response = requests.get(f'https://ipinfo.io/{ip}/json')
            return response.json()
        except requests.exceptions.RequestException:
            return None

    if not (is_ipv4(ip) or is_ipv6(ip)):
        embed = discord.Embed(title="エラー", description="無効なIPアドレス形式です。IPv4またはIPv6を指定してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    if ip.startswith("192."):
        embed = discord.Embed(title="エラー", description="ローカルIPアドレスから情報を取得することはできません。\nグローバルIPアドレスを入力してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    ip_info = get_ip_info(ip)
    
    if ip_info is None:
        embed = discord.Embed(title="エラー", description="IP情報を取得できませんでした。もう一度試してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(title="IP情報", color=discord.Color.blue())
    embed.add_field(name="IPアドレス", value=ip, inline=False)

    embed.add_field(name="都市", value=ip_info.get('city', '不明'), inline=True)
    embed.add_field(name="地域", value=ip_info.get('region', '不明'), inline=True)
    embed.add_field(name="国", value=ip_info.get('country', '不明'), inline=True)
    embed.add_field(name="組織", value=ip_info.get('org', '不明'), inline=True)
    embed.add_field(name="位置", value=ip_info.get('loc', '不明'), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(title="ヘルプ", description="カテゴリを選択してください", color=discord.Color.blue())
    
    initial_embed = discord.Embed(title="管理 コマンド", color=discord.Color.blue())
    initial_embed.add_field(name="t?kick [メンション]", value="メンバーをキックします。", inline=False)
    initial_embed.add_field(name="t?ban [メンション]", value="メンバーをBANします。", inline=False)
    initial_embed.add_field(name="t?unban [ユーザー名]", value="ユーザーのBANを解除します。", inline=False)
    initial_embed.add_field(name="t?timeout [メンション] [時間]", value="メンバーを指定時間タイムアウトします。", inline=False)
    initial_embed.add_field(name="t?untimeout [メンション]", value="メンバーのタイムアウトを解除します。", inline=False)
    initial_embed.add_field(name="t?clear [数] [メンション(任意)]", value="指定された数のメッセージを削除します。", inline=False)

    view = HelpView()
    
    await ctx.send(embed=initial_embed, view=view)

bot.run('MTMyNzQ5MjM3ODQyMDA1MjAxOA.GTa0fM.oHtxXh5E2MSapodxUF5szT8W4EpeBiWzMHvnu0')