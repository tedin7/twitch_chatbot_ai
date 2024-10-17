import uvicorn
from api import app as api_app
from twitch_bot import Bot
from web_interface import app as web_app
import asyncio
import gc
import threading
from channel_manager import get_channels

async def run_bot():
    bot = Bot()
    channels = get_channels()
    for channel in channels:
        await bot.join_channel(channel)
    await bot.start()

def run_api(port=8000):
    uvicorn.run(api_app, host="0.0.0.0", port=port, log_level="error")

def run_web_interface():
    web_app.run(host="0.0.0.0", port=5000)

async def periodic_gc():
    while True:
        await asyncio.sleep(300)  # Run every 5 minutes
        gc.collect()

async def main():
    api_task = asyncio.create_task(asyncio.to_thread(run_api))
    bot_task = asyncio.create_task(run_bot())
    gc_task = asyncio.create_task(periodic_gc())
    web_thread = threading.Thread(target=run_web_interface)
    web_thread.start()
    await asyncio.gather(api_task, bot_task, gc_task)

if __name__ == "__main__":
    asyncio.run(main())
