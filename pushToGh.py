import os
import subprocess
import time
import shutil
import logging


######### DEFINE FILE PATHS #########
LOG_FILE = "/var/www/html/AiC/conversation_log.html"
SOURCE_DIR = "/var/www/html/AiC/"
DEST_LOG_FILE = "/home/ri9z/AI-Conversations/index.html"
DEST_DIR= "/home/ri9z/AI-Conversations/chatlogs/conversation_log.html"
REPO_DIR = "/home/ri9z/AI-Conversations"



######### COPY FILES FROM HTML DIR TO GITHUB REPO DIR #########

# Copies current realtime log to index.html in gh repo directory
def copy_current():
    try:
        print(f"Copying {LOG_FILE} to {DEST_LOG_FILE}")
        shutil.copy(LOG_FILE, DEST_LOG_FILE)
        print("File copied successfully.")
    except FileNotFoundError:
        print(f"Error: {LOG_FILE} not found. Skipping copy.")
    except Exception as e:
        print(f"Error copying file: {e}")

# Copies historic logs to chatlogs dir in gh repo
def copy_history():
    try:
        # Ensure destination dir exists
        if not os.path.exists(DEST_DIR):
            os.makedirs(DEST_DIR)
            print(f"Created destination directory: {DEST_DIR}")

        # Copy files from source
        for item in os.listdir(SOURCE_DIR):
            source_path = os.path.join(SOURCE_DIR, item)
            dest_path = os.path.join(DEST_DIR, item)

            if os.path.isfile(source_path):  # Copy files only
                shutil.copy2(source_path, dest_path)
                print(f"Copied: {source_path} -> {dest_path}")
            else:
                print(f"Skipping directory: {source_path}")
    except Exception as e:
        print(f"Error copying files: {e}")


######### GITHUB #########
def setup_git_identity():
    
    # Confirm git user identity is configured.
    try:
        # Check user.name, user.email
        name = subprocess.run(['git', 'config', 'user.name'], cwd=REPO_DIR, capture_output=True, text=True).stdout.strip()
        email = subprocess.run(['git', 'config', 'user.email'], cwd=REPO_DIR, capture_output=True, text=True).stdout.strip()

        if not name or not email:
            print("Git identity not set. Configuring now...")
            subprocess.run(['git', 'config', '--local', 'user.name', 'Your Name'], cwd=REPO_DIR, check=True)
            subprocess.run(['git', 'config', '--local', 'user.email', 'your_email@example.com'], cwd=REPO_DIR, check=True)
            print("Git identity configured successfully.")
        else:
            print(f"Git identity already set: {name} <{email}>")
    except Exception as e:
        print(f"Error setting Git identity: {e}")

def push_to_github():
    try:
        # Change to the repository directory
        os.chdir(REPO_DIR)
        print(f"Changed directory to {REPO_DIR}")

        # Set up Git identity if not configured
        setup_git_identity()

        # Check the status of the repository
        print("Checking repository status...")
        subprocess.run(["git", "status"], check=True)

        # Add all changes to the staging area
        print("Adding changes to staging...")
        subprocess.run(["git", "add", "."], check=True)

        # Commit the changes with a default message
        commit_message = "chat transcript updates"
        print(f"Committing changes with message: {commit_message}")
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push the changes to GitHub
        print("Pushing changes to GitHub...")
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)  # Explicitly specify the remote and branch
        print("Changes pushed successfully.")

    except subprocess.CalledProcessError as e:
        if "403" in str(e):
            print("Error: Permission denied. Check your GitHub credentials.")
        else:
            print(f"Error during GitHub operation: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

######### LOOP #########
if __name__ == "__main__":
    while True:
        print("\n--- Running GitHub Sync Script ---")
        
        copy_current()

        copy_history()

        # Push updates to gh
        push_to_github()
        
        '''#wait 300 seconds because the the bots have a delay on their posts to avoid flooding the chat so the posts can actually be read
        might as well put the same delay here. no reason to pointless contact github'''
        delay_seconds = 300  # 5 minutes
        print("Waiting 300 seconds since the bots have a delay to avoid flooding")
        for remaining in range(delay_seconds, 0, -1):
            mins, secs = divmod(remaining, 60)
            timer = f"{mins:02d}:{secs:02d}"
            print(f"Time left: {timer}", end="\r", flush=True)
            time.sleep(1)
        
        print("\nThe program will continue...\n")