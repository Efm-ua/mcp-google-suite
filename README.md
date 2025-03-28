# MCP Google Workspace Server

[![CI](https://github.com/adexltd/mcp-google-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/adexltd/mcp-google-suite/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/adexltd/mcp-google-suite/branch/main/graph/badge.svg)](https://codecov.io/gh/adexltd/mcp-google-suite)
[![PyPI version](https://badge.fury.io/py/mcp-google-suite.svg)](https://badge.fury.io/py/mcp-google-suite)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Model Context Protocol (MCP) server enabling AI agents to interact with Google Workspace (Drive, Docs, and Sheets) services.

## 🌟 Features

- Google Drive: Search files, create folders
- Google Docs: Create, read, update documents
- Google Sheets: Create spreadsheets, read/write cell values
- Multiple transport modes: stdio (default), SSE, WebSocket
- MCP-compatible client support (Cursor, etc.)

## 📋 Installation

### Using uv (recommended)
```bash
uvx mcp-google-suite
```

### Using pip
```bash
pip install mcp-google-suite
```

### Development setup
```bash
# Clone and install
git clone git@github.com:adexltd/mcp-google-suite.git && cd mcp-google-suite
uv venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e .
```

## 🔧 Configuration

### Configure for MCP Clients

Add to your client settings (e.g. Cursor, Claude):

Using uvx (recommended):
```json
{
  "mcpServers": {
    "mcp-google-suite": {
      "command": "uvx",
      "args": ["mcp-google-suite"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "~/.google/server-creds.json",
        "GOOGLE_OAUTH_CREDENTIALS": "~/.google/oauth.keys.json"
      }
    }
  }
}
```

Using pip installation:
```json
{
  "mcpServers": {
    "mcp-google-suite": {
      "command": "python",
      "args": ["-m", "mcp_google_suite"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "~/.google/server-creds.json",
        "GOOGLE_OAUTH_CREDENTIALS": "~/.google/oauth.keys.json"
      }
    }
  }
}
```

### Google OAuth Setup
1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Enable Drive, Docs, and Sheets APIs
3. Create OAuth 2.0 credentials
4. Save as `~/.google/oauth.keys.json`
5. Run `mcp-google auth` to authenticate

### Available Tools

#### Drive Operations
- `drive_search_files`: Search files in Google Drive
  - `query` (string, required): Search query
  - `page_size` (integer, optional): Number of results to return
- `drive_create_folder`: Create a new folder
  - `name` (string, required): Folder name
  - `parent_id` (string, optional): Parent folder ID

#### Docs Operations
- `docs_create`: Create a new document
  - `title` (string, required): Document title
  - `content` (string, optional): Initial content
- `docs_get_content`: Get document content
  - `document_id` (string, required): Document ID
- `docs_update_content`: Update document content
  - `document_id` (string, required): Document ID
  - `content` (string, required): New content

#### Sheets Operations
- `sheets_create`: Create a new spreadsheet
  - `title` (string, required): Spreadsheet title
  - `sheets` (array, optional): Sheet names
- `sheets_get_values`: Get cell values
  - `spreadsheet_id` (string, required): Spreadsheet ID
  - `range` (string, required): A1 notation range
- `sheets_update_values`: Update cell values
  - `spreadsheet_id` (string, required): Spreadsheet ID
  - `range` (string, required): A1 notation range
  - `values` (array, required): 2D array of values

## 🛠️ Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black . && ruff check --fix .
```

## 🔍 Debugging

Use the MCP Inspector for interactive testing:

```bash
# Using uvx
npx @modelcontextprotocol/inspector uvx mcp-google

# For development
cd path/to/mcp-google-suite
npx @modelcontextprotocol/inspector uv run mcp-google
```

## 📚 Resources

- [Documentation](https://github.com/adexltd/mcp-google-suite/wiki)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Pre-commit Hooks](https://pre-commit.com)
- [Google Cloud Console](https://console.cloud.google.com)

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 🔒 Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities and best practices.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.
