import json
from aiocqhttp.event import Event
from hoshino import R, Service, priv, aiorequests
from nonebot import get_bot
import math
import traceback

sv = Service("server-status",visible=False)

server_status_addr = "https://status.coldthunder11.com/"
server_status_endpoint = "json/stats.json"
notice_uid = 2561502056

last_status = None

@sv.on_fullmatch('服务器状态')
async def on_query_status(bot,ev):
    try:
        resp = await aiorequests.get(server_status_addr+server_status_endpoint)
        res = await resp.json()
        msg_list = []
        for i in range(len(res["servers"])):
            msg_list.append(res["servers"][i]["name"])
            msg_list.append("  ")
            if res["servers"][i]["online4"] != True:
                msg_list.append("离线")
            else:
                msg_list.append("在线")
                msg_list.append("  ")
                msg_list.append("CPU：")
                msg_list.append(str(res["servers"][i]["cpu"]))
                msg_list.append("%  内存")
                msg_list.append(str(math.floor((res["servers"][i]["memory_used"]/res["servers"][i]["memory_total"])*100)))
                msg_list.append("%")
            msg_list.append("\n")
        await bot.send(ev,''.join(msg_list).strip())
    except:
        traceback.print_exc()
        pass

@sv.scheduled_job('interval', minutes=3)
async def on_status_schedule():
    global last_status
    bot = get_bot()
    try:
        resp = await aiorequests.get(server_status_addr+server_status_endpoint)
        res = await resp.json()
        if not "servers" in res:
            return
        if last_status == None or len(last_status["servers"]) != len(res["servers"]):
            last_status = res
            return
        for i in range(len(last_status["servers"])):
            if last_status["servers"][i]["name"] == res["servers"][i]["name"]:
                if last_status["servers"][i]["online4"] != res["servers"][i]["online4"]:
                    if res["servers"][i]["online4"] == False:
                        await bot.send_private_msg(user_id=notice_uid,message=f'服务器{res["servers"][i]["name"]}走丢了！')
                    else:
                        await bot.send_private_msg(user_id=notice_uid,message=f'服务器{res["servers"][i]["name"]}已上线！')
        last_status = res
    except:
        pass
