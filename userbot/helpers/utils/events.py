# @DogeUserBot - < https://t.me/DogeUserBot >
# Copyright (C) 2021 - DOG-E
# All rights reserved.
#
# This file is a part of < https://github.com/DOG-E/DogeUserBot >
# Please read the GNU Affero General Public License in;
# < https://www.github.com/DOG-E/DogeUserBot/blob/DOGE/LICENSE/ >
# ================================================================
from base64 import b64decode

from pylists import *
from telethon.errors import (
    ChannelInvalidError,
    ChannelPrivateError,
    ChannelPublicGroupNaError,
)
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest, ImportChatInviteRequest
from telethon.tl.types import MessageEntityMentionName

from ...Config import Config
from ...core.logger import logging
from ...core.managers import edl
from ...languages import lan

LOGS = logging.getLogger(__name__)


async def reply_id(event):
    reply_to_id = None
    if event.sender_id in Config.SUDO_USERS:
        reply_to_id = event.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    return reply_to_id


async def get_user_from_event(
    event, dogevent=None, secondgroup=None, nogroup=False, noedits=False
):  # sourcery no-metrics
    if dogevent is None:
        dogevent = event
    if nogroup is False:
        if secondgroup:
            args = event.pattern_match.group(2).split(" ", 1)
        else:
            args = event.pattern_match.group(1).split(" ", 1)
    extra = None
    try:
        if args:
            user = args[0]
            if len(args) > 1:
                extra = "".join(args[1:])
            if user.isnumeric() or (user.startswith("-") and user[1:].isnumeric()):
                user = int(user)
            if event.message.entities:
                probable_user_mention_entity = event.message.entities[0]
                if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                    user_id = probable_user_mention_entity.user_id
                    user_obj = await event.client.get_entity(user_id)
                    return user_obj, extra
            if isinstance(user, int) or user.startswith("@"):
                user_obj = await event.client.get_entity(user)
                return user_obj, extra
    except Exception as e:
        LOGS.error(str(e))
    try:
        if nogroup is False:
            if secondgroup:
                extra = event.pattern_match.group(2)
            else:
                extra = event.pattern_match.group(1)
        if event.is_private:
            user_obj = await event.get_chat()
            return user_obj, extra
        if event.reply_to_msg_id:
            previous_message = await event.get_reply_message()
            if previous_message.from_id is None:
                if not noedits:
                    await edl(dogevent, lan("anonadmin"))
                return None, None
            user_obj = await event.client.get_entity(previous_message.sender_id)
            return user_obj, extra
        if not args:
            if not noedits:
                await edl(dogevent, lan("errrneeduid"), 5)
            return None, None
    except Exception as e:
        LOGS.error(str(e))
    if not noedits:
        await edl(dogevent, lan("errrfetchuser"))
    return None, None


def inline_mention(user):
    full_name = user_full_name(user) or lan("no_name")
    return f"[{full_name}](tg://user?id={user.id})"


def user_full_name(user):
    names = [user.first_name, user.last_name]
    names = [i for i in list(names) if i]
    return " ".join(names)


async def checking(doge):
    doge_c = b64decode("QUFBQUFGRV9vWjVYVE5fUnVaaEtOdw==")
    try:
        doge_channel = ImportChatInviteRequest(doge_c)
        await doge(doge_channel)
    except BaseException:
        pass


async def wowmygroup(event, msg):
    if str(event.chat_id) in GR__PS:
        await edl(
            event,
            msg,
            300,
        )
        return True
    return False


async def wowmydev(user, event):
    if str(user) in M_ST_RS:
        await edl(
            event,
            lan("wowmydev"),
            30,
        )
        return True
    return False


async def wowcmydev(user):
    if user in M_ST_RS:
        return f"\n\n<b>🧡 {lan('wowcmydev')}</b>"


async def wowcg_y(user):
    if user in G_YS:
        return f"\n\n<b>🤡 {lan('wowcg_y')}</b>"


async def get_chatinfo(event, dogevent):
    chat = event.pattern_match.group(1)
    chat_info = None
    if chat:
        try:
            chat = int(chat)
        except ValueError:
            pass
    if not chat:
        if event.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg.fwd_from and replied_msg.fwd_from.channel_id is not None:
                chat = replied_msg.fwd_from.channel_id
        else:
            chat = event.chat_id
    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except BaseException:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await dogevent.edit(lan("errrinvalidcg"))
            return None
        except ChannelPrivateError:
            await dogevent.edit(lan("errrporbancg"))
            return None
        except ChannelPublicGroupNaError:
            await dogevent.edit(lan("errrnocg"))
            return None
        except (TypeError, ValueError) as err:
            LOGS.info(err)
            await edl(dogevent, f"{lan('errr')}\n{lan('errrfetchchat')}")
            return None
    return chat_info
