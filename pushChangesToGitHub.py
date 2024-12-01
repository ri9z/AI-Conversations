import os
import subprocess
import time
import shutil

# Paths for the log file and repository
LOG_FILE = "/var/www/html/conversation_log.html"
DEST_FILE = "/home/ri9z/AI-Conversations/index.html"
REPO_DIR = "/home/ri9z/AI-Conversations"

def copy_log_file():
    
    # Copy conversation_log.html to index.html in the repo directory.
    
    try:
        print(f"Copying {LOG_FILE} to {DEST_FILE}")
        shutil.copy(LOG_FILE, DEST_FILE)
        print("File copied successfully.")
    except FileNotFoundError:
        print(f"Error: {LOG_FILE} not found. Skipping copy.")
    except Exception as e:
        print(f"Error copying file: {e}")

def setup_git_identity():
    
    # Check git user identity
    
    try:
        # Check if user.name and user.email are set
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
        # Change to the repo directory
        os.chdir(REPO_DIR)
        print(f"Changed directory to {REPO_DIR}")

        # Set identity if not configured
        setup_git_identity()

        # Check the status of repo
        print("Checking repo status...")
        subprocess.run(["git", "status"], check=True)

        # Add changes to staging area
        print("Adding changes to staging...")
        subprocess.run(["git", "add", "."], check=True)

        # Commit changes with default message
        commit_message = "chat transcript updates"
        print(f"Committing changes with message: {commit_message}")
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Push to GitHub
        print("Pushing changes to GitHub...")
        subprocess.run(["git", "push"], check=True)
        print("Changes pushed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error during GitHub operation: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    while True:  
        print("\n--- Running GitHub Sync Script ---")
        copy_log_file()
        push_to_github()
        print("Waiting for 5 minutes before the next run...\n")
        time.sleep(300)  # 5 minutes = 300 seconds
