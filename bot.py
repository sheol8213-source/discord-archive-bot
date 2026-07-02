import os
import json
from pathlib import Path
import discord

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

DATA_DIR = Path("data")
STATE_FILE = Path("state.txt")

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def load_state():
    if not STATE_FILE.exists():
        return {}

    state = {}

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                state[k] = int(v)

    return state


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        for k, v in state.items():
            f.write(f"{k}={v}\n")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("Channel not found")
        await client.close()
        return

    state = load_state()

    for category in sorted(DATA_DIR.iterdir()):
        if not category.is_dir():
            continue

        images = sorted(
            [
                str(x)
                for x in category.iterdir()
                if x.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]
            ]
        )

        if not images:
            continue

        current_index = state.get(category.name, 0)

        # Category finished, skip it.
        if current_index >= len(images):
            continue

        pair = images[current_index:current_index + 2]

        files = [discord.File(img) for img in pair]

        await channel.send(
            content=f"**{category.name}**",
            files=files
        )

        state[category.name] = current_index + len(pair)

    save_state(state)

    await client.close()


client.run(TOKEN)
