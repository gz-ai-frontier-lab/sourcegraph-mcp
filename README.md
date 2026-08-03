# Sourcegraph MCP Server

A Model Context Protocol (MCP) server that provides AI-enhanced code search capabilities using [Sourcegraph](https://sourcegraph.com).

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Using UV (recommended)](#using-uv-recommended)
  - [Using pip](#using-pip)
  - [Using Docker](#using-docker)
- [Configuration](#configuration)
  - [Required Environment Variables](#required-environment-variables)
  - [Optional Environment Variables](#optional-environment-variables)
- [Usage with AI Tools](#usage-with-ai-tools)
  - [Cursor](#cursor)
- [MCP Tools](#mcp-tools)
  - [search](#search)
  - [search_prompt_guide](#search_prompt_guide)
  - [fetch_content](#fetch_content)
- [CI/CD](#cicd)
  - [Required Secrets](#required-secrets)
  - [Image Tags](#image-tags)
  - [Pulling the Image](#pulling-the-image)
- [Development](#development)
  - [Linting and Formatting](#linting-and-formatting)

## Overview

This MCP server integrates with Sourcegraph, a universal code search platform that enables searching across multiple repositories and codebases. It provides powerful search capabilities with advanced query syntax, making it ideal for AI assistants that need to find and understand code patterns across large codebases.

## Features

- **Code Search**: Search across codebases using Sourcegraph's powerful query language
- **Advanced Query Language**: Support for regex patterns, file filters, language filters, and boolean operators
- **Repository Discovery**: Find repositories by name and explore their structure
- **Content Fetching**: Browse repository files and directories
- **AI Integration**: Designed for LLM integration with guided search prompts

## Prerequisites

- **Sourcegraph Instance**: Access to a Sourcegraph instance (either sourcegraph.com or self-hosted)
- **Python 3.10+**: Required for running the MCP server
- **UV** (optional): Modern Python package manager for easier dependency management

## Installation

### Using UV (recommended)

```bash
# Install dependencies
uv sync

# Run the server
uv run python -m src.main
```

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .

# Run the server
python -m src.main
```

### Using Docker

```bash
# Build the image
docker build -t sourcegraph-mcp .

# Run the container with default ports
docker run -p 8000:8000 -p 8080:8080 \
  -e SRC_ENDPOINT=https://sourcegraph.com \
  -e SRC_ACCESS_TOKEN=your-token \
  sourcegraph-mcp

# Or run with custom ports
docker run -p 9000:9000 -p 9080:9080 \
  -e SRC_ENDPOINT=https://sourcegraph.com \
  -e SRC_ACCESS_TOKEN=your-token \
  -e MCP_SSE_PORT=9000 \
  -e MCP_STREAMABLE_HTTP_PORT=9080 \
  sourcegraph-mcp
```

## Configuration

### Required Environment Variables

- `SRC_ENDPOINT`: Sourcegraph instance URL (e.g., https://sourcegraph.com)

### Optional Environment Variables

- `SRC_ACCESS_TOKEN`: Authentication token for private Sourcegraph instances
- `MCP_SSE_PORT`: SSE server port (default: 8000)
- `MCP_STREAMABLE_HTTP_PORT`: HTTP server port (default: 8080)

## Usage with AI Tools

### Cursor

After running the MCP server, add the following to your `.cursor/mcp.json` file:

```json
{
  "mcpServers": {
    "sourcegraph": {
      "url": "http://localhost:8080/sourcegraph/mcp/"
    }
   }
}
```

## MCP Tools

This server provides three powerful tools for AI assistants:

### 🔍 search
Search across codebases using Sourcegraph's advanced query syntax with support for regex, language filters, and boolean operators.

### 📖 search_prompt_guide
Generate a context-aware guide for constructing effective search queries based on your specific objective.

### 📂 fetch_content
Retrieve file contents or explore directory structures from repositories.

## CI/CD

This repository ships a GitHub Actions workflow (`.github/workflows/docker-build.yml`) that automatically builds a multi-arch Docker image (linux/amd64 + linux/arm64) and pushes it to **Aliyun Container Registry (ACR)** on every push to `master`:

- **Aliyun ACR** — `crpi-maegwt5ukh5kiibp.cn-guangzhou.personal.cr.aliyuncs.com/gz-ai-frontier-lab/sourcegraph-mcp`

> Triggers on pushes to `master` (changes limited to `*.md`, `docs/`, `LICENSE`, `.gitignore` are skipped). Also supports manual triggering via `workflow_dispatch` from the Actions tab. Concurrent runs on the same branch are cancelled in favor of the newest run.

### Required Secrets

Aliyun ACR authentication requires **two organization-level secrets** configured at <https://github.com/organizations/gz-ai-frontier-lab/settings/secrets/actions>:

| Secret Name                    | Value                              | Source                                                              |
| ------------------------------ | ---------------------------------- | ------------------------------------------------------------------- |
| `ALIYUN_REGISTRY_USERNAME`     | `Midayang` (Aliyun account full name) | See "制品描述" in your ACR instance console                        |
| `ALIYUN_REGISTRY_PASSWORD`     | Registry access credential password | <https://cr.console.aliyun.com/cn-guangzhou/instances/credentials> |

Org-level secrets are automatically inherited by all repos under `gz-ai-frontier-lab`, so no per-repo configuration is needed.

### Image Tags

Each successful build publishes the following tags:

| Tag pattern      | Example             | Description                                  |
| ---------------- | ------------------- | -------------------------------------------- |
| `latest`         | `latest`            | Always points to the latest `master` build   |
| `master`         | `master`            | Branch name (useful for branch-based deploys)|
| `sha-<short>`    | `sha-0114408`       | The 7-character git commit short SHA         |

### Pulling the Image

```bash
# From Aliyun ACR
docker pull crpi-maegwt5ukh5kiibp.cn-guangzhou.personal.cr.aliyuncs.com/gz-ai-frontier-lab/sourcegraph-mcp:latest

# Pin to a specific commit
docker pull crpi-maegwt5ukh5kiibp.cn-guangzhou.personal.cr.aliyuncs.com/gz-ai-frontier-lab/sourcegraph-mcp:sha-0114408
```

Then run with the same flags documented in [Using Docker](#using-docker):


```bash
docker run -p 8000:8000 -p 8080:8080 \
  -e SRC_ENDPOINT=https://sourcegraph.com \
  -e SRC_ACCESS_TOKEN=your-token \
  crpi-maegwt5ukh5kiibp.cn-guangzhou.personal.cr.aliyuncs.com/gz-ai-frontier-lab/sourcegraph-mcp:latest
```

## Development

### Linting and Formatting

```bash
# Check code style
uv run ruff check src/

# Format code
uv run ruff format src/
```

