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
COPY README.md .
COPY src/ ./src/

# Install Python dependencies using uv
RUN uv pip install --system --no-cache .

# Create directory for logs
RUN mkdir -p /app/logs

# Create directory for secrets access (Cloud Run secrets need root access)
# Running as root is safe in Cloud Run sandboxed environment

# Expose the port for HTTP/WS servers
EXPOSE 8000

# Set default server mode to stdio
ENV SERVER_MODE=stdio

# Run the server using uv run
ENTRYPOINT ["mcp-google-suite", "run", "--mode", "ws"]
