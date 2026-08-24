from typing import Any
import os
import requests
import base64
from dotenv import load_dotenv
import json

from mcp.server import MCPServer

# Initialize server
mcp = MCPServer("image-gen")

# Constants
VENICE_BASE_URL="https://api.venice.ai/api/v1"

load_dotenv()
api_key = os.getenv("VENICE_API_KEY")

# helper 
def get_image(prompt: str):
    url = "https://api.venice.ai/api/v1/images/generations"

    payload = {
        "prompt": prompt,
        "background": "auto",
        "model": "venice-sd35",
        "moderation": "low",
        "n": 1,
        "output_compression": 100,
        "output_format": "png",
        "quality": "auto",
        "response_format": "b64_json",
        "size": "auto",
        "style": "natural",
        "user": "user123"
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    response.raise_for_status()

    b64 = response.json()["data"][0]["b64_json"]
    with open("generated_image.png", "wb") as fh:
        fh.write(base64.b64decode(b64))


# runner 
get_image("A beach with red roses")