FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/

# Install Python dependencies using uv
RUN uv pip install --no-cache .

# Create directory for logs
RUN mkdir -p /app/logs

# Create a non-root user
RUN useradd -m -u 1000 mcp
RUN chown -R mcp:mcp /app
USER mcp

# Expose the port for HTTP/WS servers
EXPOSE 8000

# Set default server mode to stdio
ENV SERVER_MODE=stdio

# Run the server using uv run
ENTRYPOINT ["uv", "run", "mcp-google-run"]
