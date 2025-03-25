import mcp.server.stdio
from .server import GoogleWorkspaceMCPServer
from .config import Config
import logging

logger = logging.getLogger(__name__)

class StdioGoogleWorkspaceMCPServer(GoogleWorkspaceMCPServer):
    """STDIO implementation of the Google Workspace MCP server using native SDK transport."""
    
    def __init__(self, config: Config = None, config_path: str = None):
        super().__init__(config, config_path)
    
    def run_server(self):
        """Run the STDIO server."""
        logger.info("Starting STDIO MCP server")
        mcp.server.stdio.run(self.server)

def main():
    server = StdioGoogleWorkspaceMCPServer()
    server.run_server()

if __name__ == "__main__":
    main() 