# MCP Google Workspace Server

A Model Context Protocol (MCP) server that provides tools for interacting with Google Workspace (Drive, Docs, and Sheets).

## Features

- Google Drive operations (search, create folders)
- Google Docs operations (create, read, update)
- Google Sheets operations (create, read, update)
- Support for stdio, SSE, and WebSocket transport modes
- Compatible with MCP Inspector for testing and debugging

## Prerequisites

- Python 3.11 or higher
- Google Cloud Project with Google Workspace APIs enabled
- OAuth 2.0 credentials for Google Workspace
- Node.js and npm (for MCP Inspector)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-google-suite
```

2. Install dependencies using `uv`:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows
uv pip install -e .
```

3. Set up Google OAuth credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select an existing one
   - Enable the Google Drive, Google Docs, and Google Sheets APIs
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials and save them as `credentials.json` in the project root

## Usage

### Direct Server Execution

1. Start the server in stdio mode (default):
```bash
mcp-google
# or
mcp-google run
```

2. Start the server in WebSocket mode:
```bash
mcp-google run --mode ws
```

3. Run authentication:
```bash
mcp-google auth
```

### Using MCP Inspector

The MCP Inspector provides a graphical interface for testing and debugging your MCP server.

1. Install the MCP Inspector:
```bash
npm install -g @modelcontextprotocol/inspector
```

2. Run the server with the inspector:
```bash
npx @modelcontextprotocol/inspector uv run mcp-google
```

The inspector will:
- Start your server in stdio mode
- Provide a web interface for testing available tools
- Show request/response data
- Allow interactive testing of all server capabilities

### Available Tools

#### Drive Tools
- `drive_search_files`: Search for files in Google Drive
- `drive_create_folder`: Create a new folder in Google Drive

#### Docs Tools
- `docs_create`: Create a new Google Doc
- `docs_get_content`: Get the contents of a Google Doc
- `docs_update_content`: Update the content of a Google Doc

#### Sheets Tools
- `sheets_create`: Create a new Google Sheet
- `sheets_get_values`: Get values from a Google Sheet range
- `sheets_update_values`: Update values in a Google Sheet range

## Example Tool Calls

```python
# Example: Create a new Google Doc
{
    "tool": "docs_create",
    "parameters": {
        "title": "My Document",
        "content": "Hello, World!"
    }
}

# Example: Search files in Drive
{
    "tool": "drive_search_files",
    "parameters": {
        "query": "name contains 'report'",
        "page_size": 10
    }
}
```

## Authentication

On first run, the server will open a browser window for OAuth authentication. After successful authentication, the credentials will be saved to `token.json` for future use.

## MCP Server Configuration

To configure the MCP server with the required Google credentials, use the following configuration in your MCP configuration file:

```json
{
  "mcpServers": {
    "mcp-google-suite": {
      "command": "uv",
      "args": ["--directory",WORKSPACE_DIR, "run", "mcp-google"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/.gdrive-server-creds.json",
        "GOOGLE_OAUTH_CREDENTIALS": "/path/to/gcp-oauth.keys.json"
      }
    }
  }
}
```

Replace `/path/to/` with the absolute paths to your credential files:
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to the service account credentials file (`.gdrive-server-creds.json`)
- `GOOGLE_OAUTH_CREDENTIALS`: Path to the OAuth client credentials file (`gcp-oauth.keys.json`)

Make sure to use absolute paths to ensure the files can be found regardless of where the server is started from.

## Development and Testing

### Using MCP Inspector for Development

The MCP Inspector is a valuable tool for development and testing:

1. It provides real-time feedback on:
   - Tool registration and availability
   - Request/response format
   - Error handling
   - Authentication status

2. Interactive testing features:
   - Test tools with custom parameters
   - View detailed request/response logs
   - Validate tool schemas
   - Debug authentication issues

To start development with the inspector:
```bash
npx @modelcontextprotocol/inspector uv run mcp-google
```

## Security Considerations

- Keep your `credentials.json` and `token.json` files secure
- Use appropriate scopes in the OAuth consent screen
- Follow the principle of least privilege when requesting access

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 