from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 1234567  # replace with your API ID
API_HASH = "your_api_hash"  # replace with your API HASH
BOT_TOKEN = "your_bot_token"  # replace with your BOT TOKEN

REQUIRED_CHANNELS = ["@channel1", "@channel2"]  # Replace with your channels
ADMIN_ID = 123456789  # Replace with your Telegram User ID

app = Client("simple_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def check_channels(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await app.get_chat_member(channel, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except Exception:
            return False
    return True

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id

    # 👤 Send Telegram ID to user
    await message.reply(f"👤 Your Telegram ID is: `{user_id}`")

    if await check_channels(user_id):
        await send_main_menu(message)
    else:
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Joined", callback_data="verify")]])
        join_links = "\n".join([f"👉 Join: {c}" for c in REQUIRED_CHANNELS])
        await message.reply(f"🚨 Please join the channels first:\n\n{join_links}", reply_markup=btn)

@app.on_callback_query(filters.regex("verify"))
async def verify(client, callback_query):
    user_id = callback_query.from_user.id
    if await check_channels(user_id):
        await callback_query.message.delete()
        await send_main_menu(callback_query.message)
    else:
        await callback_query.answer("❌ You haven't joined all required channels!", show_alert=True)

async def send_main_menu(message):
    keyboard = [
        [InlineKeyboardButton("📸 Instagram", callback_data="menu_instagram")],
        [InlineKeyboardButton("📘 Facebook", callback_data="menu_facebook")],
        [InlineKeyboardButton("🐦 Twitter", callback_data="menu_twitter")],
        [InlineKeyboardButton("🌐 Website Traffic", callback_data="menu_traffic")],
        [InlineKeyboardButton("📺 YouTube", callback_data="menu_youtube")]
    ]
    await message.reply("✅ You're verified!\nSelect a platform below 👇", reply_markup=InlineKeyboardMarkup(keyboard))

sub_menus = {
    "menu_instagram": ["Followers", "Likes", "Views", "Comments", "Engagement"],
    "menu_facebook": ["Page Likes", "Post Reach", "Shares", "Followers"],
    "menu_twitter": ["Followers", "Retweets", "Likes", "Comments"],
    "menu_traffic": ["Direct", "Organic", "Referral", "Paid Ads"],
    "menu_youtube": ["Subscribers", "Views", "Watch Time", "Likes", "Comments"]
}

@app.on_callback_query()
async def handle_menu(client, callback_query):
    data = callback_query.data
    user = callback_query.from_user

    if data in sub_menus:
        options = sub_menus[data]
        buttons = [[InlineKeyboardButton(opt, callback_data=f"send_{opt.lower()}")] for opt in options]
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
        await callback_query.message.edit_text(f"Select one:\n", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "back":
        await callback_query.message.edit_text("Back to main menu 👇")
        await send_main_menu(callback_query.message)

    elif data.startswith("send_"):
        service = data.split("_")[1].capitalize()
        msg = f"📥 New request from @{user.username or user.first_name} (ID: {user.id})\nSelected: {service}"
        await client.send_message(ADMIN_ID, msg)
        await callback_query.message.edit_text(f"✅ Your request for **{service}** has been sent to the admin.\nYou'll be contacted shortly.")

    else:
        await callback_query.answer("ℹ️ Feature under development")

app.run()
