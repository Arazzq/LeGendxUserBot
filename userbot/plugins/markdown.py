# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# @DogeUserBot - < https://t.me/DogeUserBot >
# Copyright (C) 2021 - DOG-E
# All rights reserved.
#
# This file is a part of < https://github.com/DOG-E/DogeUserBot >
# Please read the GNU Affero General Public License in;
# < https://www.github.com/DOG-E/DogeUserBot/blob/DOGE/LICENSE/ >
# ================================================================
from functools import partial
from random import choice
from re import DOTALL, compile, escape, sub

from telethon.events import StopPropagation
from telethon.extensions.markdown import DEFAULT_URL_RE
from telethon.tl.functions.messages import EditMessageRequest
from telethon.tl.types import (
    MessageEntityBold,
    MessageEntityCode,
    MessageEntityItalic,
    MessageEntityPre,
    MessageEntityStrike,
    MessageEntityTextUrl,
    MessageEntityUnderline,
)
from telethon.utils import add_surrogate, del_surrogate

from . import doge, logging

plugin_category = "tool"
LOGS = logging.getLogger(__name__)

usernexp = compile(r"@(\w{3,32})\[(.+?)\]")
nameexp = compile(r"\[([\w\S]+)\]\(tg://user\?id=(\d+)\)\[(.+?)\]")


def parse_url_match(m):
    entity = MessageEntityTextUrl(
        offset=m.start(), length=len(m.group(1)), url=del_surrogate(m.group(2))
    )
    return m.group(1), entity


def get_tag_parser(tag, entity):
    def tag_parser(m):
        return m.group(1), entity(offset=m.start(), length=len(m.group(1)))

    tag = escape(tag)
    return compile(tag + r"(.+?)" + tag, DOTALL), tag_parser


PRINTABLE_ASCII = range(0x21, 0x7F)


def parse_aesthetics(m):
    def aesthetify(string):
        for c in string:
            if " " < c <= "~":
                yield chr(ord(c) + 0xFF00 - 0x20)
            elif c == " ":
                yield "\u3000"
            else:
                yield c

    return "".join(aesthetify(m[1])), None


def parse_randcase(m):
    return "".join(choice([str.upper, str.lower])(c) for c in m[1]), None


def parse_b_meme(m):
    return sub(r"(\s|^)\S(\S)", r"\1🅱️\2", m[1]), None


def parse_subreddit(m):
    text = "/" + m.group(3)
    entity = MessageEntityTextUrl(
        offset=m.start(2), length=len(text), url=f"https://reddit.com{text}"
    )
    return m.group(1) + text, entity


def parse_strikethrough(m):
    text = m.group(2)
    text = "\u0336".join(text) + "\u0336 "
    return text, None


PARSED_ENTITIES = (
    MessageEntityBold,
    MessageEntityItalic,
    MessageEntityCode,
    MessageEntityPre,
    MessageEntityTextUrl,
    MessageEntityUnderline,
)
# A matcher is a tuple of (regex pattern, parse function)
# where the parse function takes the match and returns (text, entity)
MATCHERS = [
    (DEFAULT_URL_RE, parse_url_match),
    (get_tag_parser("**", MessageEntityBold)),
    (get_tag_parser("__", MessageEntityItalic)),
    (get_tag_parser("```", partial(MessageEntityPre, language=""))),
    (get_tag_parser("`", MessageEntityCode)),
    (get_tag_parser("--", MessageEntityUnderline)),
    (compile(r"\+\+(.+?)\+\+"), parse_aesthetics),
    (compile(r"([^/\w]|^)(/?(r/\w+))"), parse_subreddit),
    (compile(r"(?<!\w)(~{2})(?!~~)(.+?)(?<!~)\1(?!\w)"), parse_strikethrough),
]


def parse(message, old_entities=None):
    try:
        entities = []
        old_entities = sorted(old_entities or [], key=lambda e: e.offset)

        i = 0
        after = 0
        message = add_surrogate(message)
        while i < len(message):
            for after, e in enumerate(old_entities[after:], start=after):
                # If the next entity is strictly to our right, we're done here
                if i < e.offset:
                    break
                # Skip already existing entities if we're at one
                if i == e.offset:
                    i += e.length
            else:
                after += 1

            # Find the first pattern that matches
            for pattern, parser in MATCHERS:
                match = pattern.match(message, pos=i)
                if match:
                    break
            else:
                i += 1
                continue

            text, entity = parser(match)

            # Shift old entities after our current position (so they stay in place)
            shift = len(text) - len(match[0])
            if shift:
                for e in old_entities[after:]:
                    e.offset += shift

            # Replace whole match with text from parser
            message = "".join((message[: match.start()], text, message[match.end() :]))

            # Append entity if we got one
            if entity:
                entities.append(entity)

            # Skip past the match
            i += len(text)

        return del_surrogate(message), entities + old_entities
    except Exception as e:
        LOGS.info(str(e))


@doge.bot_cmd(outgoing=True)
async def reparse(event):
    old_entities = event.message.entities or []
    parser = partial(parse, old_entities=old_entities)
    if event.raw_text:
        message, msg_entities = await event.client._parse_message_text(
            event.raw_text, parser
        )
        if len(old_entities) >= len(msg_entities) and event.raw_text == message:
            return
        await event.client(
            EditMessageRequest(
                peer=await event.get_input_chat(),
                id=event.message.id,
                message=message,
                no_webpage=not bool(event.message.media),
                entities=msg_entities,
            )
        )
        raise StopPropagation


@doge.bot_cmd(outgoing=True)
async def mention(event):
    newstr = event.text
    if event.entities:
        newstr = nameexp.sub(r'<a href="tg://user?id=\2">\3</a>', newstr, 0)
        for match in usernexp.finditer(newstr):
            user = match.group(1)
            text = match.group(2)
            name, entities = await event.client._parse_message_text(text, "md")
            rep = f'<a href="tg://resolve?domain={user}">{name}</a>'
            if entities:
                for e in entities:
                    tag = None
                    if isinstance(e, MessageEntityBold):
                        tag = "<b>{}</b>"
                    elif isinstance(e, MessageEntityItalic):
                        tag = "<i>{}</i>"
                    elif isinstance(e, MessageEntityCode):
                        tag = "<code>{}</code>"
                    elif isinstance(e, MessageEntityStrike):
                        tag = "<s>{}</s>"
                    elif isinstance(e, MessageEntityPre):
                        tag = "<pre>{}</pre>"
                    elif isinstance(e, MessageEntityUnderline):
                        tag = "<u>{}</u>"
                    if tag:
                        rep = tag.format(rep)
            newstr = sub(escape(match.group(0)), rep, newstr)
    if newstr != event.text:
        await event.edit(newstr, parse_mode="html")
