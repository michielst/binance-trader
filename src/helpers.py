import requests
from env import *
import json


def send_discord(content):
    headers = {'Content-Type': 'application/json'}  # Header to indicate JSON content
    payload = {'content': content}  # The message content
    response = requests.post(DISCORD_BOT_WEBHOOK, headers=headers, data=json.dumps(payload))  # Send the request

    # if response.status_code == 204:  # HTTP 204 No Content indicates success
    #     print("Message sent successfully!")
    # else:
    #     print(f"Failed to send message. Status code: {response.status_code}")

