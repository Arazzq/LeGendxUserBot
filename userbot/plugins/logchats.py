# Credits: @mrconfused (@sandy1709)
#
# @DogeUserBot - < https://t.me/DogeUserBot >
# Copyright (C) 2021 - DOG-E
# All rights reserved.
#
# This file is a part of < https://github.com/DOG-E/DogeUserBot >
# Please read the GNU Affero General Public License in;
# < https://www.github.com/DOG-E/DogeUserBot/blob/DOGE/LICENSE/ >
# ================================================================

from telethon import Button

from ..sql_helper import no_log_pms_sql
from . import (
    BOTLOG,
    BOTLOG_CHATID,
    PM_LOGGER_GROUP_ID,
    _format,
    doge,
    edl,
    gvar,
    logging,
    media_type,
    sgvar,
)

plugin_category = "bot"
LOGS = logging.getLogger(__name__)


class LOG_CHATS:
    def __init__(self):
        self.RECENT_USER = None
        self.NEWPM = None
        self.COUNT = 0


LOG_CHATS_ = LOG_CHATS()


@doge.bot_cmd(incoming=True, func=lambda e: e.is_private, edited=False, forword=None)
async def monito_p_m_s(event):  # sourcery no-metrics
    if PM_LOGGER_GROUP_ID == -100:
        return
    if gvar("PMLOG") and gvar("PMLOG") == "false":
        return
    sender = await event.get_sender()
    if not sender.bot:
        chat = await event.get_chat()
        if not no_log_pms_sql.is_approved(chat.id) and chat.id != 777000:
            if LOG_CHATS_.RECENT_USER != chat.id:
                LOG_CHATS_.RECENT_USER = chat.id
                if LOG_CHATS_.NEWPM:
                    if LOG_CHATS_.COUNT > 1:
                        await LOG_CHATS_.NEWPM.edit(
                            LOG_CHATS_.NEWPM.text.replace(
                                "new message", f"{LOG_CHATS_.COUNT} messages"
                            )
                        )
                    else:
                        await LOG_CHATS_.NEWPM.edit(
                            LOG_CHATS_.NEWPM.text.replace(
                                "new message", f"{LOG_CHATS_.COUNT} message"
                            )
                        )
                    LOG_CHATS_.COUNT = 0
                LOG_CHATS_.NEWPM = await event.client.send_message(
                    PM_LOGGER_GROUP_ID,
                    f"🪐 #PM\n👤 {_format.mentionuser(sender.first_name, sender.id)} has sent a new message \nID: `{chat.id}`",
                    slient=True,
                )
            try:
                if event.message:
                    await event.client.forward_messages(
                        PM_LOGGER_GROUP_ID, event.message, silent=True
                    )
                LOG_CHATS_.COUNT += 1
            except Exception as e:
                LOGS.warn(str(e))


@doge.bot_cmd(incoming=True, func=lambda e: e.mentioned, edited=False, forword=None)
async def log_tagged_messages(event):
    hmm = await event.get_chat()
    from .afk import AFK_

    if gvar("GRPLOG") and gvar("GRPLOG") == "false":
        return
    if (
        (no_log_pms_sql.is_approved(hmm.id))
        or (PM_LOGGER_GROUP_ID == -100)
        or ("on" in AFK_.USERAFK_ON)
        or (await event.get_sender() and (await event.get_sender()).bot)
    ):
        return

    full = None
    try:
        full = await event.client.get_entity(event.message.from_id)
    except Exception as e:
        LOGS.info(str(e))
    messaget = media_type(event)
    resalt = f"🔔 #TAG\n<b>👥 Group: </b><code>{hmm.title}</code>"
    if full is not None:
        resalt += (
            f"\n<b>👤 From: </b>{_format.htmlmentionuser(full.first_name, full.id)}"
        )
    if messaget is not None:
        resalt += f"\n<b>🔅 Message Type: </b><code>{messaget}</code>"
    else:
        resalt += f"\n<b>🔹 Message: </b>{event.message.message}"
    button = [
        (Button.url("👁‍🗨 Mᴇssᴀɢᴇ", f"https://t.me/c/{hmm.id}/{event.message.id}"))
    ]
    if not event.is_private:
        await event.client.send_message(
            PM_LOGGER_GROUP_ID,
            resalt,
            parse_mode="html",
            link_preview=False,
            slient=True,
        )
        if messaget is not None:
            await event.client.forward_messages(
                PM_LOGGER_GROUP_ID, event.message, silent=True
            )


@doge.bot_cmd(
    pattern="save(?:\s|$)([\s\S]*)",
    command=("save", plugin_category),
    info={
        "header": "To log the replied message to bot log group so you can check later.",
        "description": "Set PRIVATE_GROUP_BOT_API_ID in vars for functioning of this",
        "usage": [
            "{tr}save <text/reply>",
        ],
    },
)
async def log(log_text):
    "To log the replied message to bot log group"
    if BOTLOG:
        if log_text.reply_to_msg_id:
            reply_msg = await log_text.get_reply_message()
            await reply_msg.forward_to(BOTLOG_CHATID)
        elif log_text.pattern_match.group(1):
            user = f"#SAVED 💾\n🆔 Chat ID: {log_text.chat_id}\n\n"
            textx = user + log_text.pattern_match.group(1)
            await doge.send_message(BOTLOG_CHATID, textx)
        else:
            return await edl(log_text, "`What am I supposed to log?`")

        await edl(log_text, "`Logged successfully`")
    else:
        await edl(log_text, "`This feature requires Logging to be enabled!`")


@doge.bot_cmd(
    pattern="logon$",
    command=("logon", plugin_category),
    info={
        "header": "To turn on logging of messages from that chat.",
        "description": "Set PM_LOGGER_GROUP_ID in vars to work this",
        "usage": [
            "{tr}logon",
        ],
    },
)
async def set_no_log_p_m(event):
    "To turn on logging of messages from that chat."
    if PM_LOGGER_GROUP_ID != -100:
        chat = await event.get_chat()
        if no_log_pms_sql.is_approved(chat.id):
            no_log_pms_sql.disapprove(chat.id)
            await edl(
                event,
                "`Logging of messages from this chat has been started!`",
            )


@doge.bot_cmd(
    pattern="logoff$",
    command=("logoff", plugin_category),
    info={
        "header": "To turn off logging of messages from that chat.",
        "description": "Set PM_LOGGER_GROUP_ID in vars to work this",
        "usage": [
            "{tr}logoff",
        ],
    },
)
async def set_no_log_p_m(event):
    "To turn off logging of messages from that chat."
    if PM_LOGGER_GROUP_ID != -100:
        chat = await event.get_chat()
        if not no_log_pms_sql.is_approved(chat.id):
            no_log_pms_sql.approve(chat.id)
            await edl(
                event,
                "`Logging of messages from this chat has been stopped!`",
            )


@doge.bot_cmd(
    pattern="pmlog (on|off)$",
    command=("pmlog", plugin_category),
    info={
        "header": "To turn on or turn off logging of Private messages in pmlogger group.",
        "description": "Set PM_LOGGER_GROUP_ID in vars to work this",
        "usage": [
            "{tr}pmlog on",
            "{tr}pmlog off",
        ],
    },
)
async def set_pmlog(event):
    "To turn on or turn off logging of Private messages"
    if PM_LOGGER_GROUP_ID == -100:
        return await edl(
            event,
            "__For functioning of this you need to set PM_LOGGER_GROUP_ID in config vars__",
        )
    input_str = event.pattern_match.group(1)
    if input_str == "off":
        h_type = False
    elif input_str == "on":
        h_type = True
    if gvar("PMLOG") and gvar("PMLOG") == "false":
        PMLOG = False
    else:
        PMLOG = True
    if PMLOG:
        if h_type:
            await edl(event, "`Pm logging is already enabled`")
        else:
            sgvar("PMLOG", h_type)
            await edl(event, "`Pm logging is disabled`")
    elif h_type:
        sgvar("PMLOG", h_type)
        await edl(event, "`Pm logging is enabled`")
    else:
        await edl(event, "`Pm logging is already disabled`")


@doge.bot_cmd(
    pattern="grplog (on|off)$",
    command=("grplog", plugin_category),
    info={
        "header": "To turn on or turn off group tags logging in pmlogger group.",
        "description": "Set PM_LOGGER_GROUP_ID in vars to work this",
        "usage": [
            "{tr}grplog on",
            "{tr}grplog off",
        ],
    },
)
async def set_grplog(event):
    "To turn on or turn off group tags logging"
    if PM_LOGGER_GROUP_ID == -100:
        return await edl(
            event,
            "__For functioning of this you need to set PM_LOGGER_GROUP_ID in config vars__",
        )
    input_str = event.pattern_match.group(1)
    if input_str == "off":
        h_type = False
    elif input_str == "on":
        h_type = True
    if gvar("GRPLOG") and gvar("GRPLOG") == "false":
        GRPLOG = False
    else:
        GRPLOG = True
    if GRPLOG:
        if h_type:
            await edl(event, "`Group logging is already enabled`")
        else:
            sgvar("GRPLOG", h_type)
            await edl(event, "`Group logging is disabled`")
    elif h_type:
        sgvar("GRPLOG", h_type)
        await edl(event, "`Group logging is enabled`")
    else:
        await edl(event, "`Group logging is already disabled`")
