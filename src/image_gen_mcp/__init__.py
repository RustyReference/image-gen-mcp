from typing import Any
import os
import requests
import base64
from dotenv import load_dotenv
import json

from mcp.server import MCPServer
import mcp.types as types

# Initialize server
mcp = MCPServer("image-gen")

# Constants
VENICE_BASE_URL="https://api.venice.ai/api/v1"

load_dotenv()
api_key = os.getenv("VENICE_API_KEY")

# helper 
def openai_image_request(url: str, prompt: str):
    payload = {
        "prompt": prompt,
        "background": "auto",
        "model": "TODO",
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

    # Make the API call
    response = requests.post(url, json=payload, headers=headers)

    response.raise_for_status()

    # Save the image as a file
    b64 = response.json()["data"][0]["b64_json"]
    with open("generated_image.png", "wb") as fh:
        fh.write(base64.b64decode(b64))

def venice_image_request(url: str, prompt: str) -> str:
    payload = {
        "model": "seedream-v5-pro",
        "prompt": prompt,
        "cfg_scale": 7.5,
        "embed_exif_metadata": False,
        "format": "png",
        "height": 1024,
        "hide_watermark": True,
        "lora_strength": 50,
        "negative_prompt": "",
        "return_binary": False,
        "variants": 1,
        "safe_mode": False,
        "seed": 0,
        "steps": 8,
        "style_preset": "Anime",
        "aspect_ratio": "1:1",
        "resolution": "1K",
        "quality": "high",
        "enable_web_search": False,
        "disable_prompt_optimization_thinking": False,
        "enhance_prompt": False,
        "width": 1024,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    response.raise_for_status()

    b64 = response.json()["images"][0]
    # with open("generated_image.png", "wb") as fh:
    #     fh.write(base64.b64decode(b64))
    return b64


@mcp.tool()
def generate_image(prompt: str):
    """
    Generate an image from a text description and display it in the conversation.

    Use this whenever the user asks for an image, picture, illustration, drawing,
    artwork, logo, or any visual to be created. Returns the generated image directly.

    Args:
        prompt: Detailed description of the image to generate.
    """
    veniceUrl = f"{VENICE_BASE_URL}/image/generate"
    b64 = venice_image_request(veniceUrl, prompt)
    return types.ImageContent(type="image", data=b64, mime_type="image/png")

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()