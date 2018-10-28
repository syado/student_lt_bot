import asyncio
import discord
import requests
import re
import json
from requests_oauthlib import OAuth1Session
import os

try:
    f = open("config.json", encoding='utf-8')
    config = json.load(f)
    f.close()

    hashtag = config["twitter"]["hashtag"]
    url = config["twitter"]["api_url"]
    consumer_key = config["twitter"]["consumer_key"]
    consumer_secret = config["twitter"]["consumer_secret"]
    access_token_key = config["twitter"]["access_token_key"]
    access_token_secret = config["twitter"]["access_token_secret"]

    token = config["discord"]["token"]
    channel_id = config["discord"]["channel_id"]
    server_id = config["discord"]["server_id"]
    entry_id = config["discord"]["entry_id"]
except:
    hashtag = os.getenv("twitter_hashtag", None)
    url = os.getenv("twitter_api_url", None)
    consumer_key = os.getenv("twitter_consumer_key", None)
    consumer_secret = os.getenv("twitter_consumer_secret", None)
    access_token_key = os.getenv("twitter_access_token_key", None)
    access_token_secret = os.getenv("twitter_access_token_secret", None)

    token = os.getenv("discord_token", None)
    channel_id = os.getenv("discord_channel_id", None)
    server_id = os.getenv("discord_server_id", None)
    entry_id = os.getenv("discord_entry_id", None)


client = discord.Client()
twitter = OAuth1Session(consumer_key, consumer_secret, access_token_key, access_token_secret)

@client.event
async def on_ready():
    print(client.user.name)
    print(client.user.id)
    print('It is ready')

@client.event
async def on_member_join(member):
    if member.server.id == server_id:
        m = "ようこそ<@"+member.id+">さん\n<#429523809926905865>を読み次第「ok」と入力してください\n実践していただければ書き込み可能となります"
        return await client.send_message(client.get_channel(entry_id), m)

@client.event
async def on_member_remove(member):
    if member.server.id == server_id:
        m = "<@"+member.id+">さんが退会しました"
        return await client.send_message(client.get_channel(entry_id), m)

@client.event
async def on_message(message):
    if message.server.id == server_id:
        if message.content.lower() == "ok":
            role = discord.utils.get(message.server.roles, name="user")
            return await client.add_roles(message.author, role)

    if message.channel.id == channel_id:
        user = message.author.display_name
        if len(user) > 10:
            user = user[:9]+"…"
        text = message.content
        
        while True:
            r = re.search(r"<@[0-9]+>", text)
            if r:
                member = message.server.get_member(r.group()[2:-1])
                text = text.replace(r.group(), ">>"+member.name)
            else:
                break

        while True:
            r = re.search(r"<@![0-9]+>", text)
            if r:
                member = message.server.get_member(r.group()[3:-1])
                text = text.replace(r.group(), ">>"+member.name)
            else:
                break

        while True:
            r = re.search(r"<#[0-9]+>", text)
            if r:
                channel = message.server.get_channel(r.group()[2:-1])
                text = text.replace(r.group(), channel.name+"_ch")
            else:
                break

        while True:
            r = re.search(r"<#![0-9]+>", text)
            if r:
                channel = message.server.get_channel(r.group()[3:-1])
                text = text.replace(r.group(), channel.name+"_ch")
            else:
                break
        
        text = re.sub('`','',text)

        content = user+": "+text
        hashtag1 = "\n"+hashtag
        if len(content) > 140-len(hashtag1):
            content = content[:139-len(hashtag1)]+"…"+hashtag1

        params = {"status": content}
        try:
            req = twitter.post(url, params = params)
            if req.status_code == 200:
                print (text)
            else:
                print ("Error: %d" % req.status_code)
        except:
            print ("Error")

if __name__ == "__main__":
    client.run(token)
