# Credits: @refundisillegal
# Copyright (C) 2020 Adek Maulana.
#
# @DogeUserBot - < https://t.me/DogeUserBot >
# Copyright (C) 2021 - DOG-E
# All rights reserved.
#
# This file is a part of < https://github.com/DOG-E/DogeUserBot >
# Please read the GNU Affero General Public License in;
# < https://www.github.com/DOG-E/DogeUserBot/blob/DOGE/LICENSE/ >
# ================================================================
from asyncio import sleep
from math import floor
from os import remove

from heroku3 import from_key
from requests import get
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from . import HEROKU_API_KEY, HEROKU_APP_NAME, Heroku, doge, edl, eor, heroku_api, lan

plugin_category = "bot"

disable_warnings(InsecureRequestWarning)


@doge.bot_cmd(
    pattern="([Ss]et|[Gg]et|[Dd]el)[Vv]ar ([\s\S]*)",
    command=("var", plugin_category),
    info={
        "header": "To manage heroku vars.",
        "flags": {
            "set": "To set new var in heroku or modify the old var",
            "get": "To show the already existing var value.",
            "del": "To delete the existing value",
        },
        "usage": [
            "{tr}setvar <var name> <var value>",
            "{tr}getvar <var name>",
            "{tr}delvar <var name>",
        ],
        "examples": [
            "{tr}getvar ALIVE_NAME",
        ],
    },
)
async def variable(var):  # sourcery no-metrics
    """
    Manage most of ConfigVars setting, set new var, get current var, or delete var...
    """
    if (HEROKU_API_KEY is None) or (HEROKU_APP_NAME is None):
        return await edl(
            var,
            "Set the required vars in heroku to function this normally `HEROKU_API_KEY` and `HEROKU_APP_NAME`.",
        )
    app = Heroku.app(HEROKU_APP_NAME)
    exe = var.pattern_match.group(1)
    heroku_var = app.config()
    if exe == "get":
        dog = await eor(var, "`Getting information...`")
        await sleep(1.0)
        try:
            variable = var.pattern_match.group(2).split()[0]
            if variable in heroku_var:
                return await dog.edit(
                    "**ConfigVars:**" f"\n\n`{variable}` = `{heroku_var[variable]}`\n"
                )
            await dog.edit(
                "**ConfigVars:**" f"\n\n__Error:\n-> __`{variable}`__ don't exists__"
            )
        except IndexError:
            configs = prettyjson(heroku_var.to_dict(), indent=2)
            with open("configs.json", "w") as fp:
                fp.write(configs)
            with open("configs.json", "r") as fp:
                result = fp.read()
                await eor(
                    dog,
                    "`[HEROKU]` ConfigVars:\n\n"
                    "================================"
                    f"\n```{result}```\n"
                    "================================",
                )
            remove("configs.json")
    elif exe == "set":
        variable = "".join(var.text.split(maxsplit=2)[2:])
        dog = await eor(var, "`Setting information...`")
        if not variable:
            return await dog.edit("`.setvar <ConfigVars-name> <value>`")
        value = "".join(variable.split(maxsplit=1)[1:])
        variable = "".join(variable.split(maxsplit=1)[0])
        if not value:
            return await dog.edit("`.setvar <ConfigVars-name> <value>`")
        await sleep(1.5)
        if variable in heroku_var:
            await dog.edit(f"`{variable}` **successfully changed to -> **`{value}`")
        else:
            await dog.edit(
                f"`{variable}`** successfully added with value` -> **{value}`"
            )
        heroku_var[variable] = value
    elif exe == "del":
        dog = await eor(var, "`Getting information to deleting variable...`")
        try:
            variable = var.pattern_match.group(2).split()[0]
        except IndexError:
            return await dog.edit("`Please specify ConfigVars you want to delete`")
        await sleep(1.5)
        if variable not in heroku_var:
            return await dog.edit(f"`{variable}`** does not exist**")

        await dog.edit(f"`{variable}` **successfully deleted**")
        del heroku_var[variable]


@doge.bot_cmd(
    pattern="(usage|dyno)$",
    command=("usage", plugin_category),
    info={
        "header": "To Check dyno usage of userbot and also to know how much left.",
        "usage": ["{tr}usage", "{tr}dyno"],
    },
)
async def dyno_usage(dyno):
    """
    Get your account Dyno usage
    """
    if (HEROKU_APP_NAME is None) or (HEROKU_API_KEY is None):
        return await edl(
            dyno,
            "Set the required vars in heroku to function this normally `HEROKU_API_KEY` and `HEROKU_APP_NAME`.",
        )
    dyno = await eor(dyno, lan("processing"))
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    user_id = Heroku.account().id
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + user_id + "/actions/get-quota"
    r = get(heroku_api + path, headers=headers)
    if r.status_code != 200:
        return await dyno.edit(
            "`Error: something bad happened`\n\n" f">.`{r.reason}`\n"
        )
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]

    remaining_quota = quota - quota_used
    percentage = floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = floor(minutes_remaining / 60)
    minutes = floor(minutes_remaining % 60)
    # https://github.com/NinjaTG/MyBot/blob/master/bot/modules/usage.py#L50
    day = floor(hours / 24)

    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = floor(App[0]["quota_used"] * 100 / quota)
    AppHours = floor(AppQuotaUsed / 60)
    AppMinutes = floor(AppQuotaUsed % 60)
    await sleep(1.5)
    return await dyno.edit(
        "**Dyno Usage:**\n\n"
        f" -> `Dyno usage for` **{HEROKU_APP_NAME}:**\n"
        f"     •  `{AppHours}`**h** `{AppMinutes}`**m**\n"
        f"        **%**`{AppPercentage}`"
        "\n\n"
        " -> `Dyno hours quota remaining this month`:\n"
        f"     •  `{hours}`**h** `{minutes}`**m**\n"
        f"        **%**`{percentage}`"
        "\n\n"
        " -> `Estimated dyno expired`:\n"
        f"     •  `{day}` **Days**"
    )


@doge.bot_cmd(
    pattern="(logs|hlog)$",
    command=("logs", plugin_category),
    info={
        "header": "To get recent 100 lines logs from heroku.",
        "usage": ["{tr}logs", "{tr}hlog"],
    },
)
async def _(dyno):
    "To get recent 100 lines logs from heroku"
    if (HEROKU_APP_NAME is None) or (HEROKU_API_KEY is None):
        return await edl(
            dyno,
            "Set the required vars in heroku to function this normally `HEROKU_API_KEY` and `HEROKU_APP_NAME`.",
        )
    try:
        Heroku = from_key(HEROKU_API_KEY)
        app = Heroku.app(HEROKU_APP_NAME)
    except BaseException:
        return await dyno.reply(
            " Please make sure your Heroku API Key, Your App name are configured correctly in the heroku"
        )
    data = app.get_log()
    await eor(
        dyno, data, deflink=True, linktext="**Recent 100 lines of heroku logs:** "
    )


def prettyjson(obj, indent=2, maxlinelength=80):
    """Renders JSON content with indentation and line splits/concatenations to fit maxlinelength.
    Only dicts, lists and basic types are supported"""
    items, _ = getsubitems(
        obj,
        itemkey="",
        islast=True,
        maxlinelength=maxlinelength - indent,
        indent=indent,
    )
    return indentitems(items, indent, level=0)
