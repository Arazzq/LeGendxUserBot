# Ported from PaperPlaneExtended by avinashreddy3108 for media support
#
# @DogeUserBot - < https://t.me/DogeUserBot >
# Copyright (C) 2021 - DOG-E
# All rights reserved.
#
# This file is a part of < https://github.com/DOG-E/DogeUserBot >
# Please read the GNU Affero General Public License in;
# < https://www.github.com/DOG-E/DogeUserBot/blob/DOGE/LICENSE/ >
# ================================================================
from ..sql_helper.snip_sql import add_snip, del_snip, get_snip, get_snips
from . import BOTLOG, BOTLOG_CHATID, doge, edl, eor, get_message_link, gvar, reply_id

plugin_category = "misc"

SNIP_CMDSET = gvar("SNIP_CMDSET") or "&"


@doge.bot_cmd(pattern=f"^\{SNIP_CMDSET}(\S+)")
async def incom_snip(event):
    if not BOTLOG:
        return
    try:
        if not (await event.get_sender()).bot:
            snipname = event.text[1:]
            snipname = snipname.lower()
            snip = get_snip(snipname)
            message_id_to_reply = await reply_id(event)
            if snip:
                if snip.f_mesg_id:
                    msg_o = await event.client.get_messages(
                        entity=BOTLOG_CHATID, ids=int(snip.f_mesg_id)
                    )
                    await event.delete()
                    await event.client.send_message(
                        event.chat_id,
                        msg_o,
                        reply_to=message_id_to_reply,
                        link_preview=False,
                    )
                elif snip.reply:
                    await event.delete()
                    await event.client.send_message(
                        event.chat_id,
                        snip.reply,
                        reply_to=message_id_to_reply,
                        link_preview=False,
                    )
    except AttributeError:
        pass


@doge.bot_cmd(
    pattern="snip (\w*)",
    command=("snip", plugin_category),
    info={
        "header": "To save snips to the bot.",
        "description": f"Saves the replied message as a snip with the snipname. (Works with pics, docs, and stickers too!. and get them by using {SNIP_CMDSET}snipname",
        "usage": "{tr}snip <keyword>",
    },
)
async def add_sniper(event):
    "To save snips to bot."
    if not BOTLOG:
        return await edl(
            event, "`To save snip you need to set PRIVATE_GROUP_BOT_API_ID`"
        )
    keyword = event.pattern_match.group(1)
    string = event.text.partition(keyword)[2]
    msg = await event.get_reply_message()
    msg_id = None
    keyword = keyword.lower()
    if msg and not string:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#SNIP\
            \n**Keyword:** `{SNIP_CMDSET}{keyword}`\
            \n\nThe following message is saved as the snip in your bot, DON'T delete it!",
        )
        msg_o = await event.client.forward_messages(
            entity=BOTLOG_CHATID, messages=msg, from_peer=event.chat_id, silent=True
        )
        msg_id = msg_o.id
    elif msg:
        return await edl(
            event,
            "`What should I save for your snip either do reply or give snip text along with keyword`",
        )
    if not msg:
        if string:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#SNIP\
            \n**Keyword:** `{SNIP_CMDSET}{keyword}`\
            \n\nThe following message is saved as the snip in your bot, DON'T delete it!",
            )
            msg_o = await event.client.send_message(BOTLOG_CHATID, string)
            msg_id = msg_o.id
            string = None
        else:
            return await edl(event, "`what should I save for your snip`")
    success = "Snip {} is successfully {}. Use `{}{}` to get it"
    if add_snip(keyword, string, msg_id) is False:
        del_snip(keyword)
        if add_snip(keyword, string, msg_id) is False:
            return await eor(event, f"Error in saving the given snip {keyword}")
        return await eor(
            event, success.format(keyword, "updated", SNIP_CMDSET, keyword)
        )
    return await eor(event, success.format(keyword, "added", SNIP_CMDSET, keyword))


@doge.bot_cmd(
    pattern="snips$",
    command=("snips", plugin_category),
    info={
        "header": "To list all snips in bot.",
        "usage": "{tr}snips",
    },
)
async def on_snip_list(event):
    "To list all snips in bot."
    message = "You haven't saved any snip."
    snips = get_snips()
    if not BOTLOG:
        return await edl(
            event, "`For saving snip you must set PRIVATE_GROUP_BOT_API_ID`"
        )
    for snip in snips:
        if message == "You haven't saved any snip.":
            message = "Snips saved in your bot are\n\n"
        message += f"👉 `{SNIP_CMDSET}{snip.keyword}`"
        if snip.f_mesg_id:
            msglink = await get_message_link(BOTLOG_CHATID, snip.f_mesg_id)
            message += f"  [preview]({msglink})\n"
        else:
            message += "  No preview\n"
    await eor(event, message)


@doge.bot_cmd(
    pattern="dsnip (\S+)",
    command=("dsnip", plugin_category),
    info={
        "header": "To delete paticular snip in bot.",
        "usage": "{tr}dsnip <keyword>",
    },
)
async def on_snip_delete(event):
    "To delete paticular snip in bot."
    name = event.pattern_match.group(1)
    name = name.lower()
    dogsnip = get_snip(name)
    if dogsnip:
        del_snip(name)
    else:
        return await eor(
            event, f"Are you sure that `{SNIP_CMDSET}{name}` is saved as snip?"
        )
    await eor(event, f"Snip `{SNIP_CMDSET}{name}` deleted successfully!")
