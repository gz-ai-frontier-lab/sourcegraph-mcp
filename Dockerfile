# ====== Builder stage: resolve & compile everything (internet available) ======
FROM python:3.13-slim AS builder

WORKDIR /app

# Build tools for C/Rust extensions (pydantic-core, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        libc6-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

# Isolated venv — will be copied whole into the runtime image
RUN uv venv /app/.venv

# Copy project metadata + source, then install project AND all deps into the venv.
# Non-editable install: source files are copied into site-packages.
# This is the ONLY layer that touches the network (pypi.org).
COPY README.md pyproject.toml ./
COPY src/ ./src/
RUN uv pip install --python /app/.venv/bin/python .


# ====== Runtime stage: slim, no build tools, no uv, no internet needed ======
FROM python:3.13-slim

WORKDIR /app

# Copy the fully-built venv (deps + project, pre-compiled)
COPY --from=builder /app/.venv /app/.venv

# Exclusively use the venv's Python
ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

ENV MCP_SSE_PORT=8000
ENV MCP_STREAMABLE_HTTP_PORT=8080

EXPOSE ${MCP_SSE_PORT} ${MCP_STREAMABLE_HTTP_PORT}

# Run as a Python module.
#   • No `uv run`  → no project re-resolution → no pypi.org access at startup
#   • `python -m`  → __package__ is set so relative imports (from .server …) work
CMD ["python", "-m", "sourcegraph_mcp.main"]
