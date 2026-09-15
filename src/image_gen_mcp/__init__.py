from typing import Any
import os
import requests
import base64
from PIL import Image
from dotenv import load_dotenv
import json
import sys
import io

from mcp.server import MCPServer
import mcp.types as types

# Initialize server
mcp = MCPServer("image-gen")

# Constants
VENICE_BASE_URL="https://api.venice.ai/api/v1"
DEFAULT_MODEL = "z-image-turbo"
MAX_SIZE_CLAUDE_DESKTOP = 900 * 1024 # 900 kilobytes
DEFAULT_QUALITY = 80 # Quality of the WebP encoded image

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

def venice_image_request(url: str, prompt: str, model: str = DEFAULT_MODEL, format: str = "png") -> str:
    """
    Creates the API call to Venice and returns the base64 string of the generated image.

    Args:
        prompt: the prompt for image generation
        model: the model used to generate the image
        format: the file format for the resulting image. For now, it stays at .png but may change to .webp
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "cfg_scale": 7.5,
        "embed_exif_metadata": False,
        "format": format,
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

    # timeout is in seconds; 180 is the default number of seconds
    response = requests.post(url, json=payload, headers=headers, timeout=180) 
    response.raise_for_status()

    b64 = response.json()["images"][0]

    return b64


@mcp.tool()
def generate_image(prompt: str):
    """
    Generate an image from a text description and display it in the conversation.

    Use this whenever the user asks for an image, picture, illustration, drawing,
    artwork, logo, or any visual to be created. Returns the generated image directly.

    Args:
        prompt: Detailed description of the image to generate.
        model: Venice model id. Defaults to a fast model (z-image-turbo)
                as other models can be slower.
    """

    veniceUrl = f"{VENICE_BASE_URL}/image/generate"
    b64 = venice_image_request(veniceUrl, prompt)
    mime_type = "image/png"

    # Test the size of the base64 string. 
    # Claude Desktop tests how big the content is BEFORE decoding
    if (len(b64) > MAX_SIZE_CLAUDE_DESKTOP): # Each character is 1 byte; size of b64 == len(b64)
        mime_type = "image/webp"
        png_bytes = base64.b64decode(b64)

        with Image.open(io.BytesIO(png_bytes)) as img:
            webp_buffer = io.BytesIO()
            img.save(webp_buffer, format="WEBP", quality=DEFAULT_QUALITY)
            webp_bytes = webp_buffer.getvalue()

        b64 = base64.b64encode(webp_bytes).decode("utf-8")
    
    return types.ImageContent(type="image", data=b64, mime_type=mime_type)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()