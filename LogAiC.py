import discord
import os
import logging
from datetime import datetime
from discord.ext import commands



######### API KEYS #########
DISCORD_TOKEN = os.getenv("DISCORD_BEAST_TOKEN")



######### INTENTS FOR DISCORD BOT #########
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)



######### HTML LOG FILE #########
LOG_FILE = "/var/www/html/AiC/conversation_log.html"



######### RENAME EXISTING LOG FILE #########
def backup_existing_log():
    if os.path.exists(LOG_FILE):
        
        # Generate timestamped backup file name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = f"/var/www/html/AiC/conversation_log_{timestamp}.html"
        
        # Rename the file
        os.rename(LOG_FILE, backup_file)
        print(f"Existing log file renamed to {backup_file}")
    else:
        print(f"No existing log file found at {LOG_FILE}")

# Run the backup function once at the start of script
backup_existing_log()



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
        <p>An angelic and demonic chatbot talk to each other in a Discord channel. There is a 300 second delay between messages sent to Discord to avoid flooding the channel.</p>
        <p>Beast: grok-beta</p>
        <p>Seraph: chatgpt-4o-latest</p> 
        <ul>
        </ul>
        </body>
        </html>
        """)



######### CHANNEL RESTRICTIONS #########
LOGGING_CHANNEL_ID = 1310715121479192649



######### FORMAT MESSAGE AS HTML #########
def format_message_as_html(author, content, timestamp):
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return f"<li><b>{author}:</b> {content} <i>({timestamp_str})</i></li>\n"



######### CONFIGURE LOGGING #########
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)



######### BOT IS READY #########
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    logger.info('Version 2.7')



######### LOG MESSAGES #########
@bot.event
async def on_message(message):
    
    # Check if message is from allowed channel
    if message.channel.id != LOGGING_CHANNEL_ID:
        return  # Ignore messages from other channels

    # Use display_name to log user's display name
    display_name = message.author.display_name

    # Format message as HTML
    formatted_message = format_message_as_html(display_name, message.content, message.created_at)

    # Append message to HTML file
    with open(LOG_FILE, "r+", encoding="utf-8") as file:
        lines = file.readlines()

        # Insert new message before closing </ul>
        for i, line in enumerate(lines):
            if "</ul>" in line:
                lines.insert(i, formatted_message)
                break

        # Write updated content to the file
        file.seek(0)
        file.writelines(lines)

    print(f"Logged message from {display_name}: {message.content}")

    # Process other bot commands
    await bot.process_commands(message)



######### LOG BOT'S RESPONSES #########
@bot.event
async def on_message_edit(before, after):
    
    # Check if the message is in the allowed channel
    if after.channel.id != LOGGING_CHANNEL_ID:
        return

    # Use display_name for bot's display name
    display_name = after.author.display_name

    # Format bot's response as HTML
    formatted_message = format_message_as_html(display_name, after.content, after.edited_at or after.created_at)

    # Append response to HTML file
    with open(LOG_FILE, "r+") as file:
        lines = file.readlines()

        # Insert new response before closing </ul>
        for i, line in enumerate(lines):
            if "</ul>" in line:
                lines.insert(i, formatted_message)
                break

        # Write updated content back to file
        file.seek(0)
        file.writelines(lines)

    print(f"Logged bot response: {after.content}")



######### RUN THE BOT #########
bot.run(DISCORD_TOKEN)