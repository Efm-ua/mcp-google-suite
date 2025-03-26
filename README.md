# MCP Google Workspace Server

A Model Context Protocol (MCP) server that provides tools for interacting with Google Workspace (Drive, Docs, and Sheets).

## Features

- Google Drive operations (search, create folders)
- Google Docs operations (create, read, update)
- Google Sheets operations (create, read, update)
- Support for stdio, SSE, and WebSocket transport modes
- Compatible with MCP Inspector for testing and debugging
- Integration with MCP-compatible clients like Cursor

## Prerequisites

- Python 3.11 or higher
- Google Cloud Project with Google Workspace APIs enabled
- OAuth 2.0 credentials for Google Workspace
- Node.js and npm (for MCP Inspector)
- `uv` package manager (recommended)

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
   - Configure OAuth consent screen
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials and save them as `oauth.keys.json` in `~/.google/` directory

## Usage

### Authentication

Before using the server, you need to authenticate with Google:

```bash
mcp-google auth
```

This will:
1. Look for OAuth credentials in `~/.google/oauth.keys.json`
2. Open a browser window for Google authentication
3. Save the server credentials to `~/.google/server-creds.json`

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

### Using with MCP-Compatible Clients

The server can be integrated with MCP-compatible clients like Cursor. Here's how to set it up:

1. Create an MCP configuration file (e.g., `mcp-config.json`):
```json
{
  "mcpServers": {
    "mcp-google-suite": {
      "command": "uv",
      "args": ["--directory", "WORKSPACE_DIR", "run", "mcp-google"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "~/.google/server-creds.json",
        "GOOGLE_OAUTH_CREDENTIALS": "~/.google/oauth.keys.json"
      }
    }
  }
}
```

2. Configure your client to use this configuration file.

3. The server will automatically:
   - Use the specified credential paths
   - Handle authentication when needed
   - Provide Google Workspace tools to your client

Note: Always use `uv` for managing the Python environment and running the server to ensure consistent behavior.

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

## Credential Management

The server uses two types of credentials and follows a specific precedence order for finding them:

1. OAuth Credentials:
   - Primary location: `GOOGLE_OAUTH_CREDENTIALS` environment variable
   - Fallback: `~/.google/oauth.keys.json` (default)
   - Contains client ID and client secret
   - Required for initial setup

2. Server Credentials:
   - Primary location: `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - Fallback: `~/.google/server-creds.json` (default)
   - Generated during authentication
   - Contains access and refresh tokens
   - Created automatically when running `mcp-google auth`

### Credential Precedence

The server looks for credentials in the following order:

1. Environment Variables:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/server-creds.json"
   export GOOGLE_OAUTH_CREDENTIALS="/path/to/oauth.keys.json"
   ```

2. Configuration File:
   Create a `config.json` in the project root:
   ```json
   {
       "credentials": {
           "server_credentials": "~/.google/server-creds.json",
           "oauth_credentials": "~/.google/oauth.keys.json"
       }
   }
   ```

3. Default Locations:
   - Server credentials: `~/.google/server-creds.json`
   - OAuth credentials: `~/.google/oauth.keys.json`

Note: Environment variables take precedence over both the config.json and default locations. This is particularly useful when:
- Running in different environments (development, production)
- Using CI/CD pipelines
- Integrating with MCP-compatible clients like Cursor

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

- Keep your credential files secure
- Use appropriate scopes in the OAuth consent screen
- Follow the principle of least privilege when requesting access
- Never commit credential files to version control
- Always use `uv` for managing the Python environment

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 