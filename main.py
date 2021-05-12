import urllib.request
import discord
import json
import re
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path=join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

token=os.environ.get('TOKEN')

client=discord.Client()


@client.event
async def on_ready():
    print('ログインしました')


@client.event
async def on_message(message):
    if '/translate' in message.content:
        if message.content == '/translate-help':
            await message.channel.send(embed=create_help_embed()['ja'])
            await message.channel.send(embed=create_help_embed()['en'])

        # 翻訳したい内容が[]に入っていない場合、エラーを返却する
        elif len(re.findall(r'\[(.+)\]', message.content)) == 0:
            embed=discord.Embed(
                title='Failure!',
                description=
                    '翻訳したい内容を[]に入れてください。\r\n'\
                    'Enter the content you want to translate in [].',
                color=discord.Colour.random()
            )
            await message.channel.send(embed=embed)

        else:
            result = request_to_translate(message.content)
            if result['flg'] == 'false':
                await message.channel.send(embed=result['response'])
            if result['flg'] == 'true':
                await message.channel.send(result['response'])


# /translateコマンドのヘルプを作成
def create_help_embed():
    # 日本語版ヘルプのembed作成
    embed_ja=discord.Embed(
        title='/translateコマンドの使い方',
        description=
            '翻訳したい内容を[]に入れてください。\r\n' \
            '翻訳したい言語を()に指定してください。\r\n\r\n'\
            '(例)\r\n' \
            '入力: /translate \[Hello World\]\(DE\) \r\n'\
            '出力: Hallo Welt (translated)\r\n\r\n'\
            '以下から翻訳したい言語を指定してください。\r\n'\
            'もし言語を選択しない場合、英語で翻訳されます。',
        color=discord.Colour.random()
    )
    embed_ja.add_field(name="ドイツ語", value="DE")
    embed_ja.add_field(name="英語", value="EN")
    embed_ja.add_field(name="イタリア語", value="IT")
    embed_ja.add_field(name="日本語", value="JP")
    embed_ja.add_field(name="ルーマニア語", value="RO")
    embed_ja.add_field(name="ロシア語", value="RU")
    embed_ja.add_field(name="スウェーデン語", value="SV")

    # 英語版ヘルプのembed作成
    embed_en=discord.Embed(
        title='How to use the /translate command',
        description=
            'Enter the content you want to translate in [].\r\n'\
            'Specify the language you want to translate in ().\r\n\r\n'\
            '(example)\r\n'\
            'input: /translate \[Hello World\]\(DE\) \r\n'\
            'output: Hallo Welt (translated)\r\n\r\n'\
            'Specify the language you want to translate from below.\r\n'\
            'If you don\'t specify the language, it will be translated in English.',
        color=discord.Colour.random()
    )
    embed_en.add_field(name="German", value="DE")
    embed_en.add_field(name="English", value="EN")
    embed_en.add_field(name="Italian", value="IT")
    embed_en.add_field(name="Japanese", value="JP")
    embed_en.add_field(name="Romanian", value="RO")
    embed_en.add_field(name="Russian", value="RU")
    embed_en.add_field(name="Swedish", value="SV")

    return {
        'ja': embed_ja,
        'en': embed_en
    }


def request_to_translate(message_content):
    url='https://api-free.deepl.com/v2/translate'

    # re.findallを使用すると配列になるので[0]をつけている
    text=re.findall(r'\[(.+)\]', message_content)[0]

    # 言語の指定がない場合英語で翻訳する
    target_lang='EN-US'

    if len(re.findall(r'\((.+)\)', message_content)) != 0:
        target_lang=re.findall(r'\((.+)\)', message_content)[0]

    if target_lang == 'EN':
        target_lang='EN-US'

    if target_lang == 'JP':
        target_lang='JA'

    # 翻訳したい言語が与えられた言語以外の場合、エラーを返却する
    if target_lang not in {'DE', 'EN-US', 'IT', 'JA', 'RO', 'RU', 'SV'}:
        embed=discord.Embed(
            title='Failure!',
            description=
                '以下から翻訳したい言語を指定してください。\r\n' \
                'Specify the language you want to translate from below.',
            color=discord.Colour.random()
        )
        embed.add_field(name="ドイツ語\r\nGerman", value="DE")
        embed.add_field(name="英語\r\nEnglish", value="EN")
        embed.add_field(name="イタリア語\r\nItalian", value="IT")
        embed.add_field(name="日本語\r\nJapanese", value="JP")
        embed.add_field(name="ルーマニア語\r\nRomanian", value="RO")
        embed.add_field(name="ロシア語\r\nRussian", value="RU")
        embed.add_field(name="スウェーデン語\r\nSwedish", value="SV")
        
        return {
            'flg': 'false',
            'response': embed
        }

    method='POST'
    auth_key=os.environ.get('AUTH_KEY')
    headers={'Content-Type': 'application/x-www-form-urlencoded'}

    data=urllib.parse.urlencode({
        'auth_key': auth_key,
        'text': text,
        'target_lang': target_lang
    }).encode('utf-8')

    request=urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(request) as response:
        response_body=response.read().decode('utf-8')

    # レスポンスは配列だがデータは一つしかないため[0]で固定している
    result = json.loads(response_body)['translations'][0]['text'] + ' (translated)'

    return {
        'flg': 'true',
        'response': result
    }


client.run(token)
