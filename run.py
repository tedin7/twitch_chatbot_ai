import uvicorn
from api import app
from twitch_bot import Bot
import asyncio

async def run_bot():
    bot = Bot()
    await bot.start()

def run_api(port=8000):
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")

async def main():
    api_task = asyncio.create_task(asyncio.to_thread(run_api))
    bot_task = asyncio.create_task(run_bot())
    await asyncio.gather(api_task, bot_task)

if __name__ == "__main__":
    asyncio.run(main())
