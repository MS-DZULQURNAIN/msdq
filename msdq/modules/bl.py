import asyncio

from telethon import events
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin
from telethon.tl.types import ChannelParticipantCreator

from msdq import client

spam_chats = []


@client.on(events.NewMessage(pattern="^/bl|/addblacklist ?(.*)"))
async def mentionall(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.respond("Perintah ini dapat digunakan dalam grup")

    is_admin = False
    try:
        partici_ = await client(GetParticipantRequest(
            event.chat_id,
            event.sender_id
        ))
    except UserNotParticipantError:
        is_admin = False
    else:
        if (
                isinstance(
                    partici_.participant,
                    (
                            ChannelParticipantAdmin,
                            ChannelParticipantCreator
                    )
                )
        ):
            is_admin = True
    if not is_admin:
        return await event.reply("__Hanya admin yang bisa blacklist!__")

    if event.pattern_match.group(1) and event.is_reply:
        return await event.reply("__Beri aku satu argumen!__")
    elif event.pattern_match.group(1):
        mode = "text_on_cmd"
        msg = event.pattern_match.group(1)
    elif event.is_reply:
        mode = "text_on_reply"
        msg = await event.get_reply_message()
    else:
        return await event.reply("balas pesan atau /addblacklist <pesan>")

    spam_chats.append(chat_id)
    usrnum = 0
    usrtxt = ''
    async for usr in client.iter_participants(chat_id):
        if not chat_id in spam_chats:
            break
        usrnum += 1
        usrtxt += f"👤 [{usr.first_name}](tg://user?id={usr.id})\n"
        if usrnum == 5:
            if mode == "text_on_cmd":
                txt = f"{msg}\n\n{usrtxt}"
                await client.send_message(chat_id, txt)
            elif mode == "text_on_reply":
                await msg.reply(usrtxt)
            await asyncio.sleep(2)
            usrnum = 0
            usrtxt = ''
    try:
        spam_chats.remove(chat_id)
    except:
        pass


@client.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
    is_admin = False
    try:
        partici_ = await client(GetParticipantRequest(
            event.chat_id,
            event.sender_id
        ))
    except UserNotParticipantError:
        is_admin = False
    else:
        if (
                isinstance(
                    partici_.participant,
                    (
                            ChannelParticipantAdmin,
                            ChannelParticipantCreator
                    )
                )
        ):
            is_admin = True
    if not is_admin:
        return await event.reply("__Hanya admin yang dapat menjalankan perintah ini!__")
    if not event.chat_id in spam_chats:
        return await event.reply("__Tidak ada proses berjalan...__")
    else:
        try:
            spam_chats.remove(event.chat_id)
        except:
            pass
        return await event.respond("__Dihentikan...__")


__mod_name__ = "BL"
__help__ = """
──「 Mention all func 」──

MSDQ-ROBOT Can Be a Mention Bot for your group.

Only admins can tag all.  here is a list of commands

× /all (reply to message or add another message) To mention all members in your group, without exception.
× /cancel for canceling the mention-all.
"""
