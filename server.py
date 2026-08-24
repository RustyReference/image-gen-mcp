from typing import Any

import httpx2
from mcp.server import MCPServer

# Initialize server
mcp = MCPServer("image-gen")

# Constants
VENICE_BASE_URL="https://api.venice.ai/api/v1"


