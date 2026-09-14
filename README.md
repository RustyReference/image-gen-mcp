# image-gen-mcp
Ever annoyed that Claude still can't create images (as of September 2026) or just wanted to integrate an API image generator to your personal chatbot?

This is a local (for now) MCP server that allows you to generate images inline with Claude using the Venice AI API endpoint. 

## Setup 
### Requirements
- Python 3.12+
- uv
- A Venice AI API key (see [this link](https://venice.ai/settings/api))

### Install
1. Clone this repository
2. Run `uv sync`
3. Create a `.env` file, include a value called `VENICE_API_KEY`, and set it equal to your Venice API key after you generate it (e.g. `VENICE_API_KEY=<YOUR API KEY`)

### Connect to Claude Desktop
- Refer to [this source](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server) (use Ctrl+F or Cmd+F for Mac and search for `claude_desktop_config.json`) to help find the directory to the `claude_desktop_config.json` file. It will differ depending on your operating system. 
- Follow the example by accessing the `claude_desktop_config.json` file and modifying the values so they fit your system as follows:
```
{
  "mcpServers": {
    "image-gen-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "<ABSOLUTE-PATH-TO-PARENT-FOLDER>/image-gen-mcp",
        "run",
        "image-gen-mcp"
      ]
    }
  }
}
```

# What's Coming Up?
I currently plan on creating an additional endpoint to OpenAI and perhaps Gemini as well.

I also have plans to integrate this with LibreChat.