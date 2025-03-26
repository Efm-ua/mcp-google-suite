import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncIterator, Awaitable, Callable, Dict, List, Optional

import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.shared.exceptions import McpError
from tabulate import tabulate

from mcp_google_suite.auth.google_auth import GoogleAuth
from mcp_google_suite.config import Config
from mcp_google_suite.docs.service import DocsService
from mcp_google_suite.drive.service import DriveService
from mcp_google_suite.sheets.service import SheetsService

if TYPE_CHECKING:
    pass  # Remove unused ServerContext import


# Configure logging
def setup_logging():
    """Configure logging with both file and console handlers."""
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Create a timestamp-based log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"mcp_google_suite_{timestamp}.log")

    # Define formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    )
    console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # File handler - DEBUG level with detailed formatting
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Console handler - INFO level with simpler formatting
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger


# Initialize logging
logger = setup_logging()


@dataclass
class GoogleWorkspaceContext:
    """Context for Google Workspace services."""

    auth: GoogleAuth
    drive: DriveService
    docs: DocsService
    sheets: SheetsService


ToolHandler = Callable[[GoogleWorkspaceContext, dict], Awaitable[Any]]


class GoogleWorkspaceMCPServer:
    """MCP server for Google Workspace operations."""

    def __init__(self, config: Optional[Config] = None, config_path: Optional[str] = None):
        """Initialize the server with optional configuration."""
        logger.info("Initializing GoogleWorkspaceMCPServer")
        try:
            self.config = config or Config.load(config_path)
            logger.debug("Config loaded successfully")

            # Create server instance
            logger.debug("Creating Server instance")
            self._context = None  # Store context for access in tools
            self.server = Server("mcp-google-suite")

            # Initialize tool registry
            self._tool_registry: Dict[str, ToolHandler] = {}

            logger.debug("Server instance created")

            # Register tools
            logger.debug("Starting tool registration")
            self.register_tools()

            # Display available tools
            self._display_available_tools()

            logger.info("Server initialization complete")
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}", exc_info=True)
            raise

    def _display_available_tools(self):
        """Display available tools in a structured format."""
        try:
            logger.info("Available Tools Summary:")

            # Prepare tool information for display
            tool_info = []
            for name, _handler in self._tool_registry.items():
                tool_schema = next((t for t in self._get_tools_list() if t.name == name), None)
                if tool_schema:
                    required_params = tool_schema.inputSchema.get("required", [])
                    all_params = list(tool_schema.inputSchema.get("properties", {}).keys())
                    optional_params = [p for p in all_params if p not in required_params]

                    tool_info.append(
                        [
                            name,
                            tool_schema.description,
                            ", ".join(required_params) or "None",
                            ", ".join(optional_params) or "None",
                        ]
                    )

            # Create a formatted table
            headers = ["Tool Name", "Description", "Required Parameters", "Optional Parameters"]
            table = tabulate(tool_info, headers=headers, tablefmt="grid")

            # Print the table with a border
            border_line = "=" * len(table.split("\n")[0])
            logger.info("\n" + border_line)
            logger.info("MCP Google Workspace Tools")
            logger.info(border_line)
            logger.info("\n" + table)
            logger.info(border_line + "\n")

            # Log summary statistics
            logger.info(f"Total tools available: {len(tool_info)}")
            logger.info(
                f"Tools with required parameters: {sum(1 for t in tool_info if t[2] != 'None')}"
            )
            logger.info(
                f"Tools with optional parameters: {sum(1 for t in tool_info if t[3] != 'None')}"
            )

        except Exception as e:
            logger.error(f"Error displaying tools: {str(e)}", exc_info=True)

    def _get_tools_list(self) -> List[types.Tool]:
        """Get the list of available tools with their schemas."""
        return [
            types.Tool(
                name="drive_search_files",
                description="Search for files in Google Drive",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "page_size": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="drive_create_folder",
                description="Create a new folder in Google Drive",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of the folder"},
                        "parent_id": {"type": "string", "description": "ID of parent folder"},
                    },
                    "required": ["name"],
                },
            ),
            types.Tool(
                name="docs_create",
                description="Create a new Google Doc",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Title of the document"},
                        "content": {"type": "string", "description": "Initial content"},
                    },
                    "required": ["title"],
                },
            ),
            types.Tool(
                name="docs_get_content",
                description="Get the contents of a Google Doc",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string", "description": "ID of the document"}
                    },
                    "required": ["document_id"],
                },
            ),
            types.Tool(
                name="docs_update_content",
                description="Update the content of a Google Doc",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string", "description": "ID of the document"},
                        "content": {"type": "string", "description": "New content"},
                    },
                    "required": ["document_id", "content"],
                },
            ),
            types.Tool(
                name="sheets_create",
                description="Create a new Google Sheet",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Title of the spreadsheet"},
                        "sheets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Sheet names",
                        },
                    },
                    "required": ["title"],
                },
            ),
            types.Tool(
                name="sheets_get_values",
                description="Get values from a Google Sheet range",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "spreadsheet_id": {
                            "type": "string",
                            "description": "ID of the spreadsheet",
                        },
                        "range": {"type": "string", "description": "A1 notation range"},
                    },
                    "required": ["spreadsheet_id", "range"],
                },
            ),
            types.Tool(
                name="sheets_update_values",
                description="Update values in a Google Sheet range",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "spreadsheet_id": {
                            "type": "string",
                            "description": "ID of the spreadsheet",
                        },
                        "range": {"type": "string", "description": "A1 notation range"},
                        "values": {
                            "type": "array",
                            "items": {"type": "array", "items": {"type": "string"}},
                            "description": "2D array of values",
                        },
                    },
                    "required": ["spreadsheet_id", "range", "values"],
                },
            ),
        ]

    def register_tool_handler(self, name: str) -> Callable[[ToolHandler], ToolHandler]:
        """Decorator to register tool handlers."""

        def decorator(handler: ToolHandler) -> ToolHandler:
            logger.debug(f"Registering tool handler for {name}")
            self._tool_registry[name] = handler
            return handler

        return decorator

    async def _handle_drive_search_files(
        self, context: GoogleWorkspaceContext, arguments: dict
    ) -> Dict[str, Any]:
        """Handle drive search files requests."""
        query = arguments.get("query")
        page_size = arguments.get("page_size", 10)

        if not query:
            raise ValueError("Search query is required")

        logger.debug(f"Drive search request - Query: {query}, Page Size: {page_size}")
        result = await context.drive.search_files(query=query, page_size=page_size)
        logger.debug(f"Drive search completed - Found {len(result.get('files', []))} files")
        return result

    async def _handle_drive_create_folder(
        self, context: GoogleWorkspaceContext, arguments: dict
    ) -> Dict[str, Any]:
        """Handle drive create folder requests."""
        name = arguments.get("name")
        parent_id = arguments.get("parent_id")

        if not name:
            raise ValueError("Folder name is required")

        logger.debug(f"Creating folder - Name: {name}, Parent: {parent_id or 'root'}")
        result = await context.drive.create_folder(name=name, parent_id=parent_id)
        logger.debug(f"Folder created - ID: {result.get('id')}")
        return result

    async def _handle_docs_create(
        self, context: GoogleWorkspaceContext, arguments: dict
    ) -> Dict[str, Any]:
        """Handle docs create requests."""
        title = arguments.get("title")
        content = arguments.get("content")

        if not title:
            raise ValueError("Document title is required")

        logger.debug(
            f"Creating document - Title: {title}, " f"Content length: {len(content or '')}"
        )
        result = await context.docs.create_document(title=title, content=content)
        logger.debug(f"Document created - ID: {result.get('documentId')}")
        return result

    async def _handle_docs_get_content(
        self, context: GoogleWorkspaceContext, arguments: dict
    ) -> Dict[str, Any]:
        """Handle docs get content requests."""
        document_id = arguments.get("document_id")

        if not document_id:
            raise ValueError("Document ID is required")

        logger.debug(f"Getting document content - ID: {document_id}")
        result = await context.docs.get_document_content(document_id=document_id)
        logger.debug("Document content retrieved successfully")
        return result

    async def _handle_docs_update_content(
        self, context: GoogleWorkspaceContext, arguments: dict
    ) -> Dict[str, Any]:
        """Handle docs update content requests."""
        document_id = arguments.get("document_id")
        content = arguments.get("content")

        if not document_id or content is None:
            raise ValueError("Both document_id and content are required")

        logger.debug(f"Updating document - ID: {document_id}, " f"Content length: {len(content)}")
        result = await context.docs.update_document_content(
            document_id=document_id, content=content
        )
        logger.debug("Document content updated successfully")
        return result

    async def _handle_sheets_create(
        self, context: GoogleWorkspaceContext, arguments: dict
    ) -> Dict[str, Any]:
        """Handle sheets create requests."""
        title = arguments.get("title")
        sheets = arguments.get("sheets", [])

        if not title:
            raise ValueError("Spreadsheet title is required")

        logger.debug(f"Creating spreadsheet - Title: {title}, Sheets: {sheets}")
        result = await context.sheets.create_spreadsheet(title=title, sheets=sheets)
        logger.debug(f"Spreadsheet created - ID: {result.get('spreadsheetId')}")
        return result

    async def _handle_sheets_get_values(
        self, context: GoogleWorkspaceContext, arguments: dict
    ) -> Dict[str, Any]:
        """Handle sheets get values requests."""
        spreadsheet_id = arguments.get("spreadsheet_id")
        range_name = arguments.get("range")

        if not spreadsheet_id or not range_name:
            raise ValueError("Both spreadsheet_id and range are required")

        logger.debug(f"Getting sheet values - ID: {spreadsheet_id}, Range: {range_name}")
        result = await context.sheets.get_values(
            spreadsheet_id=spreadsheet_id, range_name=range_name
        )
        logger.debug(f"Sheet values retrieved - Row count: {len(result.get('values', []))}")
        return result

    async def _handle_sheets_update_values(
        self, context: GoogleWorkspaceContext, arguments: dict
    ) -> Dict[str, Any]:
        """Handle sheets update values requests."""
        spreadsheet_id = arguments.get("spreadsheet_id")
        range_name = arguments.get("range")
        values = arguments.get("values")

        if not spreadsheet_id or not range_name or values is None:
            raise ValueError("spreadsheet_id, range, and values are required")

        logger.debug(f"Updating sheet values - ID: {spreadsheet_id}, " f"Range: {range_name}")
        result = await context.sheets.update_values(
            spreadsheet_id=spreadsheet_id, range_name=range_name, values=values
        )
        logger.debug(f"Sheet values updated - Updated cells: {result.get('updatedCells', 0)}")
        return result

    def register_tools(self):
        """Register all available tools."""
        try:
            logger.debug("Registering tools")

            # Register tool handlers
            for tool in self._get_tools_list():
                handler_name = f"_handle_{tool.name}"
                if hasattr(self, handler_name):
                    self._tool_registry[tool.name] = getattr(self, handler_name)
                    logger.debug(f"Registered handler for {tool.name}")

            # Register server handlers
            @self.server.list_tools()
            async def handle_list_tools() -> list[types.Tool]:
                """List available tools."""
                logger.debug("Handling list_tools request")
                tools = self._get_tools_list()
                logger.debug(f"Returning {len(tools)} tools")
                return tools

            @self.server.call_tool()
            async def handle_call_tool(
                name: str, arguments: dict | None
            ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
                """Handle tool execution requests."""
                request_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                logger.info(f"Tool execution started - Request ID: {request_id}")
                logger.debug(f"Tool: {name}, Arguments: {arguments}")

                if not arguments:
                    logger.error(f"[{request_id}] Missing arguments for tool execution")
                    raise ValueError("Missing arguments")

                if not self._context:
                    logger.error(f"[{request_id}] Context missing")
                    raise McpError("Server context not initialized")

                is_authorized = await self._context.auth.is_authorized()
                if not is_authorized:
                    logger.error(f"[{request_id}] Authentication check failed")
                    raise McpError("Not authenticated. Please run 'mcp-google auth' first.")

                try:
                    handler = self._tool_registry.get(name)
                    if not handler:
                        logger.error(f"[{request_id}] Unknown tool requested: {name}")
                        raise ValueError(f"Unknown tool: {name}")

                    logger.debug(f"[{request_id}] Executing tool with context")
                    result = await handler(self._context, arguments)
                    logger.info(f"[{request_id}] Tool execution completed successfully")

                    # Log response summary
                    response = types.TextContent(type="text", text=json.dumps(result, indent=2))
                    logger.debug(f"[{request_id}] Response size: {len(response.text)} characters")

                    return [response]

                except Exception as e:
                    logger.error(f"[{request_id}] Error executing tool: {str(e)}", exc_info=True)
                    raise

            logger.debug("Tool registration complete")
        except Exception as e:
            logger.error(f"Error registering tools: {str(e)}", exc_info=True)
            raise

    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[GoogleWorkspaceContext]:
        """Manage Google Workspace services lifecycle."""
        logger.info("Starting server lifespan")
        try:
            # Initialize services
            logger.debug("Initializing Google services")
            auth = GoogleAuth(config=self.config)
            logger.debug("Auth service initialized")

            drive = DriveService(auth)
            logger.debug("Drive service initialized")

            docs = DocsService(auth)
            logger.debug("Docs service initialized")

            sheets = SheetsService(auth)
            logger.debug("Sheets service initialized")

            # Create context
            context = GoogleWorkspaceContext(auth=auth, drive=drive, docs=docs, sheets=sheets)

            # Store context for access in tools
            self._context = context
            logger.debug("Context created and stored")

            try:
                # Yield context
                logger.debug("Yielding context")
                yield context
                logger.debug("Context yielded successfully")
            finally:
                # Clear context when done
                logger.debug("Clearing context")
                self._context = None
        except Exception as e:
            logger.error(f"Error in lifespan: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("Server lifespan ending")

    async def run(self, read_stream, write_stream, init_options: InitializationOptions):
        """Run the MCP server."""
        logger.info("Starting server run")
        try:
            async with self.lifespan():
                # Start server with transport streams
                logger.debug("Starting server with transport streams")
                await self.server.run(read_stream, write_stream, init_options)
                logger.info("Server run completed")
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise

    def list_tools_table(self) -> str:
        """List available tools in a table format."""
        try:
            # Prepare tool information for display
            tool_info = []
            for name, _handler in self._tool_registry.items():
                tool_schema = next((t for t in self._get_tools_list() if t.name == name), None)
                if tool_schema:
                    tool_info.append([name, tool_schema.description])

            return tabulate(tool_info, headers=["Tool", "Description"], tablefmt="grid")
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return "Error listing tools"
