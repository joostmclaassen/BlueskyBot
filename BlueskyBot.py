import requests
from datetime import datetime, timezone
import schedule
import time
import random
import os

# Constants for Bluesky credentials
BLUESKY_HANDLE = "your.bsky.handle"
BLUESKY_APP_PASSWORD = "your.bsky.password"

# Function to create a session and get the access token
def create_session():
    response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": BLUESKY_HANDLE, "password": BLUESKY_APP_PASSWORD},
    )
    response.raise_for_status()
    session = response.json()
    return session["accessJwt"]

# Function to read all posts from a text file
def read_posts(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]  # Read and clean lines

# Function to post on Bluesky
def post_on_bluesky(post, access_token):
    url = 'https://bsky.social/xrpc/com.atproto.repo.createRecord'  # Correct endpoint for posting
    headers = {
        'Authorization': f'Bearer {access_token}',  # Use the access token obtained from create_session
        'Content-Type': 'application/json'
    }
    
    # Create the payload with the required properties
    payload = {
        'repo': BLUESKY_HANDLE,  # Specify the repository (your account)
        'collection': 'app.bsky.feed.post',  # Specify the collection type
        'record': {
            'text': post,
            'createdAt': datetime.now(timezone.utc).isoformat()  # Correctly formatted createdAt property
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Successfully posted: {post}")
        return True
    else:
        print(f"Failed to post: {response.status_code} - {response.text}")
        return False

# Scheduled job to read and post
def scheduled_post():
    global available_posts, used_posts

    if not available_posts:  # Reload posts if all have been used
        print("All posts have been used. Reloading...")
        available_posts = read_posts('post.txt')
        used_posts = []  # Reset used posts

    access_token = create_session()  # Create session and get access token
    post_content = random.choice(available_posts)  # Choose a random post

    if post_content:
        if post_on_bluesky(post_content, access_token):
            available_posts.remove(post_content)  # Remove the used post
            used_posts.append(post_content)  # Track the used post
    else:
        print("No content to post.")

# Load posts at the start
available_posts = read_posts('post.txt')
used_posts = []

# Schedule the job to run at specific hours
schedule.every().day.at("14:00").do(scheduled_post)
schedule.every().day.at("15:00").do(scheduled_post)
schedule.every().day.at("16:00").do(scheduled_post)

# Main loop to keep the script running
if __name__ == '__main__':
    print("Scheduler started. Waiting to post a random message at 14:00, 15:00, and 16:00...")
    while True:
        schedule.run_pending()
        time.sleep(1)  # Wait for a while before checking again
