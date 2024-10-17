from twitchio.ext import commands
from config import TWITCH_TOKEN, TWITCH_CHANNEL, MODEL_PATH, BOT_NICK
from llm_handler import LLMHandler
import logging
import asyncio
import aiohttp
import re

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix='!', initial_channels=[TWITCH_CHANNEL])
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.WARNING)  # Only log warnings and errors
        self.llm_handler = None
        self.request_queue = asyncio.Queue()
        self.bot_nick = BOT_NICK
        self.last_response = {}  # Store the last response for each user

    async def event_ready(self):
        self.logger.info(f'Logged in as | {self.nick}')
        self.llm_handler = LLMHandler(model_path=MODEL_PATH)
        self.loop.create_task(self.process_requests())

    async def event_message(self, message):
        if message.echo:
            return

        if message.content.startswith(self._prefix):
            await self.handle_commands(message)
        elif self.is_reply_to_bot(message):
            await self.handle_conversation(message, is_reply=True)
        elif not message.content.startswith('@'):
            await self.handle_conversation(message)

    def is_reply_to_bot(self, message):
        # Check if the message is a reply to the bot's last response
        return message.content.lower().startswith(f"@{self.bot_nick.lower()}")

    async def handle_conversation(self, message, is_reply=False):
        user = message.author.name
        content = message.content

        if is_reply:
            # Remove the @bot_name from the beginning of the message
            content = re.sub(f"^@{self.bot_nick}\s*", "", content, flags=re.IGNORECASE)

        # If it's a reply and we have a last response, use it as context
        if is_reply and user in self.last_response:
            context = self.last_response[user]
            prompt = f"Previous response: {context}\nUser: {content}"
        else:
            prompt = content

        await self.request_queue.put((prompt, message, user))

    async def process_requests(self):
        async with aiohttp.ClientSession() as session:
            while True:
                batch = []
                while len(batch) < 5:  # Process up to 5 requests at a time
                    try:
                        request = await asyncio.wait_for(self.request_queue.get(), timeout=0.1)
                        batch.append(request)
                    except asyncio.TimeoutError:
                        break

                if batch:
                    responses = await asyncio.gather(*[self.generate_response(session, prompt, user) for prompt, ctx, user in batch])
                    for (_, ctx, user), response in zip(batch, responses):
                        await self.send_message(ctx.channel.name, f"@{user} {response}")
                        self.last_response[user] = response  # Store the last response for each user

                await asyncio.sleep(0.1)  # Small delay to prevent CPU overuse

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
