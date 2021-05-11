import urllib.request
import discord
import json
import re
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

token = os.environ.get('TOKEN')

class Main():
    client = discord.Client()

    @client.event
    async def on_ready():
        print('ログインしました')

    @client.event
    async def on_message(message):
        if '/translate' in message.content:
            if message.content == '/translate-help':
                embed_help = discord.Embed(
                    title =
                      '翻訳したい内容を[]に入れてください。 \r\n' \
                      '翻訳したい言語を()に指定してください。\r\n'\
                        'Enter the content you want to translate in [].\r\n'\
                        'Specify the language you want to translate in ().',
                    color = discord.Colour.random()
                )
                await message.channel.send(embed=embed_help)

                embed_lang = discord.Embed(
                    title =
                        '以下から翻訳したい言語を指定してください。\r\n'\
                        'Specify the language you want to translate from below.',
                    description =
                        'もし言語を選択しない場合、英語で翻訳されます。\r\n'\
                        'If you don\'t specify a language, it will be translated in EN',
                    color = discord.Colour.random()
                )
                embed_lang.add_field(name="ドイツ語,(German)", value="DE")
                embed_lang.add_field(name="英語(English)", value="EN")
                embed_lang.add_field(name="イタリア語(Italian)", value="IT")
                embed_lang.add_field(name="日本語(Japanese)", value="JA")
                embed_lang.add_field(name="ルーマニア語(Romanian)", value="RO")
                embed_lang.add_field(name="ロシア語(Russian)", value="RU")
                embed_lang.add_field(name="スウェーデン語(Swedish)", value="SV")

                await message.channel.send(embed=embed_lang)

                embed_example = discord.Embed(
                    title =
                        'e.g.) 例\r\n'\
                        '/translate [Hello World](DE) \r\n'\
                        '"Hallo Welt (translated)"',
                    color = discord.Colour.random()
                )
                await message.channel.send(embed=embed_example)
            else:
                url = 'https://api-free.deepl.com/v2/translate'

                # re.findallを使用すると配列になるので[0]をつけている
                text = re.findall(r'\[(.+)\]', message.content)[0]

                target_lang = 'EN-US'
                if len(re.findall(r'\((.+)\)', message.content)) != 0:
                    target_lang = re.findall(r'\((.+)\)', message.content)[0]

                if target_lang == 'EN':
                    target_lang = 'EN-US'

                method = 'POST'
                auth_key = os.environ.get('AUTH_KEY')
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}

                data = urllib.parse.urlencode({
                    'auth_key': auth_key,
                    'text': text,
                    'target_lang': target_lang
                }).encode('utf-8')

                request = urllib.request.Request(url, data=data, method=method, headers=headers)
                with urllib.request.urlopen(request) as response:
                    response_body = response.read().decode("utf-8")
                # レスポンスは配列だがデータは一つしかないため[0]で固定している
                result = json.loads(response_body)['translations'][0]['text'] + ' (translated)'

                await message.channel.send(result)

    client.run(token)
