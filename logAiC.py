import discord
import os
import logging
from datetime import datetime
from discord.ext import commands
import re

######### API KEYS #########
DISCORD_TOKEN = os.getenv("DISCORD_BEAST_TOKEN")

######### RESTRICTIONS #########
LOGGING_CHANNEL_ID = 1310715121479192649

######### CONFIGURE DISCORD #########
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

######### HTML LOG FILE #########
LOG_FILE = "/var/www/html/AiC/conversation_log.html"

# Rename and backup existing log file
def backup_existing_log():
    if os.path.exists(LOG_FILE):
        # Generate timestamped backup file name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = f"/var/www/html/AiC/conversation_log_{timestamp}.html"
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
        <ul>
        </ul>
        </body>
        </html>
        """)


######### FORMAT MESSAGE AS HTML #########
def format_discord_message(content):
    """
    Convert Discord Markdown to HTML.
    """
    # Convert Markdown to HTML
    content = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", content)  # Bold
    content = re.sub(r"__(.+?)__", r"<u>\1</u>", content)      # Underline
    content = re.sub(r"\*(.+?)\*", r"<i>\1</i>", content)      # Italics
    content = re.sub(r"~~(.+?)~~", r"<s>\1</s>", content)      # Strikethrough
    content = re.sub(r"`(.+?)`", r"<code>\1</code>", content)  # Inline code

    # Replace custom emojis
    content = re.sub(r"<:(.+?):\d+>", r"\1", content)

    # Preserve new lines as <br> tags
    content = content.replace("\n", "<br>")
    
    return content

def format_message_as_html(author, content, timestamp):
    
    # Format a Discord message as an HTML list item.
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return f"<li><b>{author}:</b> {content} <i>({timestamp_str})</i></li>\n"

######### CONFIGURE LOGGING #########
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

######### BOT IS READY #########
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    logger.info('Version 2.9')

######### LOG MESSAGES #########
@bot.event
async def on_message(message):
    # Check if message is from allowed channel
    if message.channel.id != LOGGING_CHANNEL_ID:
        return  # Ignore messages from other channels

    # Use display_name to log user's display name
    display_name = message.author.display_name

    # Replace mentions with display names
    content = message.content
    for user in message.mentions:
        mention_str = f"<@{user.id}>"
        content = content.replace(mention_str, f"@{user.display_name}")

    # Convert Markdown to HTML
    content = format_discord_message(content)

    # Add attachments to content
    if message.attachments:
        for attachment in message.attachments:
            content += f'<br><a href="{attachment.url}">[Attachment: {attachment.filename}]</a>'

    # Format message as HTML
    formatted_message = format_message_as_html(display_name, content, message.created_at)

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

######### RUN THE BOT #########
bot.run(DISCORD_TOKEN)