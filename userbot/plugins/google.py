# @DogeUserBot - < https://t.me/DogeUserBot >
# Copyright (C) 2021 - DOG-E
# All rights reserved.
#
# This file is a part of < https://github.com/DOG-E/DogeUserBot >
# Please read the GNU Affero General Public License in;
# < https://www.github.com/DOG-E/DogeUserBot/blob/DOGE/LICENSE/ >
# ================================================================
from datetime import datetime
from io import BytesIO
from os import path, remove
from re import I, M, findall
from urllib.parse import quote_plus
from urllib.request import build_opener

from bs4 import BeautifulSoup
from PIL import Image
from requests import get, post
from search_engine_parser import BingSearch, GoogleSearch, YahooSearch
from search_engine_parser.core.exceptions import NoResultsOrTrafficError

from . import (
    BOTLOG,
    BOTLOG_CHATID,
    TMP_DOWNLOAD_DIRECTORY,
    deEmojify,
    doge,
    edl,
    eor,
    lan,
    reply_id,
)

plugin_category = "tool"

opener = build_opener()
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
opener.addheaders = [("User-agent", useragent)]


async def ParseSauce(googleurl):
    """Parse/Scrape the HTML code for the info we want."""
    source = opener.open(googleurl).read()
    soup = BeautifulSoup(source, "html.parser")
    results = {"similar_images": "", "best_guess": ""}
    try:
        for similar_image in soup.findAll("input", {"class": "gLFyf"}):
            url = "https://www.google.com/search?tbm=isch&q=" + quote_plus(
                similar_image.get("value")
            )
            results["similar_images"] = url
    except BaseException:
        pass
    for best_guess in soup.findAll("div", attrs={"class": "r5a77d"}):
        results["best_guess"] = best_guess.get_text()
    return results


async def scam(results, lim):
    single = opener.open(results["similar_images"]).read()
    decoded = single.decode("utf-8")
    imglinks = []
    counter = 0
    pattern = r"^,\[\"(.*[.png|.jpg|.jpeg])\",[0-9]+,[0-9]+\]$"
    oboi = findall(pattern, decoded, I | M)
    for imglink in oboi:
        counter += 1
        if counter <= int(lim):
            imglinks.append(imglink)
        else:
            break
    return imglinks


@doge.bot_cmd(
    pattern="gs ([\s\S]*)",
    command=("gs", plugin_category),
    info={
        "header": "Google search command.",
        "flags": {
            ".l": "for number of search results.",
            ".p": "for choosing which page results should be showed.",
        },
        "usage": [
            "{tr}gs <flags> <query>",
            "{tr}gs <query>",
        ],
        "examples": [
            "{tr}gs DogeUserBot",
            "{tr}gs .l6 DogeUserBot",
            "{tr}gs .p2 DogeUserBot",
            "{tr}gs .p2 .l7 DogeUserBot",
        ],
    },
)
async def gsearch(q_event):
    "Google search command."
    dogevent = await eor(q_event, "`Searching...`")
    match = q_event.pattern_match.group(1)
    page = findall(r".p\d+", match)
    lim = findall(r".l\d+", match)
    try:
        page = page[0]
        page = page.replace(".p", "")
        match = match.replace(".p" + page, "")
    except IndexError:
        page = 1
    try:
        lim = lim[0]
        lim = lim.replace(".l", "")
        match = match.replace(".l" + lim, "")
        lim = int(lim)
        if lim <= 0:
            lim = int(5)
    except IndexError:
        lim = 5
    #     smatch = urllib.parse.quote_plus(match)
    smatch = match.replace(" ", "+")
    search_args = (str(smatch), int(page))
    gsearch = GoogleSearch()
    bsearch = BingSearch()
    ysearch = YahooSearch()
    try:
        gresults = await gsearch.async_search(*search_args)
    except NoResultsOrTrafficError:
        try:
            gresults = await bsearch.async_search(*search_args)
        except NoResultsOrTrafficError:
            try:
                gresults = await ysearch.async_search(*search_args)
            except Exception as e:
                return await edl(dogevent, f"**Error:**\n`{str(e)}`")
    msg = ""
    for i in range(lim):
        if i > len(gresults["links"]):
            break
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"👉[{title}]({link})\n`{desc}`\n\n"
        except IndexError:
            break
    await eor(
        dogevent,
        "**Search Query:**\n`" + match + "`\n\n**Results:**\n" + msg,
        link_preview=False,
        aslink=True,
        linktext=f"**The search results for the query **__{match}__ **are:**",
    )
    if BOTLOG:
        await q_event.client.send_message(
            BOTLOG_CHATID,
            "Google Search query `" + match + "` was executed successfully",
        )


@doge.bot_cmd(
    pattern="gis ([\s\S]*)",
    command=("gis", plugin_category),
    info={
        "header": "Google search in image format",
        "usage": "{tr}gis <query>",
        "examples": "{tr}gis doge",
    },
)
async def _(event):
    "To search in google and send result in picture."


@doge.bot_cmd(
    pattern="grs$",
    command=("grs", plugin_category),
    info={
        "header": "Google reverse search command.",
        "description": "reverse search replied image or sticker in google and shows results.",
        "usage": "{tr}grs",
    },
)
async def _(event):
    "Google Reverse Search"
    start = datetime.now()
    OUTPUT_STR = "Reply to an image to do Google Reverse Search"
    if event.reply_to_msg_id:
        dogevent = await eor(event, "Pre Processing Media")
        previous_message = await event.get_reply_message()
        previous_message_text = previous_message.message
        BASE_URL = "http://www.google.com"
        if previous_message.media:
            downloaded_file_name = await event.client.download_media(
                previous_message, TMP_DOWNLOAD_DIRECTORY
            )
            SEARCH_URL = "{}/searchbyimage/upload".format(BASE_URL)
            multipart = {
                "encoded_image": (
                    downloaded_file_name,
                    open(downloaded_file_name, "rb"),
                ),
                "image_content": "",
            }
            # https://stackoverflow.com/a/28792943/4723940
            google_rs_response = post(
                SEARCH_URL, files=multipart, allow_redirects=False
            )
            the_location = google_rs_response.headers.get("Location")
            remove(downloaded_file_name)
        else:
            previous_message_text = previous_message.message
            SEARCH_URL = "{}/searchbyimage?image_url={}"
            request_url = SEARCH_URL.format(BASE_URL, previous_message_text)
            google_rs_response = get(request_url, allow_redirects=False)
            the_location = google_rs_response.headers.get("Location")
        await dogevent.edit("Found Google Result. Pouring some soup on it!")
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
        }
        response = get(the_location, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # document.getElementsByClassName("r5a77d"): PRS
        try:
            prs_div = soup.find_all("div", {"class": "r5a77d"})[0]
            prs_anchor_element = prs_div.find("a")
            prs_url = BASE_URL + prs_anchor_element.get("href")
            prs_text = prs_anchor_element.text
            # document.getElementById("jHnbRc")
            img_size_div = soup.find(id="jHnbRc")
            img_size = img_size_div.find_all("div")
        except Exception:
            return await edl(dogevent, "`Sorry. I am unable to find similar images`")
        end = datetime.now()
        ms = (end - start).seconds
        OUTPUT_STR = """{img_size}
<b>Possible Related Search: </b> <a href="{prs_url}">{prs_text}</a>
<b>More Info: </b> Open this <a href="{the_location}">Link</a>
<i>fetched in {ms} seconds</i>""".format(
            **locals()
        )
    else:
        dogevent = event
    await eor(dogevent, OUTPUT_STR, parse_mode="HTML", link_preview=False)


@doge.bot_cmd(
    pattern="reverse(?:\s|$)([\s\S]*)",
    command=("reverse", plugin_category),
    info={
        "header": "Google reverse search command.",
        "description": "reverse search replied image or sticker in google and shows results. if count is not used then it send 1 image by default.",
        "usage": "{tr}reverse <count>",
    },
)
async def _(img):
    "Google Reverse Search"
    reply_to = await reply_id(img)
    if path.isfile("okgoogle.png"):
        remove("okgoogle.png")
    message = await img.get_reply_message()
    if message and message.media:
        photo = BytesIO()
        await img.client.download_media(message, photo)
    else:
        await eor(img, "`Reply to photo or sticker nigger.`")
        return
    if photo:
        dogevent = await eor(img, lan("processing"))
        try:
            image = Image.open(photo)
        except OSError:
            return await dogevent.edit("`Unsupported, most likely.`")
        name = "okgoogle.png"
        image.save(name, "PNG")
        image.close()
        # https://stackoverflow.com/questions/23270175/google-reverse-image-search-using-post-request#28792943
        searchUrl = "https://www.google.com/searchbyimage/upload"
        multipart = {"encoded_image": (name, open(name, "rb")), "image_content": ""}
        response = post(searchUrl, files=multipart, allow_redirects=False)
        if response != 400:
            await img.edit(
                "`Image successfully uploaded to Google. Maybe.`"
                "\n`Parsing source now. Maybe.`"
            )
        else:
            return await dogevent.edit("`Unable to perform reverse search.`")
        fetchUrl = response.headers["Location"]
        remove(name)
        match = await ParseSauce(fetchUrl + "&preferences?hl=en&fg=1#languages")
        guess = match["best_guess"]
        imgspage = match["similar_images"]
        if guess and imgspage:
            await dogevent.edit(f"[{guess}]({fetchUrl})\n\n`Looking for this Image...`")
        else:
            return await dogevent.edit("`Can't find any kind similar images.`")
        lim = img.pattern_match.group(1) or 3
        images = await scam(match, lim)
        yeet = []
        for i in images:
            k = get(i)
            yeet.append(k.content)
        try:
            await img.client.send_file(
                entity=await img.client.get_input_entity(img.chat_id),
                file=yeet,
                reply_to=reply_to,
            )
        except TypeError:
            pass
        await dogevent.edit(
            f"[{guess}]({fetchUrl})\n\n[Visually similar images]({imgspage})"
        )


@doge.bot_cmd(
    pattern="google(?:\s|$)([\s\S]*)",
    command=("google", plugin_category),
    info={
        "header": "To get link for google search",
        "description": "Will show google search link as button instead of google search results try {tr}gs for google search results.",
        "usage": ["{tr}google query", "{tr}google reply a message"],
    },
)
async def google_search(event):
    "Will show you google search link of the given query."
    input = event.pattern_match.group(1)
    if not input:
        replyinput = await event.get_reply_message()
        input = replyinput.text
    if not input:
        return await edl(event, "__What should I search? Give search query plox.__")
    reply_to_id = await reply_id(event)
    input = deEmojify(input).strip()
    if len(input) > 195 or len(input) < 1:
        return await edl(
            event,
            "__Plox your search query exceeds 200 characters or you search query is empty.__",
        )
    query = "#12" + input
    results = await event.client.inline_query("@StickerizerBot", query)
    await results[0].click(event.chat_id, reply_to=reply_to_id, hide_via=True)
    await event.delete()
