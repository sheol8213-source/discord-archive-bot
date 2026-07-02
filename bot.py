import os
import re
from datetime import datetime, timezone

import discord
from discord.ext import tasks

# ---------- SETTINGS ----------

# Read from Render's Environment Variables (set these in the Render dashboard)
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# Folder that holds your category subfolders
DATA_DIR = "data"

# Must match your actual folder names exactly (capitalization matters!)
CATEGORIES = ["Divine", "capricious", "malevolent", "neutral"]

# Hour of the day (UTC) that the bot should post. 12 = noon UTC.
POST_HOUR_UTC = 12

# The date we start counting "day 0" from. Don't change this once you've
# deployed, or your pairing sequence will jump around.
START_DATE = datetime(2026, 1, 1, tzinfo=timezone.utc).date()

# ---------- BOT SETUP ----------

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Keeps track of the last date we posted, so we don't post twice in one day
last_posted_date = None


def get_sorted_images(category):
    """Return all image files in a category folder, sorted by the number in their filename."""
    folder = os.path.join(DATA_DIR, category)
    if not os.path.isdir(folder):
        print(f"WARNING: folder not found: {folder}")
        return []

    files = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    def get_number(filename):
        match = re.search(r"(\d+)", filename)
        return int(match.group(1)) if match else 0

    files.sort(key=get_number)
    return [os.path.join(folder, f) for f in files]


def get_todays_pair(category):
    """Work out which 2 images to post today for this category."""
    images = get_sorted_images(category)
    if len(images) < 2:
        return images  # not enough images to make a pair yet

    num_pairs = len(images) // 2
    day_number = (datetime.now(timezone.utc).date() - START_DATE).days
    pair_index = day_number % num_pairs

    first = images[pair_index * 2]
    second = images[pair_index * 2 + 1]
    return [first, second]


@tasks.loop(minutes=30)
async def check_and_post():
    global last_posted_date

    now = datetime.now(timezone.utc)
    today = now.date()

    # Only post once we hit the target hour, and only once per day
    if now.hour != POST_HOUR_UTC or today == last_posted_date:
        return

    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("ERROR: Could not find channel. Check your CHANNEL_ID env var.")
        return

    for category in CATEGORIES:
        pair = get_todays_pair(category)
        if not pair:
            print(f"No images found for category: {category}")
            continue
        files = [discord.File(path) for path in pair]
        await channel.send(content=f"**{category}**", files=files)

    last_posted_date = today
    print(f"Posted daily images for {today}")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    if not check_and_post.is_running():
        check_and_post.start()


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN environment variable is not set!")
    if CHANNEL_ID == 0:
        raise RuntimeError("CHANNEL_ID environment variable is not set!")
    client.run(TOKEN)
