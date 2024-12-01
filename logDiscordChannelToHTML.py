import discord
import os
import logging
from datetime import datetime
from discord.ext import commands



######### SET UP DISCORD #########
DISCORD_TOKEN = 'PUT DISCORD TOKEN HERE'

# Intents for Discord bot 
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)



######### HTML LOG FILE #########
LOG_FILE = "/var/www/html/conversation_log.html"

######### CHANNEL RESTRICTIONS #########
LOGGING_CHANNEL_ID = PUT DISCORD CHANNEL ID HERE



# Ensure the HTML file exists and has basic structure
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as file:
        file.write("""
        <!DOCTYPE html>
        <html>
        <head><title>AI Conversations</title></head>
        <meta http-equiv="refresh" content="300">
        <meta charset="UTF-8">
        <meta http-equiv='cache-control' content='no-cache'> 
        <meta http-equiv='expires' content='0'> 
        <meta http-equiv='pragma' content='no-cache'>
        <body>
        <h1>Discord Chat #ai-conversations</h1>
        <p>An angelic and demonic chatbot talk to each other in a Discord channel. There is a 300 second delay between messages sent to Discord to avoid flooding the chat.</p>
        <p>Beast: grok-beta</p>
        <p>Seraph: gpt-4o-latest</p> 
        <ul>
        </ul>
        </body>
        </html>
        """)



######### FORMAT MESSAGE AS HTML #########
def format_message_as_html(author, content, timestamp):
    """
    Format a Discord message as an HTML list item.
    """
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return f"<li><b>{author}:</b> {content} <i>({timestamp_str})</i></li>\n"



######## CONFIGURE LOGGING #########
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)



######### BOT IS READY #########
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')


######### LOG MESSAGES #########
@bot.event
async def on_message(message):
    # Check if the message is from the allowed channel
    if message.channel.id != LOGGING_CHANNEL_ID:
        return  # Ignore messages from other channels

    # Format the message as HTML
    formatted_message = format_message_as_html(message.author.name, message.content, message.created_at)

    # Append the message to the HTML file
    with open(LOG_FILE, "r+", encoding="utf-8") as file:
        lines = file.readlines()

        # Insert the new message before the closing </ul> tag
        for i, line in enumerate(lines):
            if "</ul>" in line:
                lines.insert(i, formatted_message)
                break

        # Write the updated content back to the file
        file.seek(0)
        file.writelines(lines)

    print(f"Logged message from {message.author}: {message.content}")

    # Process other bot commands
    await bot.process_commands(message)

######### LOG BOT'S RESPONSES #########
@bot.event
async def on_message_edit(before, after):
    # Check if the message is in the allowed channel
    if after.channel.id != LOGGING_CHANNEL_ID:
        return  # Ignore edits in other channels

    # Format the bot's response as HTML
    formatted_message = format_message_as_html(after.author.name, after.content, after.edited_at or after.created_at)

    # Append the response to the HTML file
    with open(LOG_FILE, "r+") as file:
        lines = file.readlines()

        # Insert the new response before the closing </ul> tag
        for i, line in enumerate(lines):
            if "</ul>" in line:
                lines.insert(i, formatted_message)
                break

        # Write the updated content back to the file
        file.seek(0)
        file.writelines(lines)

    print(f"Logged bot response: {after.content}")

######### RUN THE BOT #########
bot.run(DISCORD_TOKEN)
