from twitchio.ext import commands
from config import TWITCH_TOKEN, TWITCH_CHANNEL, MODEL_PATH, BOT_NICK
from llm_handler import LLMHandler
import logging
import asyncio
import aiohttp

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix='!', initial_channels=[TWITCH_CHANNEL])
        self.logger = logging.getLogger(__name__)
        self.llm_handler = None
        self.request_queue = asyncio.Queue()
        self.bot_nick = BOT_NICK

    async def event_ready(self):
        self.logger.info(f'Logged in as | {self.nick}')
        self.llm_handler = LLMHandler(model_path=MODEL_PATH)
        self.loop.create_task(self.process_requests())

    async def event_message(self, message):
        if message.echo:
            return

        if message.content.startswith(self._prefix):
            await self.handle_commands(message)
        elif not message.content.startswith('@'):
            await self.handle_conversation(message)

    async def handle_conversation(self, message):
        await self.request_queue.put((message.content, message, message.author.name))

    async def process_requests(self):
        async with aiohttp.ClientSession() as session:
            while True:
                prompt, ctx, user = await self.request_queue.get()
                response = await self.generate_response(session, prompt, user)
                await self.send_message(ctx.channel.name, f"@{user} {response}")

    async def generate_response(self, session, prompt, user):
        url = "http://localhost:8000/generate"
        try:
            async with session.post(url, json={"prompt": prompt, "user": user}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["response"]
                else:
                    self.logger.error(f"API request failed with status {resp.status}")
                    return "Sorry, I couldn't generate a response at this time."
        except Exception as e:
            self.logger.error(f"Error in generate_response: {str(e)}")
            return "An error occurred while generating the response."

    async def send_message(self, channel, message):
        chunks = [message[i:i+500] for i in range(0, len(message), 500)]
        for chunk in chunks:
            await self.get_channel(channel).send(chunk)

    @commands.command(name='ai')
    async def ai_command(self, ctx):
        prompt = ctx.message.content[4:].strip()
        if not prompt:
            await ctx.send("Please provide a prompt after the !ai command.")
            return
        await self.request_queue.put((prompt, ctx, ctx.author.name))

    @commands.command(name='aiinfo')
    async def aiinfo_command(self, ctx):
        model_info = self.llm_handler.get_model_info()
        await ctx.send(f"AI Model: {model_info['model_name']} | Device: {model_info['device']} | Parameters: {model_info['model_parameters']}")
