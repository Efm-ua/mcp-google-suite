# MCP GSuite Server - Level 3 Module Documentation

## A. MODULE OVERVIEW

DocGem використовує двосерверну MCP архітектуру для розділення відповідальностей:

- **Main MCP Server (Node.js)**: `custom-mcp-server.js` - управляє GCP операціями (Firestore, Cloud Storage, Document AI, Vertex AI)
- **GSuite MCP Server (Python)**: `src/mcp_google_suite/server.py` - спеціалізується на Google Workspace операціях (Drive, Docs, Sheets)
- **Backend Integration**: Python backend взаємодіє з обома серверами через окремі клієнти

### Інтеграційна архітектура:
```
Backend Services → MCPClient → Main MCP (Node.js) → GCP APIs
                → GSuiteMcpClient → GSuite MCP (Python) → Google Workspace APIs
```

## B. ARCHITECTURE

### Core Components:

**Node.js MCP Server:**
- File: `custom-mcp-server.js`
- Protocol: JSON-RPC 2.0 over HTTP/WebSocket
- Services: Firestore, Cloud Storage, Document AI, Vertex AI, Cloud Tasks

**Python GSuite MCP Server:**
- Main: `src/mcp_google_suite/server.py`
- Auth: `src/mcp_google_suite/auth/google_auth.py`
- Services: `src/mcp_google_suite/{drive,docs,sheets}/service.py`
- Protocol: stdio-based MCP communication + HTTP endpoints

**Backend Clients:**
- Main MCP: `backend-cloudrun/app/clients/mcp_client.py`
- GSuite MCP: `backend-cloudrun/app/clients/gsuite_mcp_client.py`

### Communication Flow:
```
Backend → HTTP POST /invoke-tool → GSuite MCP → Google Workspace APIs
Backend → JSON-RPC 2.0 → Main MCP → GCP Services
```

## C. MCP TOOLS

### Main MCP Server (Node.js) Tools:

**Document AI Operations:**
- `docAiProcessDocumentOnline` - OCR processing of documents
- `docAiGetProcessorInfo` - Get Document AI processor information

**Vertex AI Operations:**
- `geminiChat` - Text generation with context support
- `geminiEnhanceDocument` - Document analysis and enhancement
- `geminiUpdateTags` - Smart tag generation and updates

**Firestore Operations:**
- `firestoreGetDocument` - Retrieve documents by ID
- `firestoreListCollection` - Query collections with filters
- `addFirestoreDocument` - Create new documents
- `updateFirestoreDocument` - Update existing documents
- `deleteFirestoreDocument` - Remove documents

**Cloud Storage Operations:**
- `storageUploadFile` - Upload files to buckets
- `storageGenerateDownloadUrlV4` - Generate signed download URLs
- `storageGenerateUploadUrlV4` - Generate signed upload URLs
- `storageListFiles` - List bucket contents
- `storageGetFileMetadata` - Get file information
- `storageDownloadFile` - Retrieve file contents
- `storageDeleteFile` - Remove files
- `storageFileExists` - Check file existence

**Cloud Tasks Operations:**
- `cloudTasksCreateHttpTask` - Create background tasks
- `cloudTasksListQueues` - List task queues
- `cloudTasksGetTask` - Get task information

### GSuite MCP Server (Python) Tools:

**Google Drive:**
- `drive_search_files` - Search files with query filters
- `drive_create_folder` - Create new folders

**Google Docs:**
- `docs_create` - Create new documents
- `docs_get_content` - Extract document text content
- `docs_update_content` - Replace document content
- `docs_append_formatted_text` - Add formatted text
- `docs_batch_update` - Execute batch formatting operations

**Google Sheets:**
- `sheets_create` - Create new spreadsheets
- `sheets_get_values` - Read cell ranges
- `sheets_update_values` - Write to cell ranges

## D. CONFIGURATION

### Environment Variables:

**Main MCP Server:**
```bash
# GCP Project Configuration
GOOGLE_CLOUD_PROJECT=docgem-ocr-poc
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS_JSON=<service-account-json>

# Document AI
DOCAI_LOCATION=us
DOCAI_PROCESSOR_ID=9ee4417089fe5019

# Cloud Storage
GCS_BUCKET_NAME=docgem-documents

# Vertex AI
VERTEX_AI_PROJECT=docgem-ocr-poc
VERTEX_AI_LOCATION=us-central1

# Server Configuration
MCP_HTTP_PATH=/mcp
MCP_PREDEFINED_SESSION_ID=cursor-session-123
MCP_HTTP_HOST=0.0.0.0
PORT=3001
```

**GSuite MCP Server:**
```bash
# OAuth Configuration
OAUTH_CLIENT_ID=<google-oauth-client-id>
OAUTH_CLIENT_SECRET=<google-oauth-client-secret>
OAUTH_CREDENTIALS_PATH=~/.google/oauth.keys.json

# Server Configuration
HOST=0.0.0.0
PORT=8000
SERVER_MODE=ws  # або stdio

# GSuite MCP Server URL (for backend client)
GSUITE_MCP_SERVER_URL=https://gsuite-mcp-server-url.run.app
```

**Backend Integration:**
```bash
# MCP Server URLs
MCP_SERVER_URL=https://docgem-mcp-server-778416671000.us-central1.run.app/mcp
GSUITE_MCP_SERVER_URL=https://gsuite-mcp-server-url.run.app
```

## E. DEVELOPMENT COMMANDS

### Node.js MCP Server:
```bash
# Install dependencies
cd /home/efmua/docgem-project
npm install

# Run development server
node custom-mcp-server.js

# Run with debug logging
DEBUG=mcp* node custom-mcp-server.js

# Test client connection
node simple-mcp-client.js
```

### Python GSuite Server:
```bash
# Setup environment
cd /home/efmua/docgem-project/mcp-gsuite-server
uv venv
source .venv/bin/activate
uv pip install -e .

# Run server (WebSocket mode)
mcp-google-suite run --mode ws --host 0.0.0.0 --port 8000

# Run server (stdio mode)
mcp-google-suite run --mode stdio

# Test server health
curl http://localhost:8000/health
```

### Debug Tools:
```bash
# Debug MCP tools
node debug-mcp.js

# Test MCP client
node test-mcp-client.js

# Check server status
curl http://localhost:3001/health  # Main MCP
curl http://localhost:8000/health  # GSuite MCP
```

## F. INTEGRATION PATTERNS

### MCPClient Usage (Main MCP):
```python
from app.clients.mcp_client import MCPClient

# Initialize with default configuration
mcp_client = MCPClient()

# Call tool with parameters
response = await mcp_client.call_mcp_tool(
    method_name="firestoreGetDocument",
    params={
        "collectionId": "documents",
        "documentId": "doc123"
    }
)

# Handle standardized response
if isinstance(response, StandardMCPDataResponse) and response.success:
    data = response.data
    # Process successful response
elif isinstance(response, StandardMCPErrorResponse):
    error = response.error
    logger.error(f"MCP error: {error.message}")
```

### GSuiteMcpClient Usage:
```python
from app.clients.gsuite_mcp_client import GSuiteMcpClient

# Initialize client
gsuite_client = GSuiteMcpClient()

# Create Google Document
doc_result = await gsuite_client.create_document(
    title="DocGem Export",
    content="Document content here"
)

# Search Drive files
search_result = await gsuite_client.search_drive_files(
    query="type:pdf",
    page_size=20
)

# Update document content
update_result = await gsuite_client.update_document_content(
    document_id="doc_id_here",
    content="New content"
)
```

### Request/Response Formats:

**Main MCP (JSON-RPC 2.0):**
```json
{
    "jsonrpc": "2.0",
    "id": "request-123",
    "method": "firestoreGetDocument",
    "params": {
        "collectionId": "documents",
        "documentId": "doc123"
    }
}
```

**GSuite MCP (HTTP POST):**
```json
{
    "tool_name": "docs_create",
    "params": {
        "title": "New Document",
        "content": "Initial content"
    }
}
```

### Error Handling:
```python
try:
    result = await mcp_client.call_mcp_tool(method_name, params)
except MCPConnectionError as e:
    logger.error(f"MCP connection failed: {e}")
    # Handle connection error
except MCPToolError as e:
    logger.error(f"MCP tool error: {e}, code: {e.code}")
    # Handle tool-specific error
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle unexpected errors
```

### Caching Strategies:
```python
# Main MCP has built-in response caching (30 min TTL)
# GSuite MCP relies on HTTP client caching
# Backend services implement additional caching layers

# Example with custom cache key
cache_key = f"mcp_result_{method_name}_{hash(str(params))}"
cached_result = await cache_service.get(cache_key)
if not cached_result:
    result = await mcp_client.call_mcp_tool(method_name, params)
    await cache_service.set(cache_key, result, ttl=300)  # 5 min
```

## G. TOOL REGISTRATION

### Adding New Tools to Main MCP:
```javascript
// Add to toolDefinitions array in custom-mcp-server.js
{
  name: "newToolName",
  description: "Tool description",
  input_schema: {
    type: "object",
    properties: {
      param1: { type: "string", description: "Parameter description" },
      param2: { type: "number", description: "Numeric parameter" }
    },
    required: ["param1"]
  },
  handler: async (params) => {
    // Tool implementation
    const { param1, param2 } = params;
    const result = await performOperation(param1, param2);
    return { success: true, data: result };
  }
}
```

### Adding New Tools to GSuite MCP:
```python
# Add method to GoogleWorkspaceMCPServer class
async def _handle_new_tool_name(
    self, context: GoogleWorkspaceContext, arguments: dict
) -> Dict[str, Any]:
    """Handle new tool requests."""
    param1 = arguments.get("param1")
    if not param1:
        raise ValueError("param1 is required")
    
    logger.debug(f"New tool called with param1: {param1}")
    result = await context.service.perform_operation(param1)
    return {"success": True, "data": result}

# Add to _get_tools_list method
types.Tool(
    name="new_tool_name",
    description="New tool description", 
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    }
)
```

### Tool Naming Conventions:
- Use snake_case for tool names
- Prefix with service name: `drive_`, `docs_`, `sheets_`, `firestore_`, `storage_`
- Use descriptive verbs: `create`, `get`, `update`, `delete`, `search`, `list`
- Keep names concise but clear

### Parameter Schemas:
```json
{
    "type": "object",
    "properties": {
        "required_param": {
            "type": "string",
            "description": "Clear parameter description"
        },
        "optional_param": {
            "type": "integer", 
            "description": "Optional parameter with default",
            "default": 10
        }
    },
    "required": ["required_param"]
}
```

### Response Formats:
```json
{
    "success": true,
    "data": {
        // Tool-specific response data
    },
    "metadata": {
        "timestamp": "2024-01-01T00:00:00Z",
        "duration": 150
    }
}
```

## H. DEPLOYMENT

### Cloud Run Deployment:

**Main MCP Server:**
```bash
# Build and deploy
gcloud builds submit --config cloudbuild.yaml .

# Deploy with secrets
gcloud run deploy docgem-mcp-server \
    --image gcr.io/docgem-ocr-poc/docgem-mcp-server:latest \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=docgem-ocr-poc" \
    --set-secrets "GOOGLE_APPLICATION_CREDENTIALS_JSON=service-account-key:latest"
```

**GSuite MCP Server:**
```bash
# Build with GSuite cloudbuild
cd mcp-gsuite-server
gcloud builds submit --config cloudbuild-gsuite.yaml .

# Deploy to Cloud Run
kubectl apply -f cloudrun-deploy.yaml
```

### Docker Configuration:

**Main MCP Dockerfile:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3001
CMD ["node", "custom-mcp-server.js"]
```

**GSuite MCP Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv install --frozen
COPY . .
EXPOSE 8000
CMD ["mcp-google-suite", "run", "--mode", "ws", "--port", "8000"]
```

### Secret Management:
```bash
# Store OAuth credentials
gcloud secrets create oauth-credentials \
    --data-file=oauth.keys.json

# Store service account
gcloud secrets create service-account-key \
    --data-file=service-account.json

# Grant access to Cloud Run service accounts
gcloud secrets add-iam-policy-binding oauth-credentials \
    --member="serviceAccount:gsuite-mcp@project.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### Health Check Endpoints:
```bash
# Main MCP health check
curl https://docgem-mcp-server-url.run.app/health
# Response: {"status": "ok", "server": "DocGem MCP Server", "version": "1.0.0"}

# GSuite MCP health check  
curl https://gsuite-mcp-server-url.run.app/health
# Response: {"status": "healthy", "tools": ["drive_search_files", ...]}
```

### Monitoring and Logging:
```bash
# View logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=docgem-mcp-server" --limit 100

# Create log-based metrics
gcloud logging metrics create mcp_error_rate \
    --description="MCP server error rate" \
    --log-filter='resource.type="cloud_run_revision" AND severity="ERROR"'
```

## I. TROUBLESHOOTING

### Common Authentication Issues:

**OAuth Token Expired:**
```bash
# Re-authenticate GSuite MCP
mcp-google-suite auth --reset

# Check token status
mcp-google-suite auth --status
```

**Service Account Issues:**
```python
# Verify credentials in code
import google.auth

try:
    credentials, project = google.auth.default()
    logger.info(f"Using project: {project}")
except Exception as e:
    logger.error(f"Auth error: {e}")
```

### API Quota Errors:

**Document AI Quota:**
- Check quota usage in GCP Console
- Implement exponential backoff
- Use batch processing for multiple documents

**Google Workspace Quota:**
```python
# Implement rate limiting
import asyncio
from asyncio import Semaphore

class GSuiteRateLimiter:
    def __init__(self, max_concurrent=5):
        self.semaphore = Semaphore(max_concurrent)
    
    async def execute_with_limit(self, coro):
        async with self.semaphore:
            await asyncio.sleep(0.1)  # Rate limiting
            return await coro
```

### Connection Problems:

**MCP Server Unreachable:**
```bash
# Test network connectivity
curl -v https://mcp-server-url/health

# Check DNS resolution
nslookup mcp-server-url.run.app

# Test from backend container
kubectl exec -it backend-pod -- curl http://mcp-server-url/health
```

**WebSocket Connection Issues:**
```python
# Test WebSocket connection
import asyncio
import websockets

async def test_websocket():
    uri = "wss://gsuite-mcp-server-url.run.app/ws"
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send("ping")
            response = await websocket.recv()
            print(f"Response: {response}")
    except Exception as e:
        print(f"WebSocket error: {e}")
```

### Debugging Techniques:

**Enable Debug Logging:**
```javascript
// Main MCP Server
const DEBUG = process.env.DEBUG || false;
if (DEBUG) {
    console.log("[DEBUG]", message, data);
}
```

```python
# GSuite MCP Server  
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

**HTTP Request Tracing:**
```python
# Add correlation IDs to requests
import uuid

correlation_id = str(uuid.uuid4())
logger.info("MCP request", correlation_id=correlation_id, tool_name=tool_name)

# Trace through both MCP servers
headers = {"X-Correlation-ID": correlation_id}
response = await http_client.post(url, json=data, headers=headers)
```

**Tool Response Validation:**
```python
def validate_mcp_response(response):
    """Validate MCP response structure."""
    if not isinstance(response, dict):
        raise ValueError(f"Invalid response type: {type(response)}")
    
    if "success" not in response:
        raise ValueError("Missing success field in response")
    
    if not response["success"] and "error" not in response:
        raise ValueError("Error response missing error field")
    
    return True
```

---

## Tool Summary

**Main MCP Server (Node.js): 20+ tools**
- Document AI: 2 tools (process, get processor info)
- Vertex AI: 3 tools (chat, enhance, update tags)  
- Firestore: 5 tools (get, list, add, update, delete)
- Cloud Storage: 8 tools (upload, download, list, metadata, URLs, delete, exists)
- Cloud Tasks: 3 tools (create, list, get)

**GSuite MCP Server (Python): 9 tools**
- Google Drive: 2 tools (search files, create folder)
- Google Docs: 5 tools (create, get content, update, append, batch update)
- Google Sheets: 3 tools (create, get values, update values)

**Total: 29 specialized MCP tools** for comprehensive DocGem backend integration.