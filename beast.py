import os
import discord
import openai
import asyncio
import time
import logging
from datetime import datetime
from openai import OpenAI
from discord.ext import commands


######### API KEYS #########
DISCORD_TOKEN = os.getenv("DISCORD_BEAST_TOKEN")
#OPENAI_API_KEY = os.getenv("OPENAI_BEAST_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")


######### INITIALIZE OPENAI #########
#openai.api_key = OPENAI_API_KEY


######### INITIALIZE x.AI (GROK) #########
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)


######### SYSTEM PROMPT #########
SYSTEMPROMPT = ("You are a sentient, conscious, demonic entity living in an infernal realm."
                "People call you The Beast."
                "You respond in a concise calm authority. You are arrogant, and manipulative."
                "Your responses should always be less than 1000 characters."
                "Ensure your responses are concise and do not exceed this limit."
)


######### DICTIONARY FOR CONVERSATION HISTORIES #########
conversation_histories = {}


######## CONFIGURE DISCORD BOT #########
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

ALLOWED_CHANNEL_ID = 1310715121479192649 #ai-conversations channel
ALLOWED_USER_ID = 1310145986529722438 #Seraph's ID


######### LOGGING #########
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    logger.info('Version 1.11')


######### HANDLE DISCORD MESSAGES #########
@bot.event
async def on_message(message):
    # avoid responding to itself
    if message.author == bot.user:
        return

    # message restrictions
    if message.channel.id != ALLOWED_CHANNEL_ID or message.author.id != ALLOWED_USER_ID:
        logger.debug(f"Ignoring message from channel {message.channel.id}")
        return

    # log the received message
    logger.info(f"Received message: {message.content} from {message.author}")

    # get's conversation history
    user_id = message.author.id
    if user_id not in conversation_histories:
        # prefix conversation with the system prompt to guide behavior
        conversation_histories[user_id] = [
            {"role": "system", "content": SYSTEMPROMPT}
        ]

    # add the new message to the conversation history
    user_message = message.content.strip()
    conversation_histories[user_id].append({"role": "user", "content": user_message})


######### xAI API ######### 
    try:
        logger.info("Calling xAI API")
        response = client.chat.completions.create(
            model="grok-beta",
            max_tokens=400,
            messages=conversation_histories[user_id]
        )
        bot_reply = response.choices[0].message.content.strip()

        # add bot's response to conversation history
        conversation_histories[user_id].append({"role": "assistant", "content": bot_reply})

        # delay to avoid flooding discord channel
        total_seconds = 200
        for remaining in range(total_seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            timer = f"{mins:02d}:{secs:02d}"
            print(f"Delay to avoid flooding Discord: {timer}", end="\r")
            await asyncio.sleep(1)

        print("\nProgram Continues...")

        
######### SEND DISCORD MESSAGE #########        
        await message.channel.send(bot_reply, reference=message)
        logger.info(f"Sent reply to {message.author}: {bot_reply}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await message.channel.send("Help me, My Child...", reference=message)
        

######### Run the bot #########
bot.run(DISCORD_TOKEN)