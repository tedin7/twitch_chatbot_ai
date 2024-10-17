import uvicorn
from api import app
from twitch_bot import Bot
import asyncio
import gc

async def run_bot():
    bot = Bot()
    await bot.start()

def run_api(port=8000):
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")

async def periodic_gc():
    while True:
        await asyncio.sleep(300)  # Run every 5 minutes
        gc.collect()

async def main():
    api_task = asyncio.create_task(asyncio.to_thread(run_api))
    bot_task = asyncio.create_task(run_bot())
    gc_task = asyncio.create_task(periodic_gc())
    await asyncio.gather(api_task, bot_task, gc_task)

if __name__ == "__main__":
    asyncio.run(main())
