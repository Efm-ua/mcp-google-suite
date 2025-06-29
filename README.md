# MCP Google Suite Server

> **📋 Fork Information**  
> This is a forked repository from [adexltd/mcp-google-suite](https://github.com/adexltd/mcp-google-suite)  
> **Fork URL:** https://github.com/Efm-ua/mcp-google-suite  
> **Purpose:** Custom modifications and enhancements for DocGem project integration

A Model Context Protocol (MCP) server for Google Workspace integration.

## Description

This server provides MCP tools for interacting with Google Workspace applications including Gmail, Google Calendar, Google Drive, and more.

## Features

- Google Workspace OAuth authentication
- WebSocket and HTTP support for Cloud Run deployment
- Integration with Google APIs

## Usage

Run the server in WebSocket mode:
```
mcp-google-suite run --mode ws
```

## Environment Variables

- `OAUTH_CREDENTIALS_PATH`: Path to Google OAuth credentials file
- `HOST`: Server host (default: localhost)
- `PORT`: Server port (default: 8000)
- `SERVER_MODE`: Server mode (ws or stdio)

## License

MIT License
