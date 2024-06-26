import requests
import os
import logging

BEARER_TOKEN = os.getenv('BEARER_TOKEN')

# log to app.log file in the same directory
logging.basicConfig(filename='app.log', level=logging.INFO)
logger = logging.getLogger(__name__)


# function to send a post to the fastapi endpoint
def send_post(title, body, flair_id, subreddit, post_type, url):
    response_url = f"http://localhost:8000/post/{subreddit}"
    payload = {"title": title, "body": body, "flair_id": flair_id, "post_type": post_type, "url": url}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {BEARER_TOKEN}"}

    try:
        response = requests.post(response_url, json=payload, headers=headers)
        response.raise_for_status()  # Raises a HTTPError for 4xx, 5xx errors
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to {response_url} failed: {e}")
        return None

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None


# Function to check flairs for a subreddit
def check_flairs(subreddit):
    url = f"http://localhost:8000/subreddit-flairs/{subreddit}"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {BEARER_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises a HTTPError for 4xx, 5xx errors
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to {url} failed: {e}")
        return None

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None


# Function to add comment to a post
def send_comment(post_id, comment):
    response_url = f"http://localhost:8000/post/comment/{post_id}"
    payload = {"post_id": post_id, "comment": comment}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {BEARER_TOKEN}"}

    try:
        response = requests.post(response_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to {response_url} failed: {e}")
        return None