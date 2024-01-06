import asyncio
import aiohttp
import discord
from discord import Webhook, app_commands
import psycopg2
from psycopg2 import sql
import socketio

from config import DBTable, DBHost, DBUsr, DBPass, DBPort, TOKEN, webhook_urls

intents = discord.Intents().all()
intents.members = True
intents.guilds = True

wanted = []

sio = socketio.AsyncClient()

class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.synced = False
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def on_ready(self):
        await self.wait_until_ready(logger=True, engineio_logger=True, reconnection_attempts=5)
        await sio.connect('https://skinport.com/', transports=['websocket'])
        await sio.emit('saleFeedJoin', {'currency': 'CAD', 'locale': 'en', 'appid': 730})
        if not self.synced:
            await client.sync()
            self.synced = True
        await asyncio.gather(on_startup())
        print(f'{self.user} has connected to Discord!')

Client = Client()
client = app_commands.CommandTree(Client)

@client.command(name = "addcsitem", description = "adds item to monitor")
async def addcsitem(interaction: discord.Interaction, itemid: str):
    try:
        conn = psycopg2.connect(dbname = DBTable, user = DBUsr, password = DBPass, host = DBHost, port = DBPort)
        curr = conn.cursor()

        postgreSQL_upload_Query = "INSERT INTO csgowant (id) VALUES (%s)"

        #data for the %s values
        data = (itemid,)
        curr.execute(postgreSQL_upload_Query, data)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        conn.close()

    global wanted
    wanted.append(itemid)

    await interaction.response.send_message("Added.")

    print(wanted)

async def on_startup():
    try:
        conn = psycopg2.connect(dbname = DBTable, user = DBUsr, password = DBPass, host = DBHost, port = DBPort)
        curr = conn.cursor()

        postgreSQL_select_Query = "select * from csgowant"
        curr.execute(postgreSQL_select_Query)
        table = curr.fetchall()

        for row in table:
            wanted.append(str(row[0]))

        conn.close()
    except Exception as e:
        conn.close()

@sio.on('saleFeed')
async def on_message(data):

    eventType = data.get("eventType")
    print(eventType)

    # Gathering what I need for the enbeds from the dict
    marketName = data["sales"][0]["marketName"]
    url = "https://skinport.com/item/" + str(data["sales"][0]["url"]) + "/" + str(data["sales"][0]["saleId"])
    lock = data["sales"][0]["lock"]
    deal = round((1 - (int(data["sales"][0]["salePrice"])/int(data["sales"][0]["suggestedPrice"]))) * 100, 2)
    stickers = data["sales"][0]["stickers"]
    itemid = data["sales"][0]["itemId"]
    pattern = data["sales"][0]["pattern"]
    finish = data["sales"][0]["finish"]
    img = "https://community.cloudflare.steamstatic.com/economy/image/" + data["sales"][0]["image"]
    
    sale = str(data["sales"][0]["salePrice"])
    if len(sale) > 2:
        saleNoCents = sale[:-2]
    else:
        saleNoCents = 0
    salePrice = sale[:-2] + "." + sale[-2:]
    
    if data["sales"][0]["wear"]:
        wear = round(data["sales"][0]["wear"], 6)
    else:
        wear = data["sales"][0]["wear"]
    exterior = data["sales"][0]["exterior"]
    if exterior == "Factory New":
        exterior = "FN"
    if exterior == "Minimal Wear":
        exterior = "MW"
    if exterior == "Field-Tested":
        exterior = "FT"
    if exterior == "Well-Worn":
        exterior = "WW"
    if exterior == "Battle-Scarred":
        exterior = "BS"
    if exterior == "None":
        exterior = "NA"

    # Low Float Channel
    if eventType == "listed":
        async with aiohttp.ClientSession() as s:
            webhook = Webhook.from_url('', session=s)

            embed = discord.Embed(title=marketName + " Listed", description="PRICE: " + str(salePrice), url=url, color=0x000000)
            embed.add_field(name="Deal %", value=str(deal), inline=True)
            embed.add_field(name="Wear | Float", value=str(exterior) + " | " + str(wear), inline=True)
            embed.add_field(name="Locked Until", value=str(lock), inline=True)
            embed.add_field(name="Pattern", value=str(pattern), inline=True)
            embed.set_thumbnail(url=img)

            await webhook.send(embed=embed)

    # Sold Channel
    if eventType == "sold":
        async with aiohttp.ClientSession() as s:
            webhook = Webhook.from_url('', session=s)

            embed = discord.Embed(title=marketName + " Sold", description="PRICE: " + str(salePrice), url=url, color=0x000000)
            embed.add_field(name="Deal %", value=str(deal), inline=True)
            embed.add_field(name="Wear | Float", value=str(exterior) + " | " + str(wear), inline=True)
            embed.add_field(name="Locked Until", value=str(lock), inline=True)
            embed.add_field(name="Pattern", value=str(pattern), inline=True)
            embed.set_thumbnail(url=img)

            await webhook.send(embed=embed)

    # Listed Channel
    if eventType == "listed":
        async with aiohttp.ClientSession() as s:
            webhook = Webhook.from_url('', session=s)

            embed = discord.Embed(title=marketName + " Listed", description="PRICE: " + str(salePrice), url=url, color=0x000000)
            embed.add_field(name="Deal %", value=str(deal), inline=True)
            embed.add_field(name="Wear | Float", value=str(exterior) + " | " + str(wear), inline=True)
            embed.add_field(name="Locked Until", value=str(lock), inline=True)
            embed.add_field(name="Pattern", value=str(pattern), inline=True)
            embed.set_thumbnail(url=img)

            await webhook.send(embed=embed)

    # What I Am Looking For Channel
    if eventType == "listed" and any(x in str(itemid) for x in wanted):
        async with aiohttp.ClientSession() as s:
            webhook = Webhook.from_url('', session=s)

            embed = discord.Embed(title=marketName + " Listed", description="PRICE: " + str(salePrice), url=url, color=0x000000)
            embed.add_field(name="Deal %", value=str(deal), inline=True)
            embed.add_field(name="Wear | Float", value=str(exterior) + " | " + str(wear), inline=True)
            embed.add_field(name="Locked Until", value=str(lock), inline=True)
            embed.add_field(name="Pattern", value=str(pattern), inline=True)
            embed.set_thumbnail(url=img)

            await webhook.send(embed=embed)

    # What I Am Looking For Channel Sold
    if eventType == "sold" and any(x in str(itemid) for x in wanted):
        async with aiohttp.ClientSession() as s:
            webhook = Webhook.from_url('', session=s)

            embed = discord.Embed(title=marketName + " Sold", description="PRICE: " + str(salePrice), url=url, color=0x000000)
            embed.add_field(name="Deal %", value=str(deal), inline=True)
            embed.add_field(name="Wear | Float", value=str(exterior) + " | " + str(wear), inline=True)
            embed.add_field(name="Locked Until", value=str(lock), inline=True)
            embed.add_field(name="Pattern", value=str(pattern), inline=True)
            embed.set_thumbnail(url=img)

            await webhook.send(embed=embed)

    # Listed + Good Deal Channel
    if eventType == "listed" and deal >= 25 and int(saleNoCents) > 4:
        async with aiohttp.ClientSession() as s:
            webhook = Webhook.from_url('', session=s)

            embed = discord.Embed(title=marketName + " Listed", description="PRICE: " + str(salePrice), url=url, color=0x000000)
            embed.add_field(name="Deal %", value=str(deal), inline=True)
            embed.add_field(name="Wear | Float", value=str(exterior) + " | " + str(wear), inline=True)
            embed.add_field(name="Locked Until", value=str(lock), inline=True)
            embed.add_field(name="Pattern", value=str(pattern), inline=True)
            embed.set_thumbnail(url=img)

            await webhook.send(embed=embed)

Client.run(TOKEN)