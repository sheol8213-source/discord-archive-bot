
import os, re
import discord

TOKEN=os.getenv("DISCORD_TOKEN")
CHANNEL_ID=int(os.getenv("CHANNEL_ID","0"))
DATA_DIR="data"
CATEGORIES=["Divine","capricious","malevolent","neutral"]
STATE_FILE="state.txt"

intents=discord.Intents.default()
client=discord.Client(intents=intents)

def imgs(cat):
    p=os.path.join(DATA_DIR,cat)
    if not os.path.isdir(p): return []
    fs=[f for f in os.listdir(p) if f.lower().endswith((".png",".jpg",".jpeg"))]
    fs.sort(key=lambda x:int(re.search(r"(\d+)",x).group(1)) if re.search(r"(\d+)",x) else 0)
    return [os.path.join(p,f) for f in fs]

def load():
    d={}
    if os.path.exists(STATE_FILE):
        for line in open(STATE_FILE,encoding="utf8"):
            if "=" in line:
                k,v=line.strip().split("=")
                d[k]=int(v)
    return d

def save(d):
    with open(STATE_FILE,"w",encoding="utf8") as f:
        for k,v in d.items(): f.write(f"{k}={v}\n")

@client.event
async def on_ready():
    ch=client.get_channel(CHANNEL_ID)
    st=load()
    for c in CATEGORIES:
        im=imgs(c)
        i=st.get(c,0)
        if i>=len(im): i=0
        pair=im[i:i+2]
        if len(pair)==1: pair=[pair[0],im[0]]
        if pair:
            await ch.send(content=f"**{c}**",files=[discord.File(x) for x in pair])
            st[c]=(i+2)%len(im)
    save(st)
    await client.close()

client.run(TOKEN)
