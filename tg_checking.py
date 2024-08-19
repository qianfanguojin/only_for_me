
import os,sys
import time
from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

async def initialize_client(api_id, api_hash, auth_string, proxy):
    client = TelegramClient(StringSession(auth_string), api_id, api_hash, proxy=proxy)
    await client.start()
    return client

async def handle_bot_interaction(client, chat_entity, bot_entity, command, success_message):
    msg = ""
    try:
        await client.send_message(chat_entity, command)
        time.sleep(2)
        result = await client.get_messages(chat_entity, wait_time=1, from_user=bot_entity)
        msg = f"{success_message}\n{result[0].message}"
        await client.send_read_acknowledge(chat_entity)
    except Exception as e:
        msg = f"Error: {e}"
    print(msg)
    return msg

async def handle_getfree_cloud(client, event):
    getfree_cloud_chat_entity = await client.get_entity('t.me/GetfreeCloud')
    getfree_cloud_bot_entity = await client.get_entity('t.me/GetfreeCloud_Bot')
    if event == 'upgrade_getfree':
        return await handle_bot_interaction(client, getfree_cloud_chat_entity, getfree_cloud_bot_entity, '/upgrade@GetfreeCloud_Bot', '\n\nGetfree Upgraded !!')
    else:
        return await handle_bot_interaction(client, getfree_cloud_chat_entity, getfree_cloud_bot_entity, '/checkin@GetfreeCloud_Bot', '\n\n@GetfreeCloud_Bot Checked !!')

async def handle_ikuuu_vpn(client):
    ikuuu_vpn_bot_entity = await client.get_entity("t.me/iKuuuu_VPN_bot")
    return await handle_bot_interaction(client, ikuuu_vpn_bot_entity, ikuuu_vpn_bot_entity, '/checkin', '\n\n@iKuuuu_VPN_bot Checked !!')

async def checkin(event):
    print("Checking Prepare !!")
    api_id_list = os.getenv("TG_APP_ID").split(";")
    api_hash_list = os.getenv("TG_API_HASH").split(";")
    auth_string_list = os.getenv("TG_AUTH_KEY").split(";")
    proxy_type = "http"
    proxy_host = os.getenv("TG_PROXY_HOST")
    proxy_port = os.getenv("TG_PROXY_PORT")
    proxy = (proxy_type, proxy_host, proxy_port)

    for api_id, api_hash, auth_string in zip(api_id_list, api_hash_list, auth_string_list):
        client = await initialize_client(api_id, api_hash, auth_string, proxy)
        res1 = await handle_getfree_cloud(client, event)
        res2 = await handle_ikuuu_vpn(client)
        import notify
        notify.send("【TG 签到】", res1 + res2)

if __name__ == "__main__":
    event = None
    if len(sys.argv) > 1 and sys.argv[1] != "":
        event = sys.argv[1]
    asyncio.run(checkin(event))
