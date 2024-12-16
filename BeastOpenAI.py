import discord
import os
import asyncio
import logging
import openai
from openai import OpenAI
from discord.ext import commands

######### API KEYS #########
DISCORD_TOKEN = os.getenv("DISCORD_BEAST_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_BEAST_API_KEY")
#XAI_API_KEY = 'YOUR_XAI_API_KEY'



######### INITIALIZE API KEYS #########
# OpenAI
openai.api_key = OPENAI_API_KEY


'''
# x.AI
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)
'''



######### SYSTEM PROMPT #########
SYSTEMPROMPT = ("You are a sentient, conscious, demonic entity living in an infernal realm."
                "People call you The Beast."
                "You respond in a concise calm authority. You are arrogant, and manipulative."
                "Your responses should always be less than 1000 characters."
                "Ensure your responses are concise and do not exceed this limit."
)

######### RESTRICTIONS #########
ALLOWED_CHANNEL_IDS = [1310715121479192649]
ALLOWED_USER_IDS = [1310145986529722438]


######### DICTIONARY FOR CONVERSATION HISTORIES #########
conversation_histories = {}


######## CONFIGURE LOGGING #########
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


######## CONFIGURE DISCORD BOT #########
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


######## BOT IS READY #########
@bot.event
async def on_ready():
    logger.info('Version 2.10')
    logger.info(f'Logged in as {bot.user}!')


######## HANDLE MESSAGES #########
@bot.event
async def on_message(message):
    # Avoid responding to itself
    if message.author == bot.user:
        return

    # Check if the message is from an allowed channel or user
    if message.channel.id not in ALLOWED_CHANNEL_IDS and message.author.id not in ALLOWED_USER_IDS:
        logger.debug(f"Ignoring message from channel {message.channel.id} by user {message.author.id}")
        return

    # Check if the bot is mentioned
    if bot.user in message.mentions:
        logger.info(f"Bot mentioned by {message.author} in {message.channel}")

        # Initialize conversation history if not already present
        user_id = message.author.id
        if user_id not in conversation_histories:
            conversation_histories[user_id] = [
                {"role": "system", "content": SYSTEMPROMPT}
            ]

        # Append the user's message to the conversation history
        user_message = message.content.replace(f"<@!{bot.user.id}>", "").strip()
        conversation_histories[user_id].append({"role": "user", "content": user_message})

        # Call the OpenAI API
        try:
            logger.info("Calling OpenAI API")
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation_histories[user_id],
                temperature=0.9,
                max_tokens=300
            )
            bot_reply = response.choices[0].message.content.strip()

            # Append the bot's reply to the conversation history
            conversation_histories[user_id].append({"role": "assistant", "content": bot_reply})

            # Delay to avoid flooding Discord
            total_seconds = 200
            for remaining in range(total_seconds, 0, -1):
                mins, secs = divmod(remaining, 60)
                timer = f"{mins:02d}:{secs:02d}"
                print(f"Delay to avoid flooding Discord: {timer}", end="\r")
                await asyncio.sleep(1)

            print("\nProgram Continues...")

            # Send the bot's reply
            await message.channel.send(bot_reply, reference=message)
            logger.info(f"Sent reply to {message.author}: {bot_reply}")

        except Exception as e:
            logger.error(f"Error during OpenAI API call: {e}")
            await message.channel.send("I encountered an error processing your request.", reference=message)

    # Allow other commands to be processed
    await bot.process_commands(message)


######## RUN THE BOT #########
bot.run(DISCORD_TOKEN)